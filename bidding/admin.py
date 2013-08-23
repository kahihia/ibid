from django.contrib import admin
#from django.contrib.auth import get_user_model
from bidding.models import Auction, PromotedAuction, PrePromotedAuction, Item, ItemImage, BidPackage, \
    ConvertHistory, FBOrderInfo, Member, ConfigKey
from django.db.models import Count
from django.contrib.auth.admin import UserAdmin
#from django.contrib.auth.models import User
#from django.conf import settings
from bidding.forms import ItemAdminForm, AuctionAdminForm, ConfigKeyAdminForm


class BidAdmin(admin.ModelAdmin):
    list_display = ('auction', 'bidder', 'unixtime')
    list_filter = ('auction', )


def winner_name(obj):
    if obj.winner:
        return " ".join([obj.winner.first_name, obj.winner.last_name])
    else:
        return "[None]"


class AuctionAdmin(admin.ModelAdmin):
    form = AuctionAdminForm

    #def queryset(self, request):
    #    qs = (self.model._default_manager.get_query_set()
    #          .extra(select={'db_address':"(SELECT street || ', ' || city || ', ' || state || ', ' || zip || ', ' || country from bidding_address where bidding_address.user_id = bidding_auction.winner_id)"}))
    #    return qs
    list_display = ('item',
                    'bid_type',
                    'status',
                    'is_active',
                    'always_alive',
                    'winner',
                    'won_price',
                    'won_date',
                    winner_name)
    readonly_fields = ("id",)
    list_filter = ('is_active', 'status')
    #raw_id_fields = ('item',)
    fieldsets = (
        (None, {
            'fields': ('item', 'bid_type', 'precap_bids', 'minimum_precap', 'is_active', 'always_alive')
        }),
        ('Bidding time', {
            'fields': ('bidding_time', 'threshold1', 'threshold2', 'threshold3',)
        }),
        ('Don\'t change', {
            'classes': ('collapse',),
            'fields': ('status',
                       'saved_time',
                       'winner',
                       'won_price',
                       'won_date',
            )
        }),
    )

    class Media:
        js = (
            'js/jquery-1.7.min.js',
            'js/jquery-ui-1.8.6.custom.min.js',
            'js/combo_box.js',
            'js/auction_admin.js')

        css = {
            'all': ('css/custom-theme/jquery-ui-1.8.6.custom.css',
                    'css/admin_fix.css',)
        }


admin.site.register(Auction, AuctionAdmin)


class PrePromotedAuctionAdmin(admin.ModelAdmin):
    form = AuctionAdminForm

    #def queryset(self, request):
    #    qs = (self.model._default_manager.get_query_set()
    #          .extra(select={'db_address':"(SELECT street || ', ' || city || ', ' || state || ', ' || zip || ', ' || country from bidding_address where bidding_address.user_id = bidding_auction.winner_id)"}))
    #    return qs
    list_display = ('item',
                    'bid_type',
                    'status',
                    'is_active',)
    list_filter = ('is_active', 'status')
    #raw_id_fields = ('item',)
    fieldsets = (
        (None, {
            'fields': ('item', 'bid_type', 'precap_bids', 'minimum_precap', 'is_active')
        }),
        ('Bidding time', {
            'fields': ('bidding_time', 'threshold1', 'threshold2', 'threshold3',)
        }),
        ('Don\'t change', {
            'classes': ('collapse',),
            'fields': ('status',
                       'saved_time',
            )
        }),
    )

    class Media:
        js = (
            'js/jquery-1.7.min.js',
            'js/jquery-ui-1.8.6.custom.min.js',
            'js/combo_box.js',
            'js/auction_admin.js')

        css = {
            'all': ('css/custom-theme/jquery-ui-1.8.6.custom.css',
                    'css/admin_fix.css',)
        }


class PromotedAuctionAdmin(admin.ModelAdmin):
    pass


admin.site.register(PrePromotedAuction, PrePromotedAuctionAdmin)
admin.site.register(PromotedAuction, PromotedAuctionAdmin)


class InlineImage(admin.TabularInline):
    model = ItemImage


def auctions(obj):
    return obj.auctions


auctions.admin_order_field = 'auctions'


def highest_won_price(obj):
    return obj.highest_price


highest_won_price.admin_order_field = 'highest_price'


def lowest_won_price(obj):
    return obj.lowest_price


lowest_won_price.admin_order_field = 'lowest_price'


def last_won_date(obj):
    return obj.last_won_date


last_won_date.admin_order_field = 'last_won_date'


class ItemAdmin(admin.ModelAdmin):
    form = ItemAdminForm

    list_display = ('name',
                    'category',
                    'retail_price',
                    'total_price',
                    auctions,
                    lowest_won_price,
                    highest_won_price,
                    last_won_date)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('name', )
    inlines = [
        InlineImage,
    ]

    def queryset(self, request):
        from django.db.models import Count, Max, Min

        qs = (self.model._default_manager.get_query_set()
              .annotate(auctions=Count('auction'))
              .annotate(highest_price=Max('auction__won_price'))
              .annotate(lowest_price=Min('auction__won_price'))
              .annotate(last_won_date=Max('auction__won_date')))
        return qs


admin.site.register(Item, ItemAdmin)


class MemberInline(admin.StackedInline):
    model = Member
    max_num = 1
    can_delete = False
    verbose_name = 'Member'
    verbose_name_plural = "Member info"

    readonly_fields = ('facebook_id', 'facebook_name', 'facebook_profile_url',)

    fieldsets = (
        (None, {
            'fields': ('bids_left', 'tokens_left', 'bidsto_left', 'remove_from_chat',)
        }),
        ('Facebook info', {
            'fields': ('facebook_id', 'facebook_name', 'facebook_profile_url', )
        }),
    )


def bids_left(obj):
    return obj.get_profile().get_bids_left()


bids_left.admin_order_field = 'bids_left'


def tokens_left(obj):
    return obj.get_profile().get_tokens_left()


def bidsto_left(obj):
    return obj.get_profile().bidsto_left


def auctions_won(obj):
    return obj.auctions_won


auctions_won.admin_order_field = 'auctions_won'


class MemberUserAdmin(UserAdmin):
    def queryset(self, request):
        qs = (self.model._default_manager.get_query_set()
              .annotate(auctions_won=Count('auction')))
        return qs

    readonly_fields = ('first_name', 'last_name', 'email',)

    list_display = ('username',
                    'first_name',
                    'last_name',
                    'email',
                    'is_staff',
                    bids_left,
                    tokens_left,
                    bidsto_left,
                    auctions_won,
    )

    inlines = [
        MemberInline,
    ]

    fieldsets = (
        (None, {'fields': ('username', 'password', 'is_active', 'is_superuser', 'is_staff')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
    )

class ConfigKeyAdmin(admin.ModelAdmin):
    form = ConfigKeyAdminForm
    
    list_display = ('key',
                    'value',
                    'description',
                    'value_type')

admin.site.register(ConfigKey, ConfigKeyAdmin)

#admin.site.unregister(User)
admin.site.register(Member, MemberUserAdmin)
admin.site.register(BidPackage)
#admin.site.register(Member)
admin.site.register(ConvertHistory)
admin.site.register(FBOrderInfo)

