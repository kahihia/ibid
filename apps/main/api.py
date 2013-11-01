from tastypie.authorization import Authorization,ReadOnlyAuthorization
from tastypie.exceptions import Unauthorized, ImmediateHttpResponse
from tastypie import http
from tastypie.resources import ModelResource, ALL,Resource
from tastypie.utils import trailing_slash
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


####################AUTHORIZATION METHODS TO ENABLE OR DISABLE DATA ACCES FOR A USER

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

class UserNotificationsAuthorization(NoAuthorization):
 
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
    
    def update_detail(self, object_list, bundle):
        return bundle.obj.recipient == bundle.request.user


class UserByTokenAuthorization(NoAuthorization):
    
    """
    This authorization class is used to login or sign in and retrieves their details
    """
    def read_detail(self, object_list, bundle):
        return bundle.obj != None


class PlayerActionAuthorization(NoAuthorization):

    """
    Only allows to modify the auction bids if the request user is in the auction.
    If joining an auction, checks that the user has not already joined.
    """    
    def update_detail(self, object_list, bundle):
        
        log.debug('PLAYER ACTION AUTHORIZATION')
        action=bundle.request.META['REQUEST_URI'].split('/')[-2]
        log.debug(action)
        
        if action == 'join_auction':
            if bundle.request.user not in bundle.obj.bidders.all():
                return True
            else:
                return False
        return bundle.request.user in bundle.obj.bidders.all()
        
            

class AuctionAuthorization(ReadOnlyAuthorization):
    
    def read_list(self, object_list, bundle):
        """
        If querying for a member's auctions, checks that the logged member matches the member_id in the url.
        If there's no member_id in the url that means that the request is for all auctions so all auctions are allowed.
        """
        method = bundle.request.META['REQUEST_URI'].split('/')[-2]
        
        try:
            object_id = int(bundle.request.META['REQUEST_URI'].split('/')[-1])
        except:    
            return object_list
        if method=='user' or method =='getAuctionsIwon':
           
            if object_id == bundle.request.user.id :    
                    return object_list
            else:    
                raise Unauthorized("Sorry, you're not the user.")    
        else:
            return object_list
         
    
    def read_detail(self, object_list, bundle):
        return bundle.obj != None
    

class MemberAuthorization(ReadOnlyAuthorization):
    
    def update_detail(self, object_list, bundle):
        return bundle.request.user.id == bundle.obj.id


#############################RESOURCES############################################################

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
    
    """ This resource loggins or register a user using the facebook access token. """
    
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
        Check the permission throw facebook access token and logs or regiter a user.
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
                raise ImmediateHttpResponse(response = self.error_response(bundle.request, str(e), http.HttpApplicationError))
        except open_facebook.exceptions.OAuthException as e:
            raise ImmediateHttpResponse(response = self.error_response(bundle.request, str(e), http.HttpApplicationError))
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
    
class MemberResource(ModelResource):
    
    """
    Resource to interact with member data objects
    Used to convert tokens to credits 
    """
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


class CategoryResource(ModelResource):

    """ Resource to retrive data of auction's items """    
    
    class Meta:
        queryset = Category.objects.all()
        resource_name = 'category'
        authorization = ReadOnlyAuthorization()
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
        resource_name = 'items'
        authorization = ReadOnlyAuthorization()
        include_resource_uri = False
        fields=['name', 'retail_price']

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
    winner = fields.ForeignKey(MemberResource, 'winner',null=True, full=True)
    item = fields.ForeignKey(ItemResource, 'item', full=True)
    

    class Meta:
        queryset = Auction.objects.all()
        resource_name = 'auction'
        authorization = AuctionAuthorization()
        excludes = ['is_active']
        
    def base_urls(self):
        
        """
        The standard URLs this ``Resource`` should respond to.
        """
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/set/(?P<%s_list>\w[\w/;-]*)%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('get_multiple'), name="api_get_multiple"),
            url(r"^(?P<resource_name>%s)/(?P<%s>\d+)%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/user/(?P<member_id>\d+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/getAuctionsIwon/(?P<winner_id>\d+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/category/(?P<category_id>\d+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_list"),
          
        ]
        
    def get_list(self, request, **kwargs):
        """
        Returns a serialized list of resources.
        Calls ``obj_get_list`` to provide the data, then handles that result
        set and serializes it.
        Should return a HttpResponse (200 OK).
        """
        
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
            finished = ['paid' ,'waiting_payment']
            
            """ Make dehydrate in different ways depending if auction is finished or available"""           
            try:
                member_id = int(request.META['REQUEST_URI'].split('/')[-1])
                member=Member.objects.get(id=member_id)
            except:
                finished = obj.status != 'precap'
                member=None 
            bundle = self.build_bundle(obj=obj, request=request)
            if obj.bid_type=='token':
                if obj.is_active==True and finished:
                    if obj.winner:
                        token_finished_list.append(self.full_dehydrate_finished(request, bundle))
                    else:
                        token_auctions_wout_winner.append(self.full_dehydrate_finished(request, bundle))
                else:
                    token_available_list.append(self.full_dehydrate_available(request, bundle, member))
                
            if obj.bid_type=='bid':
                if obj.is_active==True and finished:
                    if obj.winner:
                        credit_finished_list.append(self.full_dehydrate_finished(request, bundle))
                    else:
                        credit_auctions_wout_winner.append(self.full_dehydrate_finished(request, bundle))
                else:
                    credit_available_list.append(self.full_dehydrate_availabe(request, bundle, member))
            
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
        
        """
        Apply filters depending on the url that was used to access the resource.
        """
        ret_filters = super(AuctionResource, self).build_filters(filters)
        if filters.get('member_id'):
            ret_filters['bidders__id'] = int(filters['member_id'])
            ret_filters['status__in'] = ('precap' ,'waiting', 'processing', 'pause')
        if filters.get('winner_id'):
            ret_filters['winner_id'] = int(filters['winner_id'])
            ret_filters['status__in'] = ['paid' ,'waiting_payment']
        if filters.get('category_id'):
            ret_filters['item__categories__id'] = int(filters['category_id'])
        ret_filters['is_active'] = True
        return ret_filters
    
    def apply_sorting(self, obj_list, options=None):
        return obj_list.order_by('-status', 'won_date')
    
    def full_dehydrate_available(self, request, bundle, member):
        
        """
        Dehydrate available auctions in two ways:
            1-for a member's auction
            2-for a general auction
        """
        
        bundle = super(AuctionResource, self).full_dehydrate(bundle)
        bundle.data['completion'] = bundle.obj.completion()
        bundle.data['bidders'] = bundle.obj.bidders.count()
        bundle.data['bid_amount'] = 0
        if member:
            bundle.data['placed'] = member.auction_bids_left(bundle.obj)
            if member == request.user and bundle.data['placed'] > 0:
                bid = bundle.obj.bid_set.get(bidder=member)
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
        format = '%d-%m-%Y' # Or whatever your date format is
        bundle.data['won_date']=bundle.obj.won_date.strftime('%d/%m/%Y')
        return bundle
    
    
    
class BidPackageResource(ModelResource):
    
    class Meta:
        queryset = BidPackage.objects.all()
        resource_name = 'get_packages'
        authorization = ReadOnlyAuthorization()
        include_resource_uri = False   



class PlayerActionResource(Resource):
    
    """
    This resource exposes the uris for playing an auction.
    It's called when a user wants to join an auction, add/remove bids into an auction
    or claim for win an auction.
    """
    
    class Meta:
        resource_name = 'player_action'
        authorization = PlayerActionAuthorization()
        collection_name = 'auction'
        always_return_data = True
        list_allowed_methods = []
        detail_allowed_methods = ['put']
        include_resource_uri = False
    
    
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/join_auction%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/addBid%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail_add_bid"),
            url(r"^(?P<resource_name>%s)/remBid%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail_rem_bid"),
            url(r"^(?P<resource_name>%s)/claim%s$" %(self._meta.resource_name,trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail_rem_bid"),
        ]  
    
    def get_object_list(self, request):
        return ''
    
    def obj_update(self, bundle, **kwargs):
        
        """
            Let a user to join an auction, add/remove bids into an auction
            or claim an auction. Depends of the url used to access the resource.
        """
        error = None
        auction = Auction.objects.get(id=bundle.data['id'])
        bundle.obj = auction
        
        # check if authorized
        self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        
        member = bundle.request.user
        method=str(bundle.request.META['REQUEST_URI']).split('/')[-2]
        try:
            amount = auction.minimum_precap
        except ValueError:
            error = "not int"
        if method=='addBid':
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
        elif method =='remBid':
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
        elif method == 'claim':
            """
            The user use the bids that has commited before to try to win the auction in
            process.
            """
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
        else:
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
        return AuctionResource.full_dehydrate_available(AuctionResource(),bundle.request,bundle,member)
        
    def alter_detail_data_to_serialize(self, request, data):
        """
        A hook to alter detail data just before it gets serialized & sent to the user.

        Useful for restructuring/renaming aspects of the what's going to be
        sent.

        Should accommodate for receiving a single bundle of data.
        """
        fix = {}
        fix['auction'] = data.data
        data.data = fix
        if data.data['auction']['placed'] <= 0:
            data.data['do'] = 'close'
        return data


class SendMessageResource(Resource):
    
    """
    Creates a new message for an auction.
    """
    class Meta:
        resource_name = 'send_message'
        authorization = Authorization()
        collection_name = 'message'
        always_return_data = True
        list_allowed_methods = []
        detail_allowed_methods = ['post']
        include_resource_uri = False

    #TODO: to hook global chat
    def prepend_urls(self):
        return [
           #url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]  
    
    def get_object_list(self, request):
        return ''

    def post_detail(self, request, **kwargs):
        log.debug(request)
        text = request.POST['text']
        if 'pk' in kwargs:
            auction_id = kwargs['pk']
            auction = Auction.objects.get(id=auction_id)
            user_type_id=ContentType.objects.filter(name='user').all()[0]
            auction_type_id=ContentType.objects.filter(name='auction').all()[0]
            user = ChatUser.objects.get_or_create(object_id=request.user.id, content_type=user_type_id)[0]
            if user.can_chat(auction.id):
                db_msg = Message.objects.create(text=text, user=user, content_type=auction_type_id, object_id=auction.id)
                client.do_send_chat_message(auction, db_msg)
        else:
            member = request.user
            client.do_send_global_chat_message(member, text)
        return self.create_response(request, {} , response_class=http.HttpCreated)
    
        
        
