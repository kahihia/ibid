# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('django')

from datetime import datetime
import time
from decimal import Decimal
import re
import open_facebook
from sorl.thumbnail import get_thumbnail
from datetime import timedelta
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.aggregates import Sum
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils.safestring import mark_safe
from django_facebook import model_managers, settings as facebook_settings
from django_facebook.utils import get_user_model

from bidding.delegate import state_delegates
from audit.models import AuditedModel


re_bids = re.compile("(\d+)")

AUCTION_STATUS_CHOICES = (
    ('precap', 'Pre-Capitalization'),
    ('waiting', 'Waiting start date'),
    ('processing', 'In Process'),
    ('pause', 'Paused'),
    ('waiting_payment', 'Waiting Payment'),
    ('paid', 'Paid'),
)

ITEM_CATEGORY_CHOICES = (
    ('elec', 'Electronics'),
    ('fash', 'Fashion'),
    ('moto', 'Motors'),
    ('ente', 'Entertainment'),
    ('deal', 'Deals & gifts'),
    ('home', 'Home & outdoors'),
    ('oth', 'Other'),
)

INVOICE_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('canceled', 'Canceled'),
)

PAYMENT_CHOICES = (
    ('direct', 'Direct'),
    ('express', 'Express'),
)

BID_TYPE_CHOICES = (
    ('bid', 'Bids'),
    ('token', 'Tokens'),
    ('bidsto', 'Bidsto')
)


class Member(AuditedModel):
    user = models.ForeignKey(User)

    bids_left = models.IntegerField(default=0)
    tokens_left = models.IntegerField(default=0)
    bidsto_left = models.IntegerField(default=0)

    session = models.TextField(default='{}')

    remove_from_chat = models.BooleanField(default=False)

    #not the prettiest but ok
    def get_bids(self, bid_type):
        """ Returns the member bids of the given type. """
        if bid_type == 'token':
            return self.tokens_left
        else:
            return self.bidsto_left + self.bids_left

    def get_bids_left(self):
        return self.get_bids('bid')

    def get_tokens_left(self):
        return self.get_bids('token')

    def set_bids(self, bid_type, amount):
        """ Sets the member bids of the given type. """
        if bid_type == 'token':
            self.tokens_left = amount
        else:
            # We first decrease bidsto
            if self.bidsto_left:
                diff = self.get_bids_left() - amount
                if self.bidsto_left >= diff:
                    self.bidsto_left -= diff
                else:
                    diff -= self.bidsto_left
                    self.bidsto_left = 0
                    self.bids_left -= diff
            else:
                self.bids_left = amount

    def maximun_bids_from_tokens(self):
        return int(self.tokens_left * settings.TOKENS_TO_BIDS_RATE)

    def get_active_auctions(self):
        return self.auction_set.filter(is_active=True).count()

    def gen_available_tokens_to_bids(self):
        NUMS = (1, 2, 5)
        n = 1
        availables = []
        maximun = self.maximun_bids_from_tokens()
        while (n * NUMS[0] < maximun):
            availables += [d * n for d in NUMS if d * n <= maximun]
            n *= 10
        if maximun not in availables:
            availables.append(maximun)
        return availables

    #    def convert(self, num_bids):
    #        if self.tokens_left >= (num_bids / settings.TOKENS_TO_BIDS_RATE):
    #            self.bidsto_left += num_bids
    #            self.tokens_left -= (num_bids / settings.TOKENS_TO_BIDS_RATE)
    #            self.save()

    def auction_bids_left(self, auction):
        """ 
        Return the amount of unused commited bids the member has for the 
        given auction.
        """

        bid = self.bid_set.filter(auction=auction)
        return bid[0].left() if bid else 0

    def precap_bids(self, auction, amount):
        """ 
        Creates the specified amount of precap bids for the user in the given 
        auction. Updates the member accordingly. 
        """

        unixtime = Decimal("%f" % time.time())
        bid, _ = Bid.objects.get_or_create(auction=auction, bidder=self, defaults={'unixtime': unixtime})

        diff = amount - bid.placed_amount

        bid.time = unixtime
        bid.placed_amount = amount
        bid.save()

        #self.bids_left -= diff
        self.set_bids(auction.bid_type, self.get_bids(auction.bid_type) - diff)
        self.save()

    def get_placed_amount(self, auction):
        """ 
        Creates the specified amount of precap bids for the user in the given 
        auction. Updates the member accordingly. 
        """

        unixtime = Decimal("%f" % time.time())
        bid, _ = Bid.objects.get_or_create(auction=auction, bidder=self, defaults={'unixtime': unixtime})

        return bid.placed_amount

    def leave_auction(self, auction):
        """ Retires the member bids from the given auction. """
        try:
            # TODO: This should be removed as is not going to be used
            bids = Bid.objects.get(auction=auction, bidder=self)
            #self.bids_left += bids.placed_amount
            self.set_bids(auction.bid_type, self.get_bids(auction.bid_type) +
                                            bids.placed_amount)
            bids.delete()
            self.save()
        except:
            logger.exception('leave_auction exception')

    def bids_history(self):
        return self.bid_set.all().order_by().values('auction__item__name', 'placed_amount', 'used_amount',
                                                    'auction__bid_type')

    #Facebook fields
    about_me = models.TextField(blank=True)
    facebook_id = models.BigIntegerField(blank=True, unique=True, null=True)
    access_token = models.TextField(blank=True, help_text='Facebook token for offline access')
    facebook_name = models.CharField(max_length=255, blank=True)
    facebook_profile_url = models.TextField(blank=True)
    website_url = models.TextField(blank=True)
    blog_url = models.TextField(blank=True)
    image = models.ImageField(blank=True, null=True,
                              upload_to='profile_images', max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    raw_data = models.TextField(blank=True)

    new_token_required = models.BooleanField(default=False,
                                             help_text='Set to true if the access token is outdated or lacks permissions')

    def refresh(self):
        '''
        Get the latest version of this object from the db
        '''
        return self.__class__.objects.get(id=self.id)

    def get_user(self):
        '''
        Since this mixin can be used both for profile and user models
        '''
        if hasattr(self, 'user'):
            user = self.user
        else:
            user = self
        return user

    def get_user_id(self):
        '''
        Since this mixin can be used both for profile and user_id models
        '''
        if hasattr(self, 'user_id'):
            user_id = self.user_id
        else:
            user_id = self.id
        return user_id

    @property
    def facebook_og_state(self):
        if not self.facebook_id:
            state = FACEBOOK_OG_STATE.NOT_CONNECTED
        elif self.access_token and self.facebook_open_graph:
            state = FACEBOOK_OG_STATE.SHARING
        else:
            state = FACEBOOK_OG_STATE.CONNECTED
        return state

    def likes(self):
        likes = FacebookLike.objects.filter(user_id=self.get_user_id())
        return likes

    def friends(self):
        friends = FacebookUser.objects.filter(user_id=self.get_user_id())
        return friends

    def disconnect_facebook(self):
        self.access_token = None
        self.new_token_required = False
        self.facebook_id = None

    def clear_access_token(self):
        self.access_token = None
        self.new_token_required = False
        self.save()

    def update_access_token(self, new_value):
        '''
        Updates the access token

        **Example**::

            # updates to 123 and sets new_token_required to False
            profile.update_access_token(123)

        :param new_value:
            The new value for access_token
        '''
        self.access_token = new_value
        self.new_token_required = False

    def extend_access_token(self):
        '''
        https://developers.facebook.com/roadmap/offline-access-removal/
        We can extend the token only once per day
        Normal short lived tokens last 1-2 hours
        Long lived tokens (given by extending) last 60 days

        The token can be extended multiple times, supposedly on every visit
        '''
        logger.info('extending access token for user %s', self.get_user())
        results = None
        if facebook_settings.FACEBOOK_CELERY_TOKEN_EXTEND:
            from django_facebook import tasks
            tasks.extend_access_token.delay(self, self.access_token)
        else:
            results = self._extend_access_token(self.access_token)
        return results

    def _extend_access_token(self, access_token):
        from open_facebook.api import FacebookAuthorization
        results = FacebookAuthorization.extend_access_token(access_token)
        access_token = results['access_token']
        old_token = self.access_token
        token_changed = access_token != old_token
        message = 'a new' if token_changed else 'the same'
        log_format = 'Facebook provided %s token, which expires at %s'
        expires_delta = timedelta(days=60)
        logger.info(log_format, message, expires_delta)
        if token_changed:
            logger.info('Saving the new access token')
            self.update_access_token(access_token)
            self.save()

        from django_facebook.signals import facebook_token_extend_finished
        facebook_token_extend_finished.send(
            sender=get_user_model(), user=self.get_user(), profile=self,
            token_changed=token_changed, old_token=old_token
        )

        return results

    def get_offline_graph(self):
        '''
        Returns a open facebook graph client based on the access token stored
        in the user's profile
        '''
        from open_facebook.api import OpenFacebook
        if self.access_token:
            graph = OpenFacebook(access_token=self.access_token)
            graph.current_user_id = self.facebook_id
            return graph


    @property
    def open_graph_new_token_required(self):
        '''
        Shows if we need to (re)authenticate the user for open graph sharing
        '''
        reauthentication = False
        if self.facebook_open_graph and self.new_token_required:
            reauthentication = True
        elif self.facebook_open_graph is None:
            reauthentication = True
        return reauthentication

    def __unicode__(self):
        return self.user.__unicode__()


    def display_name(self):
        return "%s %s" % (self.user.first_name,
                          self.user.last_name)

    def display_linked_facebook_profile(self):
        output = ""
        if self.facebook_profile_url:
            output = '<a href="%s">' % self.facebook_profile_url
        output += self.display_name()
        if self.facebook_profile_url:
            output += '</a>'
        return mark_safe(output)

    def display_picture(self):
        #of = open_facebook.OpenFacebook()
        #return get_thumbnail(of.my_image_url(size='square'), '50x50').url
        #return of.my_image_url(size='square')
        return "https://graph.facebook.com/%s/picture" % self.facebook_id

    def post_to_wall(self, **args):
        """
        Posts to the member wall. Some possible arguments are:
        picture, name, link, caption, message.
        """
        logger.debug("ARGS: %s" % args)
        of = open_facebook.OpenFacebook(self.access_token)
        response = of.set('me/feed', **args)
        logger.debug("Response: %s" % response)

    def send_notification(self, message):
        of = open_facebook.OpenFacebook(self.access_token)
        of.set('me/apprequests', message=message)

    def post_facebook_registration(self, request):
        '''
        Behaviour after registering with facebook
        '''
        from django_facebook.utils import next_redirect

        default_url = reverse('facebook_connect')
        response = next_redirect(request, default=default_url, next_key='register_next')
        #response.set_cookie('fresh_registration', self.user_id)

        return response

    def extend_access_token(self):
        pass

    def update_access_token(self, new_value):
        '''
        Updates the access token

        **Example**::

            # updates to 123 and sets new_token_required to False
            profile.update_access_token(123)

        :param new_value:
            The new value for access_token
        '''
        self.access_token = new_value
        self.new_token_required = False

    def getSession(self, key=None, default=None):
        if not key:
            if self.session:
                ss = json.loads(self.session)
                if type(ss) is not dict:
                    ss = {}
            else:
                ss = {}
            return ss
        elif type(key) is str:
            ss = self.getSession()
            if key in ss:
                return ss[key]
            else:
                return default
        else:
            raise Exception('key param is not str')

    def setSession(self, sessionDict, sessionValue=None):
        if not sessionValue and type(sessionDict) is dict:
            #just dump the dict into session
            self.session = json.dumps(sessionDict)
        elif type(sessionDict) is str:
            #set the key value
            s = self.getSession()
            s[sessionDict] = sessionValue
            self.session = json.dumps(s)

class FacebookUser(models.Model):
    '''
    Model for storing a users friends
    '''
    # in order to be able to easily move these to an another db,
    # use a user_id and no foreign key
    user_id = models.IntegerField()
    facebook_id = models.BigIntegerField()
    name = models.TextField(blank=True, null=True)
    gender = models.CharField(choices=(
        ('F', 'female'), ('M', 'male')), blank=True, null=True, max_length=1)

    objects = model_managers.FacebookUserManager()

    class Meta:
        unique_together = ['user_id', 'facebook_id']

    def __unicode__(self):
        return u'Facebook user %s' % self.name


class FacebookLike(models.Model):

    '''
    Model for storing all of a users fb likes
    '''
    # in order to be able to easily move these to an another db,
    # use a user_id and no foreign key
    user_id = models.IntegerField()
    facebook_id = models.BigIntegerField()
    name = models.TextField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)

    class Meta:

        unique_together = ['user_id', 'facebook_id']

class FACEBOOK_OG_STATE:

    class NOT_CONNECTED:

        '''
        The user has not connected their profile with Facebook
        '''
        pass

    class CONNECTED:

        '''
        The user has connected their profile with Facebook, but isn't
        setup for Facebook sharing
        - sharing is either disabled
        - or we have no valid access token
        '''
        pass

    class SHARING(CONNECTED):

        '''
        The user is connected to Facebook and sharing is enabled
        '''
        pass


class Item(AuditedModel):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=5, choices=ITEM_CATEGORY_CHOICES, blank=True, null=True)
    slug = models.SlugField(unique=True, help_text='Used to identify the item, should be unique')
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField()
    specification = models.TextField(blank=True, null=True)

    name.alphabetic_filter = True

    def get_thumbnail(self, size='107x72'):
        return settings.IMAGES_SITE + get_thumbnail(self.itemimage_set.all()[0].image.name, size).url

    def __unicode__(self):
        return self.name


class ItemImage(models.Model):
    item = models.ForeignKey(Item)
    image = models.ImageField(upload_to='items/')


class AbstractAuction(AuditedModel):
    item = models.ForeignKey(Item)
    precap_bids = models.IntegerField(help_text='Minimum amount of bids to start the auction')
    minimum_precap = models.IntegerField(help_text='This is the bidPrice', default=10)

    class Meta:
        abstract = True


class Auction(AbstractAuction):
    bid_type = models.CharField(max_length=5, choices=BID_TYPE_CHOICES, default='bid')
    status = models.CharField(max_length=15, choices=AUCTION_STATUS_CHOICES, default='precap')
    bidding_time = models.IntegerField(default=10)
    saved_time = models.IntegerField(default=0, blank=True, null=True)
    always_alive = models.BooleanField(default=False)

    bidders = models.ManyToManyField(Member, blank=True, null=True)

    #winner info
    won_date = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, blank=True, null=True)
    won_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    #scheduling options
    start_date = models.DateTimeField(help_text='Date and time the auction is scheduled to start',
                                      null=True, blank=True)

    #treshold
    threshold1 = models.IntegerField('25% Threshold',
                                     help_text='Bidding time after using 25% of commited bids. Will be ignored if blank.',
                                     null=True, blank=True, default=7)
    threshold2 = models.IntegerField('50% Threshold',
                                     help_text='Bidding time after using 50% of commited bids. Will be ignored if blank.',
                                     null=True, blank=True, default=5)
    threshold3 = models.IntegerField('75% Threshold',
                                     help_text='Bidding time after using 75% of commited bids. Will be ignored if blank.',
                                     null=True, blank=True, default=3)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def _state_delegate(self):
        return state_delegates[self.status](self)

    def __getattr__(self, name):
        """ Tries to forward non resolved calls to the delegate objects. """
        logger.debug("Name: %s" % name)
        sd = self._state_delegate()
        if hasattr(sd, name):
            return getattr(sd, name)

        if hasattr(super(Auction, self), '__getattr__'):
            return super(Auction, self).__getattr__(name)
        else:
            raise AttributeError


    def placed_bids(self):
        """ Returns the amount of bids commited in precap. """
        return self.auction.bid_set.aggregate(Sum('placed_amount'))['placed_amount__sum'] or 0

    def used_bids(self):
        """ Returns the amount of precap bids already used in the auction. """
        return self.bid_set.aggregate(Sum('used_amount'))['used_amount__sum'] or 0

    def price(self):
        """ Returns the current price of the auction. """
        dollars = float(self.used_bids()/self.minimum_precap) / 100
        return Decimal('%.2f' % dollars)

    def has_joined(self, member):
        """ Returns True if the member has joined the auction. """
        return member in self.bidders.all()

    def bidder_mails(self):
        """ Returns a list of mails of members that have joined this auction. """

        return self.bidders.values_list('user__email', flat=True)

    def getBidNumber(self):
        return self.used_bids()/self.minimum_precap

    def __unicode__(self):
        return u'%s - %s' % (self.item.name, self.get_status_display())


class PrePromotedAuction(AbstractAuction):
    bid_type = models.CharField(max_length=5, choices=BID_TYPE_CHOICES, default='bid')
    status = models.CharField(max_length=15, choices=AUCTION_STATUS_CHOICES, default='precap')
    bidding_time = models.IntegerField(default=10)
    saved_time = models.IntegerField(default=0, blank=True, null=True)

    #treshold
    threshold1 = models.IntegerField('25% Threshold',
                                     help_text='Bidding time after using 25% of commited bids. Will be ignored if blank.',
                                     null=True, blank=True, default=12)
    threshold2 = models.IntegerField('50% Threshold',
                                     help_text='Bidding time after using 50% of commited bids. Will be ignored if blank.',
                                     null=True, blank=True, default=8)
    threshold3 = models.IntegerField('75% Threshold',
                                     help_text='Bidding time after using 75% of commited bids. Will be ignored if blank.',
                                     null=True, blank=True, default=5)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def _state_delegate(self):
        return state_delegates[self.status](self)

    def __getattr__(self, name):
        """ Tries to forward non resolved calls to the delegate objects. """
        logger.debug("Name: %s" % name)
        sd = self._state_delegate()
        if hasattr(sd, name):
            return getattr(sd, name)

        if hasattr(super(PrePromotedAuction, self), '__getattr__'):
            return super(PrePromotedAuction, self).__getattr__(name)
        else:
            raise AttributeError


    def placed_bids(self):
        """ Returns the amount of bids commited in precap. """
        return self.auction.bid_set.aggregate(Sum('placed_amount')
        )['placed_amount__sum'] or 0

    def used_bids(self):
        """ Returns the amount of precap bids already used in the auction. """
        return self.bid_set.aggregate(Sum('used_amount')
        )['used_amount__sum'] or 0

    def price(self):
        """ Returns the current price of the auction. """

        dollars = float(self.used_bids()) / 100
        return Decimal('%.2f' % dollars)

    def has_joined(self, member):
        """ Returns True if the member has joined the auction. """

        return member in self.bidders.all()

    def bidder_mails(self):
        """ Returns a list of mails of members that have joined this auction. """

        return self.bidders.values_list('user__email', flat=True)

    def __unicode__(self):
        return u'%s - %s' % (self.item.name, self.get_status_display())


class PromotedAuction(Auction):
    promoter = models.ForeignKey(Member, blank=False, null=False, related_name="promoter_user")


class Bid(AuditedModel):
    auction = models.ForeignKey(Auction)
    bidder = models.ForeignKey(Member)

    #why unix time and not date?
    unixtime = models.DecimalField(max_digits=17, decimal_places=5, db_index=True)

    #Created on precap. Marked as used when is placed during the auction.
    placed_amount = models.IntegerField(default=0)
    used_amount = models.IntegerField(default=0)

    def left(self):
        """ Returns the amount of placed bids that haven't been used. """

        return self.placed_amount - self.used_amount

    class Meta:
        unique_together = ('auction', 'bidder')


class BidPackage(models.Model):
    title = models.CharField(max_length=55)
    description = models.TextField()
    price = models.IntegerField()
    bids = models.IntegerField(default=0)
    image = models.ImageField(upload_to='bid_packages/', blank=True, null=True)

    def __unicode__(self):
        return self.title


class AuctionInvoice(AuditedModel):
    auction = models.ForeignKey(Auction)
    member = models.ForeignKey(Member)
    status = models.CharField(max_length=55, default='created', choices=INVOICE_CHOICES)
    payment = models.CharField(max_length=55, default='direct', choices=PAYMENT_CHOICES)
    uid = models.CharField(max_length=40, db_index=True)
    created = models.DateTimeField(default=datetime.now)


from paypal.standard.ipn.signals import payment_was_successful


def addbids(sender, **kwargs):
#TODO move to signals.py?

    ipn_obj = sender
    if ipn_obj.custom.startswith('item'):
        invoice = AuctionInvoice.objects.get(uid=ipn_obj.invoice)
        auction = invoice.auction
        auction.status = 'paid'
        auction.save()
        invoice.status = 'paid'
        invoice.save()
        #TODO maybe pay method in auction. And delete bid objects there


payment_was_successful.connect(addbids)


class Invitation(AuditedModel):
    inviter = models.ForeignKey(Member)
    invited_facebook_id = models.CharField(max_length=100)
    deleted = models.BooleanField(default=False) #facebook forced you to remove the invitation once used but not anymore


class AuctionInvitation(models.Model):
    """DEPRECATED"""
    inviter = models.ForeignKey(Member)
    request_id = models.BigIntegerField()
    auction = models.ForeignKey(Auction)

    def delete_facebook_request(self, member):
        """ Deletes the user request from the facebook profile. """
        of = open_facebook.OpenFacebook(member.access_token)
        of.delete('{request_id}_{user_id}'.format(request_id=self.request_id,
                                                  user_id=member.facebook_id))


class ConvertHistory(models.Model):
    member = models.ForeignKey(Member)
    tokens_amount = models.IntegerField(null=True, default=0)
    bids_amount = models.IntegerField(null=True, default=0)
    total_tokens = models.IntegerField(default=0)
    total_bids = models.IntegerField(default=0)
    total_bidsto = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now=True)

    @staticmethod
    def convert(member, num_bids):
        tokens_amount = (num_bids / settings.TOKENS_TO_BIDS_RATE)

        print "convert"
        print tokens_amount, member.tokens_left, tokens_amount

        if member.tokens_left >= tokens_amount:
            #TODO: add bidsto
            #member.bidsto_left += num_bids
            member.bids_left += num_bids
            member.tokens_left -= tokens_amount
            member.save()

        ConvertHistory.objects.create(member=member,
                                      tokens_amount=tokens_amount,
                                      bids_amount=num_bids,
                                      total_tokens=member.tokens_left,
                                      total_bids=member.bids_left,
                                      total_bidsto=member.bidsto_left,
        )


FB_STATUS_CHOICES = (('placed', 'placed'),
                     ('confirmed', 'confirmed'),
)


class FBOrderInfo(AuditedModel):
    member = models.ForeignKey(Member)
    package = models.ForeignKey(BidPackage)
    status = models.CharField(choices=FB_STATUS_CHOICES, max_length=25)


@receiver(post_save, sender=FBOrderInfo)
def on_confirmed_order(sender, instance, **kwargs):
    """Function to add order to the history when confirmed"""
    if instance.status == 'confirmed':
        ConvertHistory.objects.create(member=instance.member,
                                      tokens_amount=0,
                                      bids_amount=instance.package.bids,
                                      total_tokens=instance.member.tokens_left,
                                      total_bids=instance.member.bids_left,
                                      total_bidsto=instance.member.bidsto_left,
        )

class ConfigKey(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    def __unicode__(self):
        return self.key
