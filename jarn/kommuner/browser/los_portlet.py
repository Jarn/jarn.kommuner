from Acquisition import aq_inner
from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

from jarn.kommuner import kommunerMessageFactory as _


class ILOSPortlet(IPortletDataProvider):
    """A portlet to render open calls for proposal
    """


class Assignment(base.Assignment):
    implements(ILOSPortlet)

    title = _(u'LOS portlet')


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('los_portlet.pt')

    def render(self):
        return xhtml_compress(self._template())

    def LOS(self):
        context = aq_inner(self.context)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        if 'tema' not in portal:
            return []
        tema = portal['tema']
        tema_path = '/'.join(tema.getPhysicalPath())
        ct = getToolByName(context, 'portal_catalog')
        return ct.searchResults(
            portal_type='LOSCategory',
            path={'query': tema_path, 'depth':1},
            sort_on='sortable_title')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
