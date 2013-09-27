from django.contrib import admin

from models import Audit
from models import Item
from models import User
from models import Notification


admin.site.register(Audit)
admin.site.register(Item)
admin.site.register(User)
admin.site.register(Notification)
