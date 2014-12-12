from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Max, Min
from bidding.forms import AuctionAdminForm
from bidding.forms import ConfigKeyAdminForm
from bidding.forms import ItemAdminForm
from bidding.forms import MemberAdminForm
from bidding.models import Auction
from bidding.models import BidPackage
from bidding.models import ConfigKey
from bidding.models import ConvertHistory
from bidding.models import FBOrderInfo
from bidding.models import IOPaymentInfo
from bidding.models import Item
from bidding.models import ItemImage
from bidding.models import Member
from bidding.models import Category
from bidding.models import PromotedAuction
from actions import export_as_csv_action




class BidAdmiA(admin.ModelAdmin):
    list_display = ('auction', 'bidder', 'unixtime')
    list_filter = ('auction', )


def winner_name(obj):
    if obj.winner:
        return " ".join([obj.winner.first_name, obj.winner.last_name])
    else:
        return "[None]"


class AuctionAdmin(admin.ModelAdmin):
    form = AuctionAdminForm
    list_display = ('item',
                    'bid_type',
                    'status',
                    'is_active',
                    'start_time',
                    'start_date',
                    'always_alive',
                    'winner',
                    'won_price',
                    'won_date',
                    winner_name,
                    'priority')
    readonly_fields = ("id",)
    list_filter = ('is_active', 'status', 'start_time', 'bid_type')
    fieldsets = (
        (None, {
            'fields': ('item', 'bid_type', 'precap_bids', 'minimum_precap', 'is_active','start_time', 'start_date','finish_time','always_alive')
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
                       'priority',
            )
        }),
    )

    class Media:
        js = (
            'admin/js/jquery-1.7.min.js',
            'admin/js/jquery-ui-1.8.6.custom.min.js',
            'admin/js/combo_box.js',
            'admin/js/auction_admin.js')

        css = {
            'all': ('admin/css/custom-theme/jquery-ui-1.8.6.custom.css',
                    'admin/css/admin_fix.css',)
        }



class PromotedAuctionAdmin(admin.ModelAdmin):
    pass


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
        qs = (self.model._default_manager.get_query_set()
              .annotate(auctions=Count('auction'))
              .annotate(highest_price=Max('auction__won_price'))
              .annotate(lowest_price=Min('auction__won_price'))
              .annotate(last_won_date=Max('auction__won_date')))
        return qs


def auctions_won(obj):
    return obj.auctions_won


auctions_won.admin_order_field = 'auctions_won'


class MemberUserAdmin(UserAdmin):
    def queryset(self, request):
        qs = (self.model._default_manager.get_query_set()
              .annotate(auctions_won=Count('auction')))
        return qs

    form = MemberAdminForm
    readonly_fields = ('first_name', 'last_name', 'email',)

    actions = [export_as_csv_action("CSV Export", fields=['first_name', 'last_name', 'email'])]

    list_display = ('username',
                    'first_name',
                    'last_name',
                    'email',
                    'is_staff',
                    'bids_left',
                    'tokens_left',
                    'bidsto_left',
                    auctions_won,
    )

    fieldsets = (
        (None, {'fields': ('username', 'password', 'is_active', 'is_superuser', 'is_staff')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Bidding', {'fields': ('bids_left', 'tokens_left', 'bidsto_left', 'remove_from_chat')}),
        )


class ConfigKeyAdmin(admin.ModelAdmin):
    form = ConfigKeyAdminForm

    list_display = ('key',
                    'value',
                    'description',
                    'value_type')


admin.site.register(Auction, AuctionAdmin)
admin.site.register(BidPackage)
admin.site.register(ConfigKey, ConfigKeyAdmin)
admin.site.register(ConvertHistory)
admin.site.register(Category)
admin.site.register(FBOrderInfo)
admin.site.register(IOPaymentInfo)
admin.site.register(Item, ItemAdmin)
admin.site.register(Member, MemberUserAdmin)
admin.site.register(PromotedAuction, PromotedAuctionAdmin)
