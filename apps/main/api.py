from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource, ALL

from apps.main.models import Notification


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
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


class NotificationResource(ModelResource):
    class Meta:
        resource_name = 'notification'
        allowed_methods = ['get']
        #list_allowed_methods = ['get]
        #detail_allowed_methods = ['get', 'put', 'patch']
        authorization = UserNotificationsAuthorization()
        queryset = Notification.objects.order_by('created')
        filtering = {
            'status': ALL,
        }
