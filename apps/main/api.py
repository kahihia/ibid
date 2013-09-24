from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from tastypie.resources import ModelResource

from bidding.models import Member
from sandbox.models import Notification


class UserNotificationsAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(to=bundle.request.user)

    def read_detail(self, object_list, bundle):
        if bundle.request.path.endswith('schema/'):
            return True
        return bundle.obj.to == bundle.request.user

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
        allowed_methods = ['get']
        #list_allowed_methods = ['get]
        #detail_allowed_methods = ['get', 'put', 'patch']
        authorization = UserNotificationsAuthorization()
        queryset = Notification.objects.exclude(status='Read').order_by('created')
        resource_name = 'notification'
