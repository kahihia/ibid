from django import template
from datetime import datetime
from django.utils.safestring import mark_safe

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

@register.inclusion_tag('bidding/winners_widget.html')
def winners_widget(user=None):
    from bidding.models import Auction
    auctions = (Auction.objects.filter(is_active=True, 
                                       status__in=('waiting_payment', 'paid'))
                                       .order_by('-won_date')[:5])
    return {'auctions':auctions, 'user':user}

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
