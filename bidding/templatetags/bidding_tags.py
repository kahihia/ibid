from datetime import datetime
from django import template
from django.utils.safestring import mark_safe
from bidding.models import BidPackage
from django.conf import settings

register = template.Library()


@register.filter
def minutes_from_seconds(value, arg=False):
    if not value:
        value=0
    
    dt = datetime.utcfromtimestamp(value)
    
    result = [] 
    if dt.hour:
        result.append('<span class="hours">%d</span>' % dt.hour)
    if dt.minute or dt.hour:
        result.append('<span class="minutes">%02d</span>' % dt.minute)
    if not arg or dt.second:
        result.append('<span class="seconds">%02d</span>' % dt.second)
    final = ":".join(result)
    return mark_safe(final)


@register.filter
def fb_link(member, arg=False):
    link = u'<span class="fb_link"><a href="{url}" target="_blank" >{name}</a></span>'
    link = link.format(url=member.facebook_profile_url, name=member.display_name())
    return mark_safe(link)


@register.filter
def has_joined(user, auction):
    if user and user.is_authenticated():
        member = user.get_profile()
        
        return auction.has_joined(member)
    
    return False


@register.filter
def user_bids(user, auction):
    if user and user.is_authenticated():
        member = user.get_profile()
        return member.auction_bids_left(auction)
    
    return 0

@register.assignment_tag
def get_packages():
    return BidPackage.objects.all()

@register.simple_tag
def get_pubnub_sub():
    return settings.PUBNUB_SUB