from tastypie.authorization import Authorization,ReadOnlyAuthorization
from tastypie.authentication import Authentication
from tastypie.exceptions import Unauthorized, BadRequest, ImmediateHttpResponse
from tastypie import http
from tastypie.resources import ModelResource, ALL,Resource
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash, dict_strip_unicode_keys
from tastypie.authentication import SessionAuthentication
from apps.main.models import Notification
from bidding.models import Member, Auction, Item, ConvertHistory, BidPackage, ConfigKey, Bid,Category

from chat.models import Message, ChatUser

from django_facebook.connect import connect_user
from django_facebook.exceptions import MissingPermissionsError
import open_facebook

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.conf.urls import url
from datetime import datetime
import json
from tastypie import fields
import logging
from bidding import client
from chat import auctioneer
log= logging.getLogger('django')
from datetime import datetime

class CustomAuthentication(Authentication):
    
    def is_authenticated(self, request, **kwargs):
        return request.user.is_authenticated()
          
    # Optional but recommended
    def get_identifier(self, request):
        return request.user
    
#################### AUTHORIZATION METHODS TO ENABLE OR DISABLE DATA ACCES FOR A USER

class NoAuthorization(Authorization):
    
    """
    Is used as a super class to negate most of the hits
    """

    def read_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no lists.")
    def read_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no detail.")
    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")
    def create_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")
    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")
    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")
    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")
    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

class UserNotificationsAuthorization(ReadOnlyAuthorization):
 
    """
    This class is used to control the access to notifications
    """
    def read_list(self, object_list, bundle):
        
        """
        Checks a configKey to know if the retrieval of notifications
        is enabled
        """
        
        if ConfigKey.get('NOTIFICATIONS_ENABLED', False):
            return object_list.filter(recipient=bundle.request.user, status='Unread')
        raise Unauthorized("Notifications disabled")
    
    def read_detail(self, object_list, bundle):
        if bundle.request.path.endswith('schema/'):
            return True
        return bundle.obj.recipient == bundle.request.user
        
    
    def update_detail(self, object_list, bundle):
        return bundle.obj.recipient == bundle.request.user
    
class MemberAuthorization(NoAuthorization):
    
    def read_detail(self, object_list, bundle):
        if bundle.request.path.endswith('schema/'):
            return True
        return bundle.request.user == bundle.obj
    
    def update_detail(self, object_list, bundle):
        return bundle.request.user == bundle.obj

class SendMessageAuthorization(NoAuthorization):
    
    def read_detail(self, object_list, bundle):
        if bundle.request.path.endswith('schema/'):
            return True
        return False
    
    def create_detail(self, object_list, bundle):
        try:
            auction_id = int(bundle.data['auction_id'])
            if bundle.request.user.can_chat(auction_id):
                return True
        except:    
            return False

#############################RESOURCES############################################################

def common_get_list(resource,request,method,**kwargs):
    
    base_bundle = resource.build_bundle(request=request)
    objects = resource.obj_get_list(bundle=base_bundle, **resource.remove_api_resource_names(kwargs))
    log.debug('resource  '+str(resource))
    log.debug('objects  '+str(objects))
    sorted_objects = resource.apply_sorting(objects,request)
    
  
    
    paginator = resource._meta.paginator_class(request.GET, sorted_objects, resource_uri=resource.get_resource_uri(), limit=resource._meta.limit, max_limit=resource._meta.max_limit, collection_name=resource._meta.collection_name)
    to_be_serialized = paginator.page()
    
    return_dict=method(request,to_be_serialized,**kwargs)
    
    to_be_serialized[resource._meta.collection_name] = return_dict
    to_be_serialized = resource.alter_list_data_to_serialize(request, to_be_serialized)
    return resource.create_response(request, to_be_serialized)

class NotificationResource(ModelResource):
    
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
        
    def hydrate(self, bundle):
        bundle.obj = Notification.objects.get(id=bundle.data['pk'])
        bundle.obj.status = bundle.data['objects'][0]['message']['status']
        bundle.obj.updated = datetime.now()
        return bundle

