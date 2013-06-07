from django.http import Http404, HttpResponse
from chat.models import Message, ChatUser
from django.utils import simplejson as json
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from bidding.models import Auction, Member
from bidding.utils import send_stomp_message
from django.utils.html import escape
import re
from bidding import client

def get_chat_user(request):
    if not request.user.is_authenticated():
        raise Http404
    
    chat_user, _ = ChatUser.objects.get_or_create(user=request.user)
    return chat_user

def get_auction(request):
    auction_id = request.POST.get('auction_id')
    return get_object_or_404(Auction, id=int(auction_id))

def send_message(request):
    if request.POST:
        message = escape(request.POST.get('message'))
        user = get_chat_user(request)
        auction = get_auction(request)

        if user.can_chat(auction):
            db_msg = Message.objects.create(text=message, user=user,
                                             auction=auction)
            
            #do_send_message(db_msg)
            client.do_send_chat_message(auction,db_msg)
            
            return HttpResponse('{"result":true}')
        
    return HttpResponse('{"result":false}')


def do_send_message(message):
    """ Creates a message for the given action and user and sends it. """
    
    #from routines.templatetags.routines_tags import truncatechars
    #result = {'chat_message': escape(message.text),
    # We mark the message escape when getting it from user
    text = message.format_message()
    result = {'chat_message': text,
              'username':message.user.display_name(),
              'user_link' : message.user.user_link(),
              'auction': message.auction.id, 
              'time':message.get_time(), 
              'avatar':message.user.picture()}
    send_stomp_message(json.dumps(['chat', result]), '/topic/auction/' )

@login_required
def user_is_online(request):
    if request.POST and request.POST.has_key('chatroom_id'):
        chatroom = request.POST['chatroom_id']
        send_stomp_message(json.dumps(["user_online", {"user":request.user.username}]), '/topic/chatroom/%s/' % chatroom)
        return HttpResponse('{"result":true}')
    return HttpResponse('{"result":false}')
