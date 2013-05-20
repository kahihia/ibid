'''
Registration backend to use with django-facebook connect, 
instead of the default from django-registration.
'''
from django.contrib.auth.models import User
from registration.forms import RegistrationForm
from bidding.models import Member
from django_facebook.auth_backends import FacebookBackend
import open_facebook

import logging

logger = logging.getLogger(__name__)

class YambidRegistration(object):
    def register(self, request, **kwargs):
        username, email, password = kwargs['username'], kwargs['email'], kwargs['password1']
        
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = True
        new_user.save()
        
        profile = Member()
        profile.user = new_user
        profile.save()
        
        return new_user

    def activate(self, request, activation_key):
        raise NotImplementedError

    def registration_allowed(self, request):
        return True

    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        
        """
        return RegistrationForm

    def post_registration_redirect(self, request, user):
                return ('bidding_home', (), {})

    def post_activation_redirect(self, request, user):
        raise NotImplementedError


class YambidAuthBacked(FacebookBackend):
    """ Performs extra tasks when logging in from Facebook. """
    
    def authenticate(self, facebook_id=None, facebook_email=None):
        user = super(YambidAuthBacked, self).authenticate(facebook_id, facebook_email)
        
        if user:
            #Sets profile pic for the session
            member = user.get_profile()
            of = open_facebook.OpenFacebook(member.access_token)
            member.profile_pic = of.my_image_url(size='square')
            logger.info(of.me())
            member.save()
        
        return user
    
    
    