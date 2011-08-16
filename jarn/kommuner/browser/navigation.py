from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_parent
from Products.Five import BrowserView

from Products.CMFPlone import utils
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import get_view_url

from plone.app.layout.navigation.root import getNavigationRoot


class URLNavigationBreadcrumbs(BrowserView):
    """Build breadcrumbs from the URL path and let acquisition have its way."""

    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = self.context
        request = self.request
        parent = aq_parent(context)

        name, item_url = get_view_url(context)

        if parent is None:
            return ({'absolute_url': item_url,
                     'Title': utils.pretty_title_or_id(context, context), },)

        view = getMultiAdapter((parent, request), name='breadcrumbs_view')
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        if base:
            item_url = '%s/%s' % (base[-1]['absolute_url'], name)
        else:
            item_url = '%s/%s' % (parent.absolute_url(), name)

        rootPath = getNavigationRoot(context)
        itemPath = '/'.join(context.getPhysicalPath())

        # Don't show default pages in breadcrumbs or pages above the navigation root
        if not utils.isDefaultPage(context, request) and not rootPath.startswith(itemPath):
            base += ({'absolute_url': item_url,
                      'Title': utils.pretty_title_or_id(context, context), },)

        return base

