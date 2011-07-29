from plone.app.portlets.interfaces import IColumn
from zope.component.interfaces import IObjectEvent
from zope.interface import Interface


class ILOSCategory(Interface):
    pass


class ILOSWords(Interface):
    pass


class IServiceDescription(Interface):
    pass


class IPerson(Interface):
    pass


class IFrontpage(Interface):
    pass


class IFrontpagePortletManagers(IColumn):
    """ General interface for portlet managers on the Frontpage View.
    """


class IServiceDescriptionCreated(IObjectEvent):
    """Fired when a service description has been created.
    """


class IServiceDescriptionUpdated(IObjectEvent):
    """Fired when a service description has changed.
    """


class ServiceDescriptionUpdated(object):

    def __init__(self, obj, updated_text, data={}):
        self.object = obj
        self.updated_text = updated_text
        self.data = data


class ServiceDescriptionCreated(object):

    def __init__(self, obj):
        self.object = obj
