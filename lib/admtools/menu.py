from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from admin_tools.menu import items, Menu

# to activate your custom menu add the following to your settings.py:
#
# ADMIN_TOOLS_MENU = 'lib.admtools.menu.CustomMenu'

class CustomMenu(Menu):
    """
    Custom Menu for yambidsite admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.Bookmarks(),
            items.AppList(
                _('Applications'),
                exclude_list=('django.contrib',
                              'django_facebook',
                              'registration',
                              'bidding.models.Member',
                              'chat.models.ChatUser',
                              )
            ),
            items.AppList(
                _('Administration'),
                include_list=('django.contrib',),
                exclude_list=('django.contrib.auth.models.Group',
                              'django.contrib.sites',)
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        pass
