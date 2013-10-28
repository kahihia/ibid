from tastypie.authorization import Authorization,ReadOnlyAuthorization
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource, ALL

from apps.main.models import Notification
from bidding.models import Member, Auction, Item,ConvertHistory,BidPackage

from chat.models import Message

from django_facebook.connect import connect_user
from django_facebook.exceptions import MissingPermissionsError
import open_facebook

from django.conf import settings
from django.conf.urls import url
from datetime import datetime
import json
from tastypie import fields
import logging

log= logging.getLogger('django')


#AUTHORIZATION
class UserNotificationsAuthorization(ReadOnlyAuthorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(recipient=bundle.request.user, status='Unread')

    def read_detail(self, object_list, bundle):
        if bundle.request.path.endswith('schema/'):
            return True
        return bundle.obj.recipient == bundle.request.user

    def update_detail(self, object_list, bundle):
        return bundle.obj.recipient == bundle.request.user

class UserByTokenAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no lists.")
    def read_detail(self, object_list, bundle):
        return bundle.obj != None
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
      
class AuctionAuthorization(ReadOnlyAuthorization):
    
    def read_list(self, object_list, bundle):
        try:
            member_id = int(bundle.request.META['REQUEST_URI'].split('/')[-1])
        except:
            return object_list
        if member_id == bundle.request.user.id :    
                return object_list
        else:
            raise Unauthorized("Sorry, you're not the user.")     
    def read_detail(self, object_list, bundle):
        return bundle.obj != None
    
class MemberAuthorization(ReadOnlyAuthorization):
    def update_detail(self, object_list, bundle):
        return bundle.request.user.id == bundle.obj.id


#RESOURCES

class NotificationResource(ModelResource):
    
    class Meta:
        resource_name = 'notification'
        list_allowed_methods = ['get', 'put']
        detail_allowed_methods = ['get', 'put', 'patch']
        authorization = UserNotificationsAuthorization()
        queryset = Notification.objects.order_by('created')
        always_return_data = True
        filtering = {
            'status': ALL,
        }
        
    def hydrate(self, bundle):
        bundle.obj = Notification.objects.get(id=bundle.data['pk'])
        bundle.obj.status = bundle.data['objects'][0]['message']['status']
        bundle.obj.updated = datetime.now()
        return bundle

class UserByFBTokenResource(ModelResource):
    class Meta:
        resource_name = 'user/byFBToken'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authorization = UserByTokenAuthorization()
        queryset = Member.objects.all()
        detail_uri_name = 'access_token'
        include_resource_uri = False

    def obj_get(self, bundle, **kwargs):
        """
        A hook to allow making returning the list of available objects.

        This needs to be implemented at the user level.

        ``ModelResource`` includes a full working version specific to Django's
        ``Models``.
        """

        access_token = kwargs['access_token']
        db_user = Member.objects.none()
        try:
            try:
                graph = self.check_permissions(access_token)
                of = open_facebook.OpenFacebook(access_token)
                facebook_user = of.get('me/',)
                action, db_user = connect_user(bundle.request, access_token)
            except Exception as e:
                bundle.request.META['error'] = str(e)
        except open_facebook.exceptions.OAuthException as e:
            bundle.request.META['error'] = str(e)
        return db_user
    
    def dehydrate(self, bundle):
        bundle.data['display_name'] = "%s %s" % (bundle.obj.first_name, bundle.obj.last_name) 
        bundle.data['won_auctions'] = bundle.obj.auction_set.filter(winner=bundle.obj).all().count()
        bundle.data['actual_auctions'] = bundle.obj.auction_set.exclude(status='waiting_payment').exclude(status='paid').all().count()
        return bundle
    
    def full_dehydrate(self, bundle, for_list=False):
        """
        Given a bundle with an object instance, extract the information from it
        to populate the resource.
        """
        
        if bundle.obj:
           bundle = super(UserByFBTokenResource, self).full_dehydrate(bundle)
        return bundle
    
    
    def check_permissions(self, access_token):
        graph = open_facebook.OpenFacebook(access_token)
        permissions = set(graph.permissions())
        scope_list = set(settings.FACEBOOK_DEFAULT_SCOPE)
        missing_perms = scope_list - permissions
        if missing_perms:
            permissions_string = ', '.join(missing_perms)
            error_format = 'Permissions Missing: %s'
            raise MissingPermissionsError(error_format % permissions_string)
        return graph

    def alter_detail_data_to_serialize(self, request, data):
        """
        A hook to alter detail data just before it gets serialized & sent to the user.

        Useful for restructuring/renaming aspects of the what's going to be
        sent.

        Should accommodate for receiving a single bundle of data.
        """
        try:
            if request.META['error']:
                error ={}
                error['ERROR'] = request.META['error']
                data.data = error
        except Exception as e:
            pass
        return data
    
class MemberResource(ModelResource):
    
    class Meta:
        queryset = Member.objects.all()
        resource_name = 'members'
        authorization = MemberAuthorization()
        include_resource_uri = False
        fields=['first_name','facebook_id']
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/convert_tokens$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]   
    
    def dehydrate(self, bundle):
        bundle.data['display_name'] = "%s %s" % (bundle.obj.first_name, bundle.obj.last_name) 
        return bundle
    
    def obj_update(self, bundle, **kwargs):
        bundle.obj = Member.objects.get(id = int(bundle.data['id']))
        amount = bundle.obj.maximun_bids_from_tokens()
        ConvertHistory.convert(bundle.obj, int(amount))
        return self.save(bundle)

