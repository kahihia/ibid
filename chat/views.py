import json

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.utils.html import escape

from bidding import client
from chat.models import Message, ChatUser

from django.contrib.contenttypes.models import ContentType
auction_type_id=ContentType.objects.filter(name='auction').all()[0]

def get_chat_user(request):
    if not request.user.is_authenticated():
        raise Http404
    
    chat_user, _ = ChatUser.objects.get_or_create(object_id=request.user.id)
    return chat_user


def get_auction(request):
    auction_id = request.POST.get('auction_id')
    if auction_id:
        return auction_id
    else:
        raise Http404


def send_message(request):
    if request.POST:
        message = escape(request.POST.get('message'))
        user = get_chat_user(request)
        auction = get_auction(request)

        if user.can_chat(auction):
            db_msg = Message.objects.create(text=message, user=user,
                                             content_type=auction_type_id, object_id=auction)
            
            #do_send_message(db_msg)
            client.do_send_chat_message(auction,db_msg)
            
            return HttpResponse('{"result":true}')
        
    return HttpResponse('{"result":false}')


def do_send_message(message):
    """ Creates a message for the given action and user and sends it. """
    
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
