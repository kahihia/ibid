from django.utils.translation import ugettext_lazy as _
from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard

# to activate your index dashboard add the following to your settings.py:
#
# ADMIN_TOOLS_INDEX_DASHBOARD = 'yambidsite.dashboard.CustomIndexDashboard'

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for yambidsite.
    """
    def __init__(self, **kwargs):
        Dashboard.__init__(self, **kwargs)

        # append an app list module for "Administration"
        self.children.append(modules.ModelList(
            title=_('Administration'),
            include_list=('django.contrib.auth.models.User',
                          'django.contrib.flatpages.models.FlatPage'),
        ))

        self.children.append(modules.ModelList(
            title=_('Bidding'),
            models=[
                'bidding.models.Auction',
                'bidding.models.Item',
                'bidding.models.AuctionFixture',
                'bidding.models.BidPackage',
                'bidding.models.ConvertHistory',
                'bidding.models.FBOrderInfo',
                'bidding.models.ConfigKey',
            ]
        ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            title=_('Applications'),
            exclude_list=('django.contrib',
                          'bidding',
                          'django_facebook',
                          'registration',
                          'chat.models.ChatUser'),
        ))


    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        pass


# to activate your app index dashboard add the following to your settings.py:
#
# ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'yambidsite.dashboard.CustomAppIndexDashboard'

class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for yambidsite.
    """
    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # we disable title because its redundant with the model list module
        self.title = ''

        # append a model list module
        self.children.append(modules.ModelList(
            title=self.app_title,
            include_list=self.models,
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(
            title=_('Recent Actions'),
            include_list=self.get_app_content_types(),
        ))

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        pass
