from zope.publisher.browser import BrowserView
from AccessControl import getSecurityManager


class FrontPageView(BrowserView):

    def canManagePortlets(self):
        sm = getSecurityManager()
        return sm.checkPermission("Portlets: Manage portlets", self.context)
