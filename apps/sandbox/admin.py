from django.contrib import admin

from apps.sandbox.models import Audit
from apps.sandbox.models import Item
from apps.sandbox.models import User


admin.site.register(Audit)
admin.site.register(Item)
admin.site.register(User)
