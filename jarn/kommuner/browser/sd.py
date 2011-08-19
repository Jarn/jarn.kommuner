from zope.interface import implements
from plone.app.layout.globals.interfaces import IViewView
from Products.Five.browser import BrowserView


class ServiceDescriptionView(BrowserView):

    # Explicitly mark ourselves as being the "main" view.
    # This is needed as we otherwise lose the plone.contentactions viewlet
    # when a ServiceDescription is displayed "in context".
    implements(IViewView)
