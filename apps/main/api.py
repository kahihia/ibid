from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource, ALL
from tastypie import fields
from datetime import datetime
from apps.main.models import Notification
from bidding.models import Member

import json
import logging
logger = logging.getLogger('django')

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
