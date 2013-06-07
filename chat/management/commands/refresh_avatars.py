from django.core.management.base import BaseCommand, NoArgsCommand
from django.contrib.auth.models import User
from chat.models import ChatUser
from routines.templatetags.routines_tags import gravatar

#TODO remove this

class Command(BaseCommand):
    help = """Avatar urls are cached in chat user instance,
           this command refreshed cached avatars in case
           user changed his email"""

    def handle(self, *args, **options): 
        try:
            size = int(args[0])
        except IndexError:
            size = 38
        for chatuser in ChatUser.objects.all():
             try:
                 chatuser.avatar = chatuser.picture()
                 chatuser.save()
             except User.DoesNotExist:
                 chatuser.avatar = gravatar(chatuser.username+"@ibiddjango.com", size=size)
                 chatuser.save()

