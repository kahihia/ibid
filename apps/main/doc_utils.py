from __future__ import unicode_literals
from rest_framework.compat import six
from rest_framework.views import APIView
from rest_framework import serializers
from bidding.models import Member, Auction, Item, ConvertHistory, BidPackage, ConfigKey, Bid,Category, IOPaymentInfo, BID_TYPE_CHOICES, AUCTION_STATUS_CHOICES
from apps.main.models import Notification, NOTIFICATION_TYPES
import types
from datetime import datetime
    
def api_doc_view(http_method_names, instance_serializer=None):

    """
    Decorator that converts a function-based view into an APIView subclass.
    Takes a list of allowed methods for the view as an argument.
    """

    def decorator(func):

        WrappedAPIView = type(
            six.PY3 and 'WrappedAPIView' or b'WrappedAPIView',
            (APIView,),
            {'__doc__': func.__doc__}
        )

        # Note, the above allows us to set the docstring.
        # It is the equivalent of:
        #
        #     class WrappedAPIView(APIView):
        #         pass
        #     WrappedAPIView.__doc__ = func.doc    <--- Not possible to do this

        # api_doc_view applied without (method_names)
        assert not(isinstance(http_method_names, types.FunctionType)), \
            '@api_doc_view missing list of allowed HTTP methods'

        # api_doc_view applied with eg. string instead of list of strings
        assert isinstance(http_method_names, (list, tuple)), \
            '@api_doc_view expected a list of strings, received %s' % type(http_method_names).__name__

        allowed_methods = set(http_method_names) | set(('options',))
        WrappedAPIView.http_method_names = [method.lower() for method in allowed_methods]

        def handler(self, *args, **kwargs):
            return func(*args, **kwargs)

        for method in http_method_names:
            setattr(WrappedAPIView, method.lower(), handler)
        
        class Body(serializers.Serializer):
            
            def __init__(self, **kwargs):
                super(Body, self).__init__(**kwargs) 
        
        def get_serializer_class(self):
            if instance_serializer:
                return instance_serializer
            return Body
        
        setattr(WrappedAPIView, 'get_serializer_class', get_serializer_class)
        
        WrappedAPIView.__name__ = func.__name__

        WrappedAPIView.renderer_classes = getattr(func, 'renderer_classes',
                                                  APIView.renderer_classes)

        WrappedAPIView.parser_classes = getattr(func, 'parser_classes',
                                                APIView.parser_classes)

        WrappedAPIView.authentication_classes = getattr(func, 'authentication_classes',
                                                        APIView.authentication_classes)

        WrappedAPIView.throttle_classes = getattr(func, 'throttle_classes',
                                                  APIView.throttle_classes)

        WrappedAPIView.permission_classes = getattr(func, 'permission_classes',
                                                    APIView.permission_classes)
        
        return WrappedAPIView.as_view()
    return decorator

class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=55)
    description = serializers.CharField()
    image = serializers.ImageField(blank=True)
    
class MemberSerializer(serializers.Serializer):
    about_me = serializers.CharField()
    access_token = serializers.CharField()
    actual_auctions =  serializers.IntegerField()
    bids_left =  serializers.IntegerField()
    bidsto_left =  serializers.IntegerField()
    blog_url = serializers.URLField()
    date_joined = serializers.DateTimeField()
    date_of_birth = serializers.DateField()
    display_name = serializers.CharField()
    email = serializers.EmailField()
    facebook_id = serializers.IntegerField()
    facebook_name =  serializers.CharField()
    facebook_open_graph = serializers.BooleanField()
    facebook_profile_url = serializers.URLField()
    first_name = serializers.CharField()
    gender = serializers.CharField()
    id = serializers.IntegerField()
    image = serializers.ImageField()
    image_thumb = serializers.URLField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    last_login = serializers.DateTimeField()
    last_name = serializers.CharField()
    new_token_required = serializers.BooleanField()
    password = serializers.CharField()
    raw_data = serializers.CharField()
    remove_from_chat = serializers.BooleanField()
    session = serializers.CharField()
    tokens_left = serializers.IntegerField()
    username = serializers.CharField()
    website_url = serializers.URLField()
    won_auctions = serializers.IntegerField()
  
class NotificationSerializer(serializers.Serializer):
    recipient =MemberSerializer()
    sender = MemberSerializer()
    notification_type = serializers.ChoiceField(choices=NOTIFICATION_TYPES,default='text')
    message = serializers.CharField(blank=True)
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    status = serializers.CharField(default='Unread', max_length=20)
    
class ItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(help_text='Used to identify the item, should be unique')
    retail_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, blank=True)
    description = serializers.CharField()
    specification = serializers.CharField(blank=True)
    categories = CategorySerializer(many=True, blank=True)
    itemImage = serializers.ImageField(blank=True)

class MessageSerializer(serializers.Serializer):
    text = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    auction_id = serializers.IntegerField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    
class AuctionSerializer(serializers.Serializer):
    item = ItemSerializer(read_only=True)
    precap_bids = serializers.IntegerField(help_text='Minimum amount of bids to start the auction',read_only=True)
    minimum_precap = serializers.IntegerField(help_text='This is the bidPrice', default=10,read_only=True)
    bid_type = serializers.ChoiceField(choices=BID_TYPE_CHOICES, default='bid', help_text='Type of currency for this auction.',read_only=True)
    status = serializers.ChoiceField(choices=AUCTION_STATUS_CHOICES, default='precap', help_text='Auction status.',read_only=True)
    bidding_time = serializers.IntegerField(default=10, help_text='Auction initial timer',read_only=True)
    saved_time = serializers.IntegerField(default=0, blank=True, help_text='Saved bidding time for later use.',read_only=True)
    finish_time = serializers.IntegerField(default=0, blank=True,read_only=True)
    always_alive = serializers.BooleanField(default=False, help_text='Wether the auction copies itself after precap.',read_only=True)
    is_active = serializers.BooleanField(default=True,read_only=True)
    priority = serializers.IntegerField(default=-1, help_text='Used for sorting.',read_only=True)
    categories = CategorySerializer(many=True, blank=True,read_only=True)
    winner = MemberSerializer(blank=True,read_only=True)
    won_date = serializers.DateTimeField(blank=True,read_only=True)
    won_price = serializers.DecimalField(max_digits=10, decimal_places=2,blank=True,read_only=True)
    start_date = serializers.DateTimeField(help_text='Date and time the auction is scheduled to start',blank=True,read_only=True)
    threshold1 = serializers.IntegerField('25% Threshold',
                                     help_text='Bidding time after using 25% of commited bids. Will be ignored if blank.',blank=True, default=7,read_only=True)
    threshold2 = serializers.IntegerField('50% Threshold',
                                     help_text='Bidding time after using 50% of commited bids. Will be ignored if blank.',blank=True, default=5,read_only=True)
    threshold3 = serializers.IntegerField('75% Threshold',
                                     help_text='Bidding time after using 75% of commited bids. Will be ignored if blank.',blank=True, default=3,read_only=True)
    bidNumber = serializers.IntegerField(read_only=True)
    bid_amount = serializers.IntegerField(read_only=True)
    bidders = serializers.IntegerField(read_only=True)
    chatMessages = MessageSerializer(many=True,read_only=True)
    completion = serializers.IntegerField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    mine = serializers.BooleanField(read_only=True)
    placed = serializers.IntegerField(read_only=True)
    timeleft = serializers.IntegerField(read_only=True)
    auctioneerMessages = MessageSerializer(many=True, read_only=True)
    
class ClaimSerializer(AuctionSerializer):
    bidNumber = serializers.IntegerField(help_text="Total number of this auction's bids used.")

class BidPackageSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=55)
    description = serializers.CharField()
    price = serializers.IntegerField()
    bids = serializers.IntegerField(default=0)
    image = serializers.ImageField(blank=True)
    id = serializers.IntegerField()

class AppleIbidPackageIdsSerializer(serializers.Serializer):
    value = serializers.CharField()

#class IOPaymentInfoSerializer(serializers.Serializer):
    #member = MemberSerializer(read_only=True)
    #package = BidPackageSerializer(read_only=True)
    #transaction_id = serializers.IntegerField(read_only=True)  # this field should be unique
    #purchase_date = serializers.DateTimeField(blank=True, read_only=True)
    #receipt_data = serializers.CharField(max_length=255, help_text = 'Should be sent as a json, {"receipt-data": "..."}', read_only=True)
    
