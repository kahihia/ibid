from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource, ALL
from tastypie.utils import trailing_slash
from tastypie import fields

from apps.main.models import Notification
from bidding.models import Member

from django_facebook.connect import connect_user
from django_facebook.exceptions import MissingPermissionsError
import open_facebook

from django.conf.urls import url
from django.conf import settings

from datetime import datetime
import json

class UserNotificationsAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(recipient=bundle.request.user, status='Unread')

    def read_detail(self, object_list, bundle):
        if bundle.request.path.endswith('schema/'):
            return True
        return bundle.obj.recipient == bundle.request.user

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")
    
    def create_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def update_list(self, object_list, bundle):
        return Unauthorized("Sorry, no creates.")
    
    def update_detail(self, object_list, bundle):
        return True

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


class DummyAuthorization(Authorization):
    def read_list(self, object_list, bundle): return object_list
    def read_detail(self, object_list, bundle): return True
    def create_list(self, object_list, bundle): return object_list
    def create_detail(self, object_list, bundle): return True
    def update_list(self, object_list, bundle): return object_list
    def update_detail(self, object_list, bundle): return True
    def delete_list(self, object_list, bundle): return object_list
    def delete_detail(self, object_list, bundle): return True

class NotificationResource(ModelResource):
    
    class Meta:
        resource_name = 'notification'
        list_allowed_methods = ['get', 'put']
        detail_allowed_methods = ['get', 'put', 'patch']
        authorization = UserNotificationsAuthorization()
        queryset = Notification.objects.order_by('created')
        always_return_data = True
        filtering = {
            'status': ALL,
        }
        
    def hydrate(self, bundle):
        bundle.obj = Notification.objects.get(id=bundle.data['pk'])
        bundle.obj.status = bundle.data['objects'][0]['message']['status']
        bundle.obj.updated = datetime.now()
        return bundle

class UserDataAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        
        return object_list.filter(id=bundle.request.user.id)
    def read_detail(self, object_list, bundle):
        return True
    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")
    def create_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")
    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")
    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")
    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")
    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")
    
class UserByFBTokenResource(ModelResource):
    class Meta:
        resource_name = 'user/byFBToken'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authorization = UserDataAuthorization()
        queryset = Member.objects.all()
        detail_uri_name = 'token'
        include_resource_uri = False
        
    def prepend_urls(self):
        """
        A hook for adding your own URLs or matching before the default URLs.
        """
        return [
            url(r"^(?P<resource_name>%s)/(?P<%s>.*?)%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_detail"),
        ]
    
    def get_object_list(self, request):
        """
        A hook to allow making returning the list of available objects.

        This needs to be implemented at the user level.

        ``ModelResource`` includes a full working version specific to Django's
        ``Models``.
        """
        access_token = request.path
        access_token = access_token.replace('/api/v1/user/byFBToken/', '')
        of = open_facebook.OpenFacebook(access_token)
        db_user = Member.objects.none()
        try:
            try:
                graph = self.check_permissions(access_token)
                facebook_user = of.get('me/',)
                connect_user(request, access_token)
                db_user = Member.objects.filter(facebook_id=facebook_user['id'])
            except Exception as e:
                request.META['error'] = str(e)
        except open_facebook.exceptions.OAuthException as e:
            request.META['error'] = str(e)
        return db_user
    
    def check_permissions(self, access_token):
        graph = open_facebook.OpenFacebook(access_token)
        permissions = set(graph.permissions())
        scope_list = set(settings.FACEBOOK_DEFAULT_SCOPE)
        missing_perms = scope_list - permissions
        if missing_perms:
            permissions_string = ', '.join(missing_perms)
            error_format = 'Permissions Missing: %s'
            raise MissingPermissionsError(error_format % permissions_string)
        return graph

    def alter_list_data_to_serialize(self, request, data):
        """
        A hook to alter list data just before it gets serialized & sent to the user.

        Useful for restructuring/renaming aspects of the what's going to be
        sent.

        Should accommodate for a list of objects, generally also including
        meta data.
        """
        try:
            if request.META['error']:
                data['error'] = request.META['error']
        except Exception:
            data['error'] = 'none'
        return data
    