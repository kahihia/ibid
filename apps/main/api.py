# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('django')
from datetime import datetime
import json
import time
from urllib2 import urlopen
from django.conf import settings
from django.conf.urls import url
from django.contrib.contenttypes.models import ContentType
from django_facebook.connect import connect_user
from django_facebook.exceptions import MissingPermissionsError
import open_facebook
from tastypie import fields
from tastypie import http
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.exceptions import Unauthorized, BadRequest, ImmediateHttpResponse
from tastypie.resources import ModelResource, ALL, Resource
from tastypie.utils import trailing_slash, dict_strip_unicode_keys
from apps.main.models import Notification
from apps.main.apiauth import *
from bidding import client
from bidding.models import Member, Auction, Item, ConvertHistory, BidPackage, ConfigKey, Bid, Category, Invitation, IOPaymentInfo
from chat import auctioneer
from chat.models import Message, ChatUser
from lib import metrics


#########################################
from django.utils.decorators import classonlymethod
from doc_utils import api_doc_view
#########################################

metrics.initialize(settings.MIXPANEL_TOKEN)

class IBGModelResource(ModelResource):
    def dispatch(self, *args, **kwargs):
        start = time.time()
        res = super(IBGModelResource, self).dispatch(*args, **kwargs)
        event = 'api_{api_name}_{resource_name}'.format(**kwargs)
        metrics.track_event('system', event, {'req_time': time.time() - start})
        return res

class NotificationResource(IBGModelResource):

    class Meta:
        resource_name = 'notification'
        list_allowed_methods = ['get', 'put']
        detail_allowed_methods = ['get', 'put']
        authorization = UserNotificationsAuthorization()
        queryset = Notification.objects.order_by('created')
        always_return_data = True
        include_resource_uri = False
        authentication = CustomAuthentication()
        filtering = {
            'status': ALL,
        }

    
    @classonlymethod
    @api_doc_view(['GET'])
    def get(self, request):
        """ Retrieves all of a users notifications """
        return super(NotificationResource,self).wrap_view('dispatch_list')
    
    @classonlymethod
    @api_doc_view(['PUT'])
    def put(self, request, pk=None):
        """ Updates a notification as read """
        return super(NotificationResource,self).wrap_view('dispatch_detail')
    

    def hydrate(self, bundle):
        bundle.obj = Notification.objects.get(id=bundle.data['pk'])
        bundle.obj.status = bundle.data['objects'][0]['message']['status']
        bundle.obj.updated = datetime.now()
        return bundle

class MemberResource(IBGModelResource):
    
    """ Resource to interact with member data objects.  """
    class Meta:
        queryset = Member.objects.all()
        resource_name = 'member'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authorization = MemberAuthorization()
        authentication = CustomAuthentication()
        include_resource_uri = False
    
    def base_urls(self):
        
        """ The standard URLs this ``Resource`` should respond to. """
        
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/(?P<%s>\d+)%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    

    @classonlymethod
    @api_doc_view(['GET'])
    def get(self, request):
        """ Retrieves all members.  """
        return super(MemberResource,self).wrap_view('dispatch_list')
    
    @classonlymethod
    @api_doc_view(['GET'])
    def retrieve(self, request, pk=None):
        """ Retrieves the member with 'pk' if it is the user  """
        return super(MemberResource,self).wrap_view('dispatch_detail')
    
    def dehydrate(self, bundle):
        
        """
        A hook to allow a final manipulation of data once all fields/methods
        have built out the dehydrated data.
        """
        
        bundle.data['display_name'] = "%s %s" % (bundle.obj.first_name, bundle.obj.last_name) 
        bundle.data['won_auctions'] = bundle.obj.auction_set.filter(winner=bundle.obj).all().count()
        bundle.data['actual_auctions'] = bundle.obj.auction_set.exclude(status='waiting_payment').exclude(status='paid').all().count()
        if bundle.obj.raw_data:
            bundle.data['image_thumb'] = json.loads(bundle.obj.raw_data)['image_thumb']
        return bundle
    
    def obj_get(self, bundle, **kwargs):
        return super(MemberResource, self).obj_get(bundle=bundle, **kwargs)
    
class ConverTokensResource(MemberResource):
    
    """ Resource to convert all of a member's tokens to credits """
    
    class Meta:
        resource_name = 'convertTokens'
        list_allowed_methods = []
        detail_allowed_methods = ['get']
        authorization = MemberAuthorization()
        queryset = Member.objects.all()
        authentication = CustomAuthentication()
        include_resource_uri = False
    
    def base_urls(self):
        return [
            url(r"^member/(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^member/(?P<resource_name>%s)/(?P<member_id>\d+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="convertTokens"),
        ]


    @classonlymethod
    @api_doc_view(['GET'])
    def get(self, request):
        """ Resource to convert all of a member's tokens to credits """
        return super(ConvertTokensResource,self).wrap_view('dispatch_detail')

    def obj_get(self, bundle, **kwargs):
        bundle.obj = Member.objects.get(id = kwargs['member_id'])
        self.authorized_read_detail('', bundle)
        amount = bundle.obj.maximun_bids_from_tokens()
        ConvertHistory.convert(bundle.obj, int(amount))
        bundle = self.save(bundle)
        return bundle.obj
    
class MemberByFBTokenResource(IBGModelResource):
    

    """ This resource logins or register a user using the facebook access token. """
    
    class Meta:
        resource_name = 'byFBToken'
        list_allowed_methods = []
        detail_allowed_methods = ['get']
        authorization = MemberAuthorization()
        queryset = Member.objects.all()
        detail_uri_name = 'access_token'
        include_resource_uri = False

    def base_urls(self):
        return [
            url(r"^member/(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^member/(?P<resource_name>%s)/(?P<%s>.*?)%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    @classonlymethod
    @api_doc_view(['GET'])
    def get(self, request):
        """ This resource logins or register a user using the facebook access token. """
        return super(MemberByFBTokenResource,self).wrap_view('dispatch_detail')

    def obj_get(self, bundle, **kwargs):
        
        """ Makes login or register the user with the access token from facebook. """

        access_token = kwargs['access_token']
        db_user = Member.objects.none()
        try:
            try:
                graph = self.check_permissions(access_token)
                of = open_facebook.OpenFacebook(access_token)
                facebook_user = of.get('me/',)
                action, db_user = connect_user(bundle.request, access_token)
            except Exception as e:
                raise ImmediateHttpResponse(response = self.error_response(bundle.request, str(e), http.HttpForbidden))
        except open_facebook.exceptions.OAuthException as e:
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, str(e), http.HttpForbidden))
        bundle.obj=db_user
        self.authorized_read_detail('', bundle)
        return db_user
    
    def dehydrate(self, bundle):
        """
        A hook to allow a final manipulation of data once all fields/methods
        have built out the dehydrated data.

        Useful if you need to access more than one dehydrated field or want
        to annotate on additional data.

        Must return the modified member.
        """
        bundle.data['display_name'] = "%s %s" % (bundle.obj.first_name, bundle.obj.last_name) 
        bundle.data['won_auctions'] = bundle.obj.auction_set.filter(winner=bundle.obj).all().count()
        bundle.data['actual_auctions'] = bundle.obj.auction_set.exclude(status='waiting_payment').exclude(status='paid').all().count()
        bundle.data['image_thumb'] = json.loads(bundle.obj.raw_data)['image_thumb']
        return bundle

    def check_permissions(self, access_token):
        """ check user permissions using django_facebook methods"""
        
        graph = open_facebook.OpenFacebook(access_token)
        permissions = set(graph.permissions())
        scope_list = set(settings.FACEBOOK_DEFAULT_SCOPE)
        missing_perms = scope_list - permissions
        if missing_perms:
            permissions_string = ', '.join(missing_perms)
            error_format = 'Permissions Missing: %s'
            raise MissingPermissionsError(error_format % permissions_string)
        return graph

class CategoryResource(IBGModelResource):
    """ Resource to retrive data of auction's items """    
    
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        collection_name = 'categories'
        authorization = ReadOnlyAuthorization()
        authentication = CustomAuthentication()
        include_resource_uri = False
        fields=['name', 'description','image']
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        
    @classonlymethod
    @api_doc_view(['GET'])
    def get(self, request):
        """ Retrives all categories available."""
        return super(MemberByFBTokenResource,self).wrap_view('dispatch_detail')
    
    @classonlymethod
    @api_doc_view(['GET'])
    def retrieve(self, request):
        """ Retrives one category. """
        return super(MemberByFBTokenResource,self).wrap_view('dispatch_detail')
    
    def dehydrate(self, bundle):
        try:
            bundle.data['categoryImage'] = bundle.obj.get_thumbnail(size="107x72")
        except Exception:
            pass
        return bundle

class ItemResource(IBGModelResource):
    """ Resource to retrive data of auction's items """    
    categories = fields.ManyToManyField(CategoryResource, 'categories',null=True ,full=True)

    class Meta:
        queryset = Item.objects.all()
        resource_name = 'item'
        collection_name = 'items'
        authorization = ReadOnlyAuthorization()
        authentication = CustomAuthentication()
        include_resource_uri = False
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

    @classonlymethod
    @api_doc_view(['GET'])
    def get(self, request):
        """ Retrives all items available."""
        return super(ItemResource,self).wrap_view('dispatch_detail')
    
    @classonlymethod
    @api_doc_view(['GET'])
    def retrieve(self, request):
        """ Retrives one item. """
        return super(ItemResource,self).wrap_view('dispatch_detail')

    def dehydrate(self, bundle):
        bundle.data['itemImage'] = bundle.obj.get_thumbnail(size="107x72")
        return bundle

class AuctionResource(IBGModelResource):
    """
    This resource retrieves auctions data filtered and sorted by status.
    """
    winner = fields.ForeignKey(MemberResource, 'winner',null=True, full=True, help_text = 'Member that won the auction.')
    item = fields.ForeignKey(ItemResource, 'item', full=True, help_text = 'Item being auctioned.')
    categories = fields.ManyToManyField(CategoryResource, 'categories', full=True, help_text ='Category of the auction')

    class Meta:
        queryset = Auction.objects.all()
        resource_name = 'auction'
        collection_name = 'auctions'
        detail_uri_name = 'id'
        authorization = ReadOnlyAuthorization()
        excludes = ['is_active']
        authentication = CustomAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
            'status' : ['exact'],
            'categories' : ['exact'],
        }
         
    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/set/(?P<%s_list>\w[\w/;-]*)%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('get_multiple'), name="api_get_multiple"),
            url(r"^(?P<resource_name>%s)/(?P<%s>\d+)%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            
        ]
    
    @classonlymethod
    @api_doc_view(['GET'])
    def get(self, request):
        """
        Retrives multiple auctions.
        status --  filter
        """
        return super(AuctionResource,self).wrap_view('dispatch_list')
    
    @classonlymethod
    @api_doc_view(['GET'])
    def retrieve(self, request):
        """ Retrieves one auction. """
        return super(AuctionResource,self).wrap_view('dispatch_detail')

    def get_list(self, request, **kwargs):
        
        """ Make object list in different ways depending if auction is finished or available"""
         
        filters = dict(request.GET.iterlists())
        get_list_method = self.default_get_list
        apply_sorting_method = self.apply_sorting
        if len(filters) > 0:
            if 'status' in filters and len(filters['status'])==1:
                if 'finished' in filters['status']:
                    get_list_method = self.finished_get_list
                    apply_sorting_method = self.finished_apply_sorting
                if 'available' in filters['status']:
                    get_list_method = self.available_get_list
                    apply_sorting_method = self.available_apply_sorting
                if 'playing' in filters['status']:
                    get_list_method = self.playing_get_list
        return self.common_get_list(request, get_list_method, apply_sorting_method, **kwargs)
    
    def common_get_list(self, request, get_list_method, apply_sorting_method, **kwargs):
        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        sorted_objects = apply_sorting_method(objects, request)
        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_uri(), limit=self._meta.limit, max_limit=self._meta.max_limit, collection_name=self._meta.collection_name)
        to_be_serialized = paginator.page()
        return_dict=get_list_method(request,to_be_serialized,**kwargs)
        to_be_serialized[self._meta.collection_name] = return_dict
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def default_get_list(self, request,to_be_serialized,**kwargs):
        token_finished_list=[]
        token_wout_winner=[]
        token_playing_list=[]
        token_available_list=[]
        credit_playing_list=[]
        credit_finished_list=[]
        credit_available_list=[]
        credit_wout_winner=[]
        finished_status = ['paid' ,'waiting_payment']
        playing_status=['processing','pause','waiting']
        return_dict={'token':{},'credit':{}}
        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            if obj.bid_type=='token' and obj.is_active ==True:
                if obj.status in finished_status:
                    if obj.winner:
                        token_finished_list.append(self.full_dehydrate_finished(request, bundle))
                    else:
                        token_wout_winner.append(self.full_dehydrate_finished(request, bundle))
                
                elif obj.status in playing_status:
                    token_playing_list.append(self.full_dehydrate_available(bundle))
                else:
                    token_available_list.append(self.full_dehydrate_available( bundle))
                    
            if obj.bid_type=='bid' and obj.is_active ==True:
                if obj.status in finished_status:
                    if obj.winner:
                        credit_finished_list.append(self.full_dehydrate_finished(request, bundle))
                    else:
                        credit_wout_winner.append(self.full_dehydrate_finished(request, bundle))
                
                elif obj.status in playing_status:
                    credit_playing_list.append(self.full_dehydrate_available( bundle))
                else:
                    credit_available_list.append(self.full_dehydrate_available( bundle)) 
        return_dict['token']['finished'] = token_finished_list
        return_dict['token']['available'] = token_available_list
        return_dict['token']['wout_winner'] = token_wout_winner
        return_dict['token']['playing'] = token_playing_list
        return_dict['credit']['finished'] = credit_finished_list
        return_dict['credit']['available'] = credit_available_list
        return_dict['credit']['wout_winner'] = credit_wout_winner
        return_dict['credit']['playing'] = credit_playing_list
        return return_dict
        
    def finished_get_list(self, request,to_be_serialized,**kwargs):
        finished_list=[]
        wout_winner=[]
        return_dict={}
        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            if obj.winner:
                finished_list.append(self.full_dehydrate_finished(request, bundle))
            else:
                wout_winner.append(self.full_dehydrate_finished(request, bundle))
        return_dict['finished'] = finished_list
        return_dict['wout_winner'] = wout_winner  
        return return_dict
    
    def available_get_list(self, request,to_be_serialized,**kwargs): 
        available_list=[]
        return_dict={}
        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            available_list.append(self.full_dehydrate_available( bundle))
        return_dict['available'] = available_list
        return return_dict
      
    def playing_get_list(self, request,to_be_serialized,**kwargs): 
        playing_list=[]
        return_dict={}
        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            playing_list.append(self.full_dehydrate_available( bundle))
        return_dict['playing'] = playing_list
        return return_dict
      
    def build_filters(self, filters=None):
        """
        Apply filters depending on the url that was used to access the resource.
        """
        ret_filters = {}
        ret_filters['is_active'] = True
        return ret_filters
    
    def apply_filters(self, request, applicable_filters):
        obj_list = self.get_object_list(request).filter(**applicable_filters)
        return_list = obj_list
        filters = dict(request.GET.iterlists())
        if len(filters) > 0:
            if 'status' in filters:
                status_list = obj_list.none()
                if 'finished' in filters['status']:
                    finished = ['waiting_payment', 'paid']
                    status_list = status_list | obj_list.filter(status__in=finished)
                if 'available' in filters['status']:
                    status_list = status_list | obj_list.filter(status = 'precap')
                if 'playing' in filters['status']:
                    playing = ['waiting', 'pause', 'processing']
                    status_list = status_list | obj_list.filter(status__in = playing)
                for search_status in filters['status'] :
                    if search_status not in ['finished', 'playing','available'] :
                        status_list = status_list | obj_list.filter(status = search_status)
                return_list = return_list & status_list
            filters_queryDict = request.GET.copy()
            if 'status' in filters_queryDict:
                filters_queryDict.pop('status')
            applicable_filters = super(AuctionResource, self).build_filters(filters_queryDict)
            return_list = return_list & obj_list.filter(**applicable_filters)
            return return_list
        return obj_list
    
    def available_apply_sorting(self, obj_list,request=None):
        return_list=[]
        for_token=obj_list.filter(bid_type='token').values('item__name','priority').order_by('-priority','item__name').distinct()
        for_credit=obj_list.filter(bid_type='bid').values('item__name','priority').order_by('-priority','item__name').distinct()
        
        #auctions that are for items on both lists
        [return_list.extend(Auction.objects.filter(status='precap').filter(item__name=x['item__name'],priority=x['priority']).order_by('-bid_type')) for x in for_token if x  in for_credit]
        #auctions that are for credit but not for tokens
        [return_list.extend(Auction.objects.filter(status='precap').filter(item__name=x['item__name'],priority=x['priority']).order_by('-bid_type')) for x in for_credit if x not in for_token]
        #autions tht are for tokens but no for credits
        [return_list.extend(Auction.objects.filter(status='precap').filter(item__name=x['item__name'],priority=x['priority']).order_by('-bid_type')) for x in for_token if x not in for_credit]
        
        return return_list
    
    def finished_apply_sorting(self, obj_list,request=None):
        return obj_list.order_by('-won_date')
    
    def full_dehydrate(self, bundle, for_list=False):
        return self.full_dehydrate_available(bundle)
    
    def full_dehydrate_available(self,bundle):
        
        """
        Dehydrate available auctions in two ways:
            1-for a member's auction
            2-for a general auction
        """
        bundle = super(AuctionResource, self).full_dehydrate(bundle)
        bundle.data['completion'] = bundle.obj.completion()
        bundle.data['bidders'] = bundle.obj.bidders.count()
        bundle.data['bid_amount'] = 0
        bundle.data['mine'] = bundle.obj.bidders.filter(id=bundle.request.user.id).exists()
        if bundle.data['mine']:
            bundle.data['placed'] = bundle.request.user.auction_bids_left(bundle.obj)
            bid = bundle.obj.bid_set.get(bidder=bundle.request.user)
            bundle.data['bid_amount'] = bid.left()
            bundle.data['timeleft'] = bundle.obj.get_time_left() if bundle.obj.status == 'processing' else None
            bundle.data['send_time'] = time.strftime("%d %b %Y %H:%M:%S +0000", time.gmtime()) if  bundle.obj.status == 'processing' else None
        bundle.data['bidNumber'] = bundle.obj.used_bids() / bundle.obj.minimum_precap
        bundle.data['auctioneerMessages'] = []
        for mm in Message.objects.filter(object_id=bundle.obj.id).filter(_user__isnull=True).order_by('-created')[:10]:
            w = {
                'text': mm.format_message(),
                'date': mm.get_time(),
                'auctionId': bundle.obj.id
            }
            bundle.data['auctioneerMessages'].append(w)
    
        bundle.data['chatMessages'] = []
        
        for mm in Message.objects.filter(object_id=bundle.obj.id).filter(_user__isnull=False).order_by('-created')[:10]:
            
            logger.debug('type ----->%s' % type(mm.get_user().content_object))
            w = {'text': mm.format_message(),
                 'date': mm.get_time(),
                 'user': {'displayName': mm.get_user().display_name(),
                          'profileFotoLink': mm.get_user().picture(),
                          'profileLink': mm.user.user_link(),
                          'facebookId': mm.get_user().user_facebook_id()
                          },
                 'auctionId': bundle.obj.id
            }
            bundle.data['chatMessages'].insert(0, w)
          
        return bundle
    
    def full_dehydrate_finished(self, request, bundle):
        """ Dehydrate a finished auction """
        bundle = super(AuctionResource, self).full_dehydrate(bundle)
        bundle.data['bidNumber'] = bundle.obj.used_bids() / bundle.obj.minimum_precap
        bundle.data['placed'] = 0
        bundle.data['auctioneerMessages'] = []
        bundle.data['chatMessages'] = []
        if bundle.obj.won_date:
            format = '%d-%m-%Y' # Or whatever your date format is
            bundle.data['won_date']=bundle.obj.won_date.strftime('%d/%m/%Y')
        else:
            bundle.data['won_date']=None
        return bundle
    
