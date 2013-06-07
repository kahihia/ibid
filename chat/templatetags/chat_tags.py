from chat.models import Message, ChatUser
from django import template

register = template.Library()

@register.inclusion_tag('chat/embed_chat.html')
def embed_chat(user, auction, msg_number=3):
    if user.is_authenticated():   
        chat_user, _ = ChatUser.objects.get_or_create(user=user)
        can_chat = chat_user.can_chat(auction)
    else:
        chat_user = None
        can_chat = False
    
    messages = Message.objects.filter(auction=auction)\
                    .order_by('-created')[:msg_number]

    return {'user' : chat_user,
            'auction' : auction, 
            'messages': messages,
            'can_chat':can_chat}
    
    return {}

