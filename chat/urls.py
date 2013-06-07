from django.conf.urls.defaults import *

urlpatterns = patterns('chat.views',
    url(r'^send_message/$', 'send_message', name='chat_send_message'),
    url(r'^user_is_online/$', 'user_is_online', name='chat_user_is_online'),
)