class MemberResource(ModelResource):
    
    """  Resource to interact with member data objects. """
    
    class Meta:
        queryset = Member.objects.all()
        resource_name = 'member'
        list_allowed_methods = []
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
    
    def obj_update(self, bundle, **kwargs):
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

    def obj_get(self, bundle, **kwargs):
        bundle.obj = Member.objects.get(id = kwargs['member_id'])
        self.authorized_read_detail('', bundle)
        amount = bundle.obj.maximun_bids_from_tokens()
        ConvertHistory.convert(bundle.obj, int(amount))
        bundle = self.save(bundle)
        return bundle.obj
    
class MemberByFBTokenResource(MemberResource):
    
    """ This resource loggins or register a user using the facebook access token. """
    
    class Meta:
        resource_name = 'byFBToken'
        list_allowed_methods = []
        detail_allowed_methods = ['get']
        authorization = MemberAuthorization()
        queryset = Member.objects.all()
        detail_uri_name = 'access_token'
        include_resource_uri = False
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<%s>.*?)%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
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
                raise ImmediateHttpResponse(response = self.error_response(bundle.request, str(e), http.HttpApplicationError))
        except open_facebook.exceptions.OAuthException as e:
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, str(e), http.HttpApplicationError))
        bundle.obj=db_user
        self.authorized_read_detail('', bundle)
        return db_user

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

class CategoryResource(ModelResource):

    """ Resource to retrive data of auction's items """    
    
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        authorization = ReadOnlyAuthorization()
        authentication = SessionAuthentication()
        include_resource_uri = False
        fields=['name', 'description','image']

    def dehydrate(self, bundle):
        bundle.data['categoryImage'] = bundle.obj.get_thumbnail(size="107x72")
        return bundle

class ItemResource(ModelResource):

    """ Resource to retrive data of auction's items """    
    categories = fields.ManyToManyField(CategoryResource, 'categories',null=True ,full=True)
    
    class Meta:
        queryset = Item.objects.all()
        resource_name = 'item'
        authorization = ReadOnlyAuthorization()
        authentication = SessionAuthentication()
        include_resource_uri = False

    def dehydrate(self, bundle):
        bundle.data['itemImage'] = bundle.obj.get_thumbnail(size="107x72")
        return bundle