class ItemResource(ModelResource):
    
    class Meta:
        queryset = Item.objects.all()
        resource_name = 'items'
        authorization = ReadOnlyAuthorization()
        include_resource_uri = False
        fields=['name', 'retail_price']

    def dehydrate(self, bundle):
        bundle.data['itemImage'] = bundle.obj.get_thumbnail(size="107x72")
        return bundle

class AuctionResource(ModelResource):
    
    winner = fields.ForeignKey(MemberResource, 'winner',null=True, full=True)
    item = fields.ForeignKey(ItemResource, 'item', full=True)

    class Meta:
        queryset = Auction.objects.all()
        resource_name = 'auctions'
        authorization = AuctionAuthorization()
        excludes = ['is_active']
        
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/user/(?P<member_id>\w[\w/-]*)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/getAuctionsIwon/(?P<winner_id>\w[\w/-]*)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
        ]      
    def get_list(self, request, **kwargs):
        """
        Returns a serialized list of resources.

        Calls ``obj_get_list`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).
        """
        # TODO: Uncached for now. Invalidation that works for everyone may be
        #       impossible.
        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_uri(), limit=self._meta.limit, max_limit=self._meta.max_limit, collection_name=self._meta.collection_name)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.

        return_dict={'token':{},'credit':{}}
        
        token_finished_list=[]
        token_available_list=[]
        credit_finished_list=[]
        credit_available_list=[]
        token_auctions_wout_winner=[]
        credit_auctions_wout_winner=[]
    
        for obj in to_be_serialized[self._meta.collection_name]:
            finished = False
            try:
                int(request.META['REQUEST_URI'].split('/')[-1])
            except:
                finished = obj.status != 'precap'
                    
            bundle = self.build_bundle(obj=obj, request=request)
            if obj.bid_type=='token':
                if obj.is_active==True and finished:
                    if obj.winner:
                        token_finished_list.append(self.full_dehydrate_finished(request, bundle, for_list=True))
                    else:
                        token_auctions_wout_winner.append(self.full_dehydrate_finished(request, bundle, for_list=True))
                else:
                    token_available_list.append(self.full_dehydrate_available(request, bundle, for_list=True))
                
            if obj.bid_type=='bid':
                if obj.is_active==True and finished:
                    if obj.winner:
                        credit_finished_list.append(self.full_dehydrate_finished(request, bundle, for_list=True))
                    else:
                        credit_auctions_wout_winner.append(self.full_dehydrate_finished(request, bundle, for_list=True))
                else:
                    credit_available_list.append(self.full_dehydrate_availabe(request, bundle, for_list=True))
            
        return_dict['token']['finished'] = token_finished_list
        return_dict['token']['available'] = token_available_list
        return_dict['token']['wout_winner'] = token_auctions_wout_winner
        return_dict['credit']['finished'] = credit_finished_list
        return_dict['credit']['available'] = credit_available_list
        return_dict['credit']['wout_winner'] = credit_auctions_wout_winner
        return_dict['token']['mine'] = []
        return_dict['credit']['mine'] = []
        
        to_be_serialized[self._meta.collection_name] = return_dict
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)
    
    def build_filters(self, filters=None):
        ret_filters = super(AuctionResource, self).build_filters(filters)
        if filters.get('member_id'):
            ret_filters['bidders__id'] = int(filters['member_id'])
            ret_filters['status__in'] = ('precap' ,'waiting', 'processing', 'pause')
        if filters.get('winner_id'):
            ret_filters['winner_id'] = int(filters['winner_id'])
            ret_filters['status__in'] = ['paid' ,'waiting_payment']
        ret_filters['is_active'] = True
        return ret_filters
    
    def apply_sorting(self, obj_list, options=None):
        return obj_list.order_by('-status', 'won_date')
    
    def full_dehydrate_available(self, request, bundle, for_list=False):
        bundle = super(AuctionResource, self).full_dehydrate(bundle)
        bundle.data['completion'] = bundle.obj.completion()
        bundle.data['bidders'] = bundle.obj.bidders.count()
        try:
            member_id = int(request.META['REQUEST_URI'].split('/')[-1])
            member=Member.objects.get(id=member_id)
            bundle.data['placed'] = member.auction_bids_left(bundle.obj)
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
        except Exception:
            bundle.data['placed']= 0    
        return bundle
    
    def full_dehydrate_finished(self, request, bundle, for_list=False):
        bundle = super(AuctionResource, self).full_dehydrate(bundle)
        bundle.data['bidNumber'] = bundle.obj.used_bids() / bundle.obj.minimum_precap
        bundle.data['placed']= 0
        bundle.data['auctioneerMessages'] = []
        bundle.data['chatMessages'] = []
        return bundle
    
    
class BidPackageResource(ModelResource):
    
    class Meta:
        queryset = BidPackage.objects.all()
        resource_name = 'get_packages'
        authorization = ReadOnlyAuthorization()
        include_resource_uri = False   

    