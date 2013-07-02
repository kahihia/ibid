from datetime import datetime
import time
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils.safestring import mark_safe
import re

from django.db import models
from django.contrib.auth.models import User

from django.core.urlresolvers import reverse
from bidding.delegate import state_delegates
import open_facebook
from sorl.thumbnail import get_thumbnail
from django.db.models.aggregates import Sum
from settings import IMAGES_SITE
from django.conf import settings
import logging

logger = logging.getLogger('django')

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


class Member(models.Model):
    user = models.ForeignKey(User)

    bids_left = models.IntegerField(default=0)
    tokens_left = models.IntegerField(default=0)
    bidsto_left = models.IntegerField(default=0)

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

        # TODO: This should be removed as is not going to be used
        bids = Bid.objects.get(auction=auction, bidder=self)
        #self.bids_left += bids.placed_amount
        self.set_bids(auction.bid_type, self.get_bids(auction.bid_type) +
                                        bids.placed_amount)
        bids.delete()
        self.save()

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
        response.set_cookie('fresh_registration', self.user_id)

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
        #self.new_token_required = False

    def __unicode__(self):
        return self.user.username


class Item(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=5, choices=ITEM_CATEGORY_CHOICES, blank=True, null=True)
    slug = models.SlugField(unique=True, help_text='Used to identify the item, should be unique')
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField()
    specification = models.TextField(blank=True, null=True)

    name.alphabetic_filter = True

    def get_thumbnail(self, size='70x70'):
        return IMAGES_SITE + get_thumbnail(self.itemimage_set.all()[0].image.name, size).url

    def __unicode__(self):
        return self.name


class ItemImage(models.Model):
    item = models.ForeignKey(Item)
    image = models.ImageField(upload_to='items/')

class AbstractAuction(models.Model):
    item = models.ForeignKey(Item)
    precap_bids = models.IntegerField(help_text='Minimum amount of bids to start the auction')
    minimum_precap = models.IntegerField(help_text='Minimum amount of bids to join', default=5)

    class Meta:
        abstract = True


class Auction(AbstractAuction):
    bid_type = models.CharField(max_length=5, choices=BID_TYPE_CHOICES, default='bid')
    status = models.CharField(max_length=15, choices=AUCTION_STATUS_CHOICES, default='precap')
    bidding_time = models.IntegerField(default=10)
    saved_time = models.IntegerField(default=0, blank=True, null=True)

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

        dollars = float(self.used_bids()) / 100
        return Decimal('%.2f' % dollars)

    def has_joined(self, member):
        """ Returns True if the member has joined the auction. """
        return member in self.bidders.all()

    def bidder_mails(self):
        """ Returns a list of mails of members that have joined this auction. """

        return self.bidders.values_list('user__email', flat=True)

    def getBidNumber(self):
        return self.used_bids()/settings.TODO_BID_PRICE

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


class AuctionFixture(models.Model):
    bid_type = models.CharField(max_length=5, choices=BID_TYPE_CHOICES, default='bid')
    automatic = models.BooleanField(help_text='If selected, will be automatically run when the threshold is reached',
                                    default=True)
    threshold = models.PositiveSmallIntegerField(help_text='Amount of upcoming auctions before the fixture is run',
                                                 default=5)

    def make_auctions(self):
        auctions = []
        for template in self.templateauction_set.all():
            auctions.append(template.make_auction())
        return auctions


class TemplateAuction(AbstractAuction):
    """ Auction to be used on Fixtures. """

    fixture = models.ForeignKey(AuctionFixture)

    def make_auction(self):
        auction = Auction.objects.create(item=self.item, bid_type=self.fixture.bid_type,
                                         precap_bids=self.precap_bids,
                                         minimum_precap=self.minimum_precap)
        auction.save()
        return auction


class Bid(models.Model):
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


class AuctionInvoice(models.Model):
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


class Invitation(models.Model):
    inviter = models.ForeignKey(Member)
    invited_facebook_id = models.CharField(max_length=100)
    deleted = models.BooleanField(default=False) #facebook forced you to remove the invitation once used but not anymore


class AuctionInvitation(models.Model):
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

        if member.tokens_left >= tokens_amount:
            member.bidsto_left += num_bids
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


class FBOrderInfo(models.Model):
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