class AuctionResource(ModelResource):
    """
    This resource retrieves auctions data in different ways:
        1- All auctions sorted by credits  (avaiable and finished) and tokens (avaiable and finished)
        2- Auctions that the user with id = "member_id" (sent in url) is in, sorted by credits (avaiable and finished) and tokens (avaiable and finished)
        3- Auctions that were won by the user with the "winner_id" (sent in the url)
    """
    winner = fields.ForeignKey(MemberResource, 'winner',null=True, full=True, help_text = 'Member that won the auction.')
    item = fields.ForeignKey(ItemResource, 'item', full=True, help_text = 'Item being auctioned.')
    
    class Meta:
        queryset = Auction.objects.all()
        resource_name = 'auction'
        collection_name = 'auctions'
        authorization = ReadOnlyAuthorization()
        excludes = ['is_active']
        authentication = SessionAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        filtering = {
            'status' : ['in'],
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
    
    def obj_update(self, bundle, **kwargs):
        return super(AuctionResource, self).obj_get(bundle=bundle, **kwargs)
    
    def custom_get_list(self, request,to_be_serialized,**kwargs):
        
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
                    token_playing_list.append(self.full_dehydrate_available(request, bundle))
                else:
                    token_available_list.append(self.full_dehydrate_available(request, bundle))
                    
            if obj.bid_type=='bid' and obj.is_active ==True:
                if obj.status in finished_status:
                    if obj.winner:
                        credit_finished_list.append(self.full_dehydrate_finished(request, bundle))
                    else:
                        credit_wout_winner.append(self.full_dehydrate_finished(request, bundle))
                
                elif obj.status in playing_status:
                    credit_playing_list.append(self.full_dehydrate_available(request, bundle))
                else:
                    credit_available_list.append(self.full_dehydrate_available(request, bundle)) 
            
        return_dict['token']['finished'] = token_finished_list
        return_dict['token']['available'] = token_available_list
        return_dict['token']['wout_winner'] = token_wout_winner
        return_dict['token']['playing'] = token_playing_list
        return_dict['credit']['finished'] = credit_finished_list
        return_dict['credit']['available'] = credit_available_list
        return_dict['credit']['wout_winner'] = credit_wout_winner
        return_dict['credit']['playing'] = credit_playing_list
        return return_dict
        
    def get_list(self, request, **kwargs):
        return common_get_list(self, request,self.custom_get_list,**kwargs)         
        
    def build_filters(self, filters=None):
        
        """
        Apply filters depending on the url that was used to access the resource.
        """
        ret_filters = super(AuctionResource, self).build_filters(filters)
        ret_filters['is_active'] = True
        return ret_filters
    #
    def apply_sorting(self, obj_list,request=None):
        return super(AuctionResource,self).apply_sorting(obj_list,options=request.GET)
        
    
    def full_dehydrate_available(self, request, bundle):
        
        """
        Dehydrate available auctions in two ways:
            1-for a member's auction
            2-for a general auction
        """
        
        bundle = super(AuctionResource, self).full_dehydrate(bundle)
        bundle.data['completion'] = bundle.obj.completion()
        bundle.data['bidders'] = bundle.obj.bidders.count()
        bundle.data['bid_amount'] = 0
        bundle.data['mine'] = bundle.obj.bidders.filter(id=request.user.id).exists()
        if bundle.data['mine']:
            bundle.data['placed'] = request.user.auction_bids_left(bundle.obj)
            bid = bundle.obj.bid_set.get(bidder=request.user)
            bundle.data['bid_amount'] = bid.left()
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
            w = {'text': mm.format_message(),
                 'date': mm.get_time(),
                 'user': {'displayName': mm.get_user().display_name(),
                          'profileFotoLink': mm.get_user().picture(),
                          'profileLink': mm.user.user_link()},
                 'auctionId': bundle.obj.id
            }
            bundle.data['chatMessages'].insert(0, w)
          
        return bundle
    
    def full_dehydrate_finished(self, request, bundle):
        
        """ Dehydrate a finished auction """
        
        bundle = super(AuctionResource, self).full_dehydrate(bundle)
        bundle.data['bidNumber'] = bundle.obj.used_bids() / bundle.obj.minimum_precap
        bundle.data['placed']= 0
        bundle.data['auctioneerMessages'] = []
        bundle.data['chatMessages'] = []
        if bundle.obj.won_date:
            format = '%d-%m-%Y' # Or whatever your date format is
            bundle.data['won_date']=bundle.obj.won_date.strftime('%d/%m/%Y')
        else:
            bundle.data['won_date']=None
        return bundle

class AuctionAvailableResource(AuctionResource):

    class Meta:
        queryset = Auction.objects.all()
        resource_name = 'available'
        authorization = ReadOnlyAuthorization()
        include_resource_uri = False   
        excludes = ['is_active']
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        authentication = CustomAuthentication()
    
    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
                url(r"^auction/(?P<resource_name>%s)%s$" % (self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
                url(r"^auction/(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
                ]
    
    def custom_get_list(self, request,to_be_serialized,**kwargs):
        # Dehydrate the bundles in preparation for serialization.
        """ Make dehydrate in different ways depending if auction is finished or available"""           
        available_list=[]
        return_dict={}
        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            available_list.append(self.full_dehydrate_available(request, bundle))
        return_dict['available'] = available_list
        return return_dict
    
    def build_filters(self, filters=None):
        
        """
        Apply filters depending on the url that was used to access the resource.
        """
        ret_filters = super(AuctionAvailableResource, self).build_filters(filters)
        ret_filters['status__in'] = ['precap']
        return ret_filters
    
    def apply_sorting(self, obj_list,request=None):
        
       
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

class AuctionFinishedResource(AuctionResource):

    class Meta:
        queryset = Auction.objects.all()
        resource_name = 'finished'
        authorization = ReadOnlyAuthorization()
        include_resource_uri = False   
        excludes = ['is_active']
        authentication = CustomAuthentication()
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        
    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
                url(r"^auction/(?P<resource_name>%s)%s$" % (self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
                url(r"^auction/(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
                ]
    
    def custom_get_list(self, request,to_be_serialized,**kwargs):
        
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
    
    def build_filters(self, filters=None):
        """
        Apply filters depending on the url that was used to access the resource.
        """
        ret_filters = super(AuctionFinishedResource, self).build_filters(filters)
        ret_filters['status__in'] = ['paid' ,'waiting_payment']
        return ret_filters
    
    def apply_sorting(self, obj_list,request=None):
        return obj_list.order_by('won_date')
            
class AuctionsWonByUserResource(AuctionFinishedResource):
    
    class Meta:
        queryset = Auction.objects.all()
        resource_name = 'wonByUser'
        authorization = ReadOnlyAuthorization()
        include_resource_uri = False   
        excludes = ['is_active']
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        authentication = CustomAuthentication()
        
    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
                url(r"^auction/(?P<resource_name>%s)%s$" % (self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
                url(r"^auction/(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
                ]
    
    def apply_filters(self, request, applicable_filters):
        obj_list = self.get_object_list(request).filter(**applicable_filters)
        return obj_list.filter(winner__id = request.user.id)
            
class AuctionByCategoryResource(AuctionAvailableResource):
    
    class Meta:
        queryset = Auction.objects.all()
        resource_name = 'byCategory'
        authorization = ReadOnlyAuthorization()
        include_resource_uri = False   
        excludes = ['is_active']
        list_allowed_methods = ['get']
        detail_allowed_methods = []
        authentication = CustomAuthentication()
        
    def base_urls(self):
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
                url(r"^auction/(?P<resource_name>%s)%s$" % (self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
                url(r"^auction/(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
                ]
    
    def build_filters(self, filters=None):
        """
        Apply filters depending on the url that was used to access the resource.
        """
        ret_filters = super(AuctionByCategoryResource, self).build_filters(filters)
        if 'category_id' in filters:
            ret_filters['item__categories__id'] = int(filters['category_id'])
        else:
            raise BadRequest("not valid category_id.")
        return ret_filters   

class BidPackageResource(ModelResource):
    
    class Meta:
        queryset = BidPackage.objects.all()
        resource_name = 'bid_package'
        authorization = ReadOnlyAuthorization()
        authentication = SessionAuthentication()
        include_resource_uri = False   

class addBidResource(ModelResource):
     
    """
        Let a user to add bids into an auction
    """
    
    class Meta:
        resource_name = 'addBid'
        authorization = Authorization()
        authentication = CustomAuthentication()
        queryset = Auction.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ['get']
        include_resource_uri = False
           
    def base_urls(self):
        return [
            url(r"^auction/(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^auction/(?P<resource_name>%s)/(?P<auction_id>\d+)%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="addBid"),
        ]  

    def obj_get(self, bundle, **kwargs):
        
        error = None
        auction = Auction.objects.get(id=kwargs['auction_id'])
        bundle.obj = auction
     
        
        # check if authorized
        self.authorized_read_detail('', bundle)
        
        member = bundle.request.user
        try:
            amount = auction.minimum_precap
        except ValueError:
            error = "not int"
        amount += member.auction_bids_left(auction)
        if auction.status == 'precap' and auction.can_precap(member, amount):
             #check max tokens for member per auction
            if auction.bid_type != 'bid' and (((amount*100)/(auction.precap_bids)) > ConfigKey.get('AUCTION_MAX_TOKENS', 100)):
                error = 'AUCTION_MAX_TOKENS_REACHED'
            auction.place_precap_bid(member, amount)
            client.updatePrecap(auction)
        else:
            if auction.bid_type == 'bid':
             error = 'NO_ENOUGH_CREDITS'
            else:
             error = 'NO_ENOUGH_TOKENS'
        if error:
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, error, http.HttpApplicationError))
        return bundle.obj


class remBidResource(ModelResource):
     
    """
        Let a user to remove bids into an auction
    """
    
    class Meta:
        resource_name = 'remBid'
        authorization = Authorization()
        authentication = CustomAuthentication()
        queryset = Auction.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ['get']
        include_resource_uri = False
           
    def base_urls(self):
        return [
            url(r"^auction/(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^auction/(?P<resource_name>%s)/(?P<auction_id>\d+)%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="remBid"),
        ]  

    def obj_get(self, bundle, **kwargs):
          
        
        error = None
        auction = Auction.objects.get(id=kwargs['auction_id'])
        bundle.obj = auction
     
        # check if authorized
        self.authorized_read_detail('', bundle)
        
        member = bundle.request.user
        try:
            amount = auction.minimum_precap
        except ValueError:
            error = "not int"
        
        amount = member.auction_bids_left(auction) - amount
        if auction.can_precap(member, amount):
            auction.place_precap_bid(member, amount, 'remove')
            client.updatePrecap(auction)
        if member.auction_bids_left(auction) <= 0:
            auction.leave_auction(member)
            clientMessages = []
            clientMessages.append(client.updatePrecapMessage(auction))
            clientMessages.append(auctioneer.member_left_message(auction, member))
            client.sendPackedMessages(clientMessages)
        if error:
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, error, http.HttpApplicationError))    
        return bundle.obj

class claimBidResource(AuctionResource):
     
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
        detail_allowed_methods = ['put']
        include_resource_uri = False
        detail_uri_name = 'auction_id'
        
    def prepend_urls(self):
        return [
            url(r"^auction/(?P<resource_name>%s)%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),  
        ]  

    def obj_update(self,bundle, **kwargs ):
        
        error = None
        auction = Auction.objects.get(id=kwargs['auction_id'])
        bundle.obj = auction
        
        # check if authorized
        self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        
        member = bundle.request.user
        try:
            amount = auction.minimum_precap
        except ValueError:
            error = "not int"
        
        bidNumber = int(bundle.data['bidNumber'])
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
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, error, http.HttpApplicationError))
        return AuctionResource.full_dehydrate_available(AuctionResource(),bundle.request,bundle)


class joinAuctionResource(ModelResource):
     
    """
        Let a user to joing an auction
    """
    
    class Meta:
        resource_name = 'joinAuction'
        authorization = Authorization()
        authentication = CustomAuthentication()
        queryset = Auction.objects.all()
        list_allowed_methods = []
        detail_allowed_methods = ['get']
        include_resource_uri = False
        
    def base_urls(self):
        return [
            url(r"^auction/(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^auction/(?P<resource_name>%s)/(?P<auction_id>\d+)%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="joinAuction"),
        ]   

    def obj_get(self,bundle, **kwargs ):
        
        error = None
        auction = Auction.objects.get(id=kwargs['auction_id'])
        bundle.obj = auction
        
        # check if authorized
        self.authorized_read_detail('', bundle)
        member = bundle.request.user
        try:
            amount = auction.minimum_precap
            
        except ValueError:
           
            error = "not int"
        if amount < auction.minimum_precap:
            error = "not minimun, minimun : %s" % auction.minimum_precap
        joining = False
        if auction.can_precap(member, amount):
            joining = auction.place_precap_bid(member, amount)
        
        if joining:
            clientMessages = []
            clientMessages.append(client.updatePrecapMessage(auction))
            clientMessages.append(auctioneer.member_joined_message(auction, member))
            client.sendPackedMessages(clientMessages)
        else:
            if auction.bid_type == 'bid':
                error = 'NO_ENOUGH_CREDITS'
            else:
                error = 'NO_ENOUGH_TOKENS'
        if error:
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, error, http.HttpApplicationError))
        return bundle.obj


class SendMessageResource(ModelResource):
    
    """
    Creates a new message for an auction.
    """
    class Meta:
        resource_name = 'sendMessage'
        authorization = SendMessageAuthorization()
        authentication = CustomAuthentication()
        queryset = Message.objects.all()
        collection_name = 'messages'
        list_allowed_methods = ['post']
        detail_allowed_methods = []
        include_resource_uri = False

    def post_list(self, request, **kwargs):
        deserialized = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))
        basic_bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)
        text = basic_bundle.data['text']
        if 'auction_id' in basic_bundle.data:
            auction_id = basic_bundle.data['auction_id']
            auction = Auction.objects.get(id=auction_id)
            user_type_id=ContentType.objects.filter(name='user').all()[0]
            auction_type_id=ContentType.objects.filter(name='auction').all()[0]
            user = ChatUser.objects.get_or_create(object_id=request.user.id, content_type=user_type_id)[0]
            bundle = self.obj_create(bundle=basic_bundle, text=text, user=user, content_type=auction_type_id, object_id=auction.id)
            client.do_send_chat_message(auction, bundle.obj)
        else:
            member = request.user
            client.do_send_global_chat_message(member, text)
        return self.create_response(request, {} , response_class=http.HttpCreated)
    
    