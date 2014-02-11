from django.contrib import admin

from apps.audit.models import Log

admin.site.register(Log)


# Change the default 'Delete selected items' behaviour so the delete() method
# is executed on each object instead of the queryset, and the action is audited

def audited_delete_selected(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()
audited_delete_selected.short_description = 'Delete selected items (audited)'

admin.site.disable_action('delete_selected')
admin.site.add_action(audited_delete_selected)