class MemberAuctionsResource(AuctionResource):
    
    """ Resource to retrieve data of auctions from some user """
    
    class Meta:
        queryset = Auction.objects.all()
        resource_name = 'my_auction'
        collection_name = 'auctions'
        authorization = ReadOnlyAuthorization()
        excludes = ['is_active']
        include_resource_uri = False   
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        authentication = CustomAuthentication()
        
    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
                url(r"^member/(?P<resource_name>%s)%s$" % (self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
                url(r"^member/(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
                ]

    @classonlymethod
    @api_doc_view(['GET'])
    def get(self, request):
        """
        Resource to retrieve data of auctions from the user
        """
        return super(MemberAuctionsResource,self).wrap_view('dispatch_list')

    def apply_filters(self, request, applicable_filters):
        obj_list = self.get_object_list(request).filter(bidders = request.user.id)
        return_list = obj_list & super(MemberAuctionsResource, self).apply_filters(request, applicable_filters)
        filters = dict(request.GET.iterlists())
        if len(filters) > 0:
            if 'status' in filters:
                if 'won' in filters['status']:
                    finished = ['waiting_payment', 'paid']
                    won_list = obj_list.filter(status__in=finished, winner__id = request.user.id)
                    return_list = return_list | won_list
        return return_list
    
    def apply_sorting(self, obj_list, options=None):
        return_list = []
        playing = ['waiting', 'processing', 'pause']
        finished = ['waiting_payment', 'paid']
        return_list.extend(obj_list.filter(status__in=playing))
        return_list.extend(obj_list.filter(status='precap'))
        return_list.extend(obj_list.filter(status__in=finished))
        return return_list
    
    def get_list(self, request, **kwargs):
        return super(AuctionResource, self).get_list(request, **kwargs)

class BidPackageResource(IBGModelResource):
    
    """ Resource to retrieve data of bid package objects """
    
    class Meta:
        queryset = BidPackage.objects.all()
        resource_name = 'bid_package'
        authorization = ReadOnlyAuthorization()
        authentication = CustomAuthentication()
        include_resource_uri = False
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']

    @classonlymethod
    @api_doc_view(['GET'])
    def get(self, request):
        """ Retrieves data of all bid package objects """
        return super(BidPackageResource,self).wrap_view('dispatch_list')
    
    @classonlymethod
    @api_doc_view(['GET'])
    def retrieve(self, request):
        """ Retrieves data of one bid package object """
        return super(BidPackageResource,self).wrap_view('dispatch_detail')

class AddBidResource(AuctionResource):
     
    """
        Let a user to add bids into an auction
    """
    
    class Meta:
        resource_name = 'add_bids'
        authorization = Authorization()
        authentication = CustomAuthentication()
        queryset = Auction.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ['post']
        include_resource_uri = False
           
    def base_urls(self):
        return [
            url(r"^auction/(?P<auction_id>\d+)/(?P<resource_name>%s)%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
    @classonlymethod
    @api_doc_view(['POST'])
    def post(self, request):
        """ The user add bids to an auction. """
        return super(AddBidResource,self).wrap_view('dispatch_detail')

    def post_detail(self, request, **kwargs):
        return super(AddBidResource, self).get_detail(request, **kwargs)
    
    def obj_get(self, bundle, **kwargs):
        error = None
        can_place = False
        auction = Auction.objects.select_for_update().filter(id=kwargs['auction_id'])[0]
        bundle.obj = auction

        # check if authorized
        self.authorized_read_detail('', bundle)
        
        member = bundle.request.user
        try:
            amount = auction.minimum_precap
        except ValueError:
            error = "not int"
        can_place = auction.can_precap(member, amount)
        if not auction.bidders.filter(id=member.id).exists():
            joining = False
            if auction.status == 'precap' and can_place:
                joining = auction.place_precap_bid(member, amount)
            if joining:
                metrics.join_auction(member, auction)
                clientMessages = []
                clientMessages.append(client.updatePrecapMessage(auction))
                clientMessages.append(auctioneer.member_joined_message(auction, member))
                client.sendPackedMessages(clientMessages)
        else: 
            amount += member.auction_bids_left(auction)
            if auction.status == 'precap' and can_place:
                 #check max tokens for member per auction
                if auction.bid_type != 'bid' and (((amount*100)/(auction.precap_bids)) > ConfigKey.get('AUCTION_MAX_TOKENS', 100)):
                    error = 'AUCTION_MAX_TOKENS_REACHED'
                else:
                    auction.place_precap_bid(member, amount)
                    client.updatePrecap(auction)
        if not can_place:
            if auction.status != "precap":
                error = "NOT_IN_PRECAP"
            else:
                if auction.bid_type == 'bid':
                    error = 'NO_ENOUGH_CREDITS'
                elif auction.bid_type == 'token':
                    error = 'NO_ENOUGH_TOKENS'
        if error:
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, error, http.HttpForbidden))
        return bundle.obj
    
class RemBidResource(AuctionResource):
     
    """
        Let a user to remove bids into an auction
    """
    
    class Meta:
        resource_name = 'rem_bids'
        authorization = Authorization()
        authentication = CustomAuthentication()
        queryset = Auction.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ['post']
        include_resource_uri = False
           
    def base_urls(self):
        return [
            url(r"^auction/(?P<auction_id>\d+)/(?P<resource_name>%s)%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="remBid"),
        ]  

    def post_detail(self, request, **kwargs):
        return super(RemBidResource, self).get_detail(request, **kwargs)
    
    @classonlymethod
    @api_doc_view(['POST'])
    def post(self, request):
        """ The user remove bids to an auction. """
        return super(RemBidResource,self).wrap_view('dispatch_detail')

    def obj_get(self, bundle, **kwargs):
          
        error = None
        try:
            auction = Auction.objects.select_for_update().filter(id=kwargs['auction_id'])[0]
            bundle.obj = auction
        except ValueError:
            error = "auction not found"
        
     
        # check if authorized
        self.authorized_read_detail('', bundle)
        
        member = bundle.request.user
        try:
            amount = auction.minimum_precap
        except ValueError:
            error = "not int"
        
        amount = member.auction_bids_left(auction) - amount
        if auction.can_precap(member, amount):
            auction.place_precap_bid(member, amount, False)
            client.updatePrecap(auction)
        if member.auction_bids_left(auction) <= 0:
            auction.leave_auction(member)
            clientMessages = []
            clientMessages.append(client.updatePrecapMessage(auction))
            clientMessages.append(auctioneer.member_left_message(auction, member))
            client.sendPackedMessages(clientMessages)
        if error:
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, error, http.HttpForbidden))    
        return bundle.obj

class ClaimBidResource(AuctionResource):

    """
        Let a user to calim bids into an auction
    """
    
    class Meta:
        resource_name = 'claim'
        authorization = Authorization()
        authentication = CustomAuthentication()
        queryset = Auction.objects.all()
        always_return_data = True
        list_allowed_methods = []
        detail_allowed_methods = ['post']
        include_resource_uri = False
        detail_uri_name = 'auction_id'
        
    def prepend_urls(self):
        return [
            url(r"^auction/(?P<auction_id>\d+)/(?P<resource_name>%s)%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),  
        ]  

    def post_detail(self, request, **kwargs):
        return super(ClaimBidResource, self).get_detail(request, **kwargs)

    @classonlymethod
    @api_doc_view(['POST'])
    def post(self, request):
        "" " The user claims an auction. """
        return super(ClaimBidResource,self).wrap_view('dispatch_detail')
    
    def obj_get(self,bundle, **kwargs ):
        
        error = None
        auction = Auction.objects.select_for_update().filter(id=kwargs['auction_id'])[0]
        bundle.obj = auction
        
        # check if authorized
        self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        
        member = bundle.request.user
        try:
            amount = auction.minimum_precap
        except ValueError:
            error = "not int"
        try:
            bidNumber = int(json.loads(bundle.request.body)['bidNumber'])
        except Exception:
            error = 'BIDNUMBER_MISSING'
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, error, http.HttpBadRequest))
        if auction.status == 'processing' and auction.can_bid(member):
            if bidNumber == auction.getBidNumber():
                if auction.bid(member, bidNumber):
                    clientMessages = []
                    clientMessages.append(client.someoneClaimedMessage(auction))
                    clientMessages.append(auctioneer.member_claim_message(auction, member))
                    client.sendPackedMessages(clientMessages)
                else:
                    #else ignore! because the claim is old, based on a previous timer.
                    error = 'OLD_CLAIM'
                    
            else:
                #else ignore! because the claim is old, based on a previous timer.
                error = 'OLD_CLAIM'
        else:
            error = 'AUCTION_NOT_ACTIVE_OR_CANT_BID'
        if error:
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, error, http.HttpForbidden))

        return bundle.obj


class MessageResource(ModelResource):
    
    """
    Creates a new message for an auction.
    """
    class Meta:
        resource_name = 'messages'
        authorization = Authorization()
        authentication = CustomAuthentication()
        queryset = Message.objects.all()
        collection_name = 'messages'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = []
        include_resource_uri = False
        filtering = {
            'object_id' : ['exact'],
        }

    def base_urls(self):
        return [
            url(r"^auction/(?P<object_id>\d+)/(?P<resource_name>%s)%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
        ]   
        
    @classonlymethod
    @api_doc_view(['POST', 'GET'])
    def post(self, request):
        """
        Message handler.
        
        Body: {"text":String}
        """
        return super(MessageResource,self).wrap_view('dispatch_list')
    
    def post_list(self, request, **kwargs):
        deserialized = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        basic_bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        if 'text' in basic_bundle.data:
            text = basic_bundle.data['text']
            auction_id = kwargs['object_id']
            auction = Auction.objects.get(id=auction_id)
            user_type_id=ContentType.objects.filter(name='user').all()[0]
            auction_type_id=ContentType.objects.filter(name='auction').all()[0]
            user = ChatUser.objects.get_or_create(object_id=request.user.id, content_type=user_type_id)[0]
            bundle = self.obj_create(bundle=basic_bundle, text=text, user=user, content_type=auction_type_id, object_id=auction.id)
            client.do_send_chat_message(auction, bundle.obj)
            return self.create_response(request, {} , response_class=http.HttpCreated)
        return self.create_response(request, {} , response_class=http.HttpBadRequest)

    def apply_sorting(self, obj_list, options=None):
        obj_list = obj_list.order_by('-created')
        return obj_list
    
class RegisterInvitationResource(IBGModelResource):
    """
        Register an invitation for each facebook id in the post
    """
    class Meta:
        resource_name = 'registerInvitation'
        authorization = Authorization()
        list_allowed_methods = ['post']
        detail_allowed_methods = []
        include_resource_uri = False
        
    def base_urls(self):
        return[
            url(r"^member/(?P<resource_name>%s)%s$" %(self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
        ]
    
    @classonlymethod
    @api_doc_view(['POST'])
    def post(self, request):
        """
        Payment from apple store handler.
        
        Body:{"invited":"[facebook_id,]")}
        """
        return super(IOPaymentInfoResource,self).wrap_view('dispatch_list')
    
    def post_list(self, request, **kwargs):
        member = request.user
        requPOST = json.loads(request.body)
        try:
            invited = request.GET.get('invited', requPOST['invited'])
            for fb_id in invited:
                #if already users or already invited: pass
                fb_id = int(fb_id)
                if len(Member.objects.filter(facebook_id=fb_id)) or len(Invitation.objects.filter(invited_facebook_id=fb_id)):
                    pass
                #else: add to invited
                else:
                    inv = Invitation()
                    inv.inviter_id = member.id
                    inv.invited_facebook_id = fb_id
                    inv.save()
            return self.create_response(request, {}, response_class=http.HttpCreated)
        except Exception:
            return self.create_response(request, {} , response_class=http.HttpBadRequest)
    
class ServerClockResource(Resource):
    class Meta:
        resource_name = "clock"
        list_allowed_methods = ['get']
        authorization = Authorization()
        
    def base_urls(self):
        return[
            url(r"^(?P<resource_name>%s)%s$" %(self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
        ]
    
    def get_list(self, request, **kwargs):
        client.clock_pubnub()
        return self.create_response(request, time.strftime("%d %b %Y %H:%M:%S +0000", time.gmtime()))

  
class IOPaymentInfoResource(ModelResource):
    
    """
    Creates a new payment for a purchase via apple store
    """
    
    class Meta:
        resource_name = 'io_purchase'

        authorization = Authorization()
        #authorization = PaymentAuthorization()
        #authentication = CustomAuthentication()

        queryset = IOPaymentInfo.objects.all()
        collection_name = 'payments'
        list_allowed_methods = ['post']
        detail_allowed_methods = []
        include_resource_uri = False

    @classonlymethod
    @api_doc_view(['POST'])
    def post(self, request):
        """
        Payment from apple store handler.
        
        Body   :   {"receipt-data":string(64-bit coded data)}
        """
        return super(IOPaymentInfoResource,self).wrap_view('dispatch_list')
    
    def post_list(self, request, **kwargs):
        error = None
        logger.debug('REQUEST.BODY: %s' % request.body)
        deserialized = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        basic_bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        if 'receipt-data' in basic_bundle.data:
            #bundle.data = urlopen('https://buy.itunes.apple.com/verifyReceipt', bundle.data).read()
            post = urlopen('https://sandbox.itunes.apple.com/verifyReceipt', request.body).read()
            logger.debug('post response:%s'%post)
            verified_data = json.loads(post)
            if 'status' in verified_data:
                if verified_data['status'] == 0:
                    for receipt in verified_data['receipt']['in_app']:
                        try:
                            IOPaymentInfo.objects.get(transaction_id=receipt['transaction_id'])
                            error = 'DUPLICATED PURCHASE'
                        except Exception:
                            store_ids = ConfigKey.get('APPLE_STORE_PACKAGES')
                            if store_ids:
                                try:
                                    store_ids = json.loads(store_ids)
                                    package = BidPackage.objects.get(pk=store_ids[receipt['product_id']])
                                    logger.debug(str(receipt['purchase_date']))
                                    bundle = self.obj_create(
                                        bundle = basic_bundle, 
                                        member = request.user,
                                        package = package,
                                        transaction_id = int(receipt['transaction_id']), 
                                        purchase_date = datetime.strptime(str(receipt['purchase_date']), '%Y-%m-%d %H:%M:%S Etc/GMT'),
                                        quantity = int(receipt['quantity'])
                                        )
                                    request.user.bids_left += (package.bids * int(receipt['quantity']))
                                    request.user.save()
                                    client.update_credits(request.user)
                                    return self.create_response(request, {} , response_class=http.HttpCreated)
                                except Exception:
                                    error = 'ERROR IN THE PURCHASE' 
                            else:
                                error = 'INVALID PACKAGE'
                else:
                    error = 'INVALID RECEIPT : %s' % verified_data['status']
        else:
            error = 'KEY MISSING : receipt-data'
        return self.create_response(request, {'error':error} , response_class=http.HttpBadRequest)

class AppleIbidPackageIdsResource(IBGModelResource):
    
    """ Resource to retrieve data of bid package objects """
    
    class Meta:
        queryset = ConfigKey.objects.filter(key='APPLE_STORE_PACKAGES')
        resource_name = 'apple_ibid_packages'
        authorization = ReadOnlyAuthorization()
        #authentication = CustomAuthentication()
        include_resource_uri = False
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        fields = ('value',)
        
    @classonlymethod
    @api_doc_view(['GET'])
    def get(self, request):
        """ Resource to retrieve data of bid package objects' relation with apple store """
        return super(AppleIbidPackageIdsResource,self).wrap_view('dispatch_list')

    