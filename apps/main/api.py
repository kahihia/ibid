from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource, ALL
from datetime import datetime
from apps.main.models import Notification
import json
import logging
logger = logging.getLogger('django')

class UserNotificationsAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(recipient=bundle.request.user)

    def read_detail(self, object_list, bundle):
        if bundle.request.path.endswith('schema/'):
            return True
        return bundle.obj.recipient == bundle.request.user

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")
    
    def create_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def update_list(self, object_list, bundle):
        data = json.loads(bundle.request.body)
        #message_to_read = object_list.filter(id=data['objects'][0]['message']['id'])[0]
        #if message_to_read.recipient == bundle.request.user:
        #    message_to_read.status = 'Read'
        #    message_to_read.updated = datetime.now()
        return object_list.filter(id=data['objects'][0]['message_id'])
    
    def update_detail(self, object_list, bundle):
        return bundle.obj.recipient == bundle.request.user

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
        filtering = {
            'status': ALL,
        }
    
    def readMessage():
        return True
