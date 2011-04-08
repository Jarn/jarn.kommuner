from zope.component.interfaces import IObjectEvent
from zope.interface import Interface


class ILOSCategory(Interface):
    pass


class ILOSWords(Interface):
    pass


class IServiceDescription(Interface):
    pass


class IServiceDescriptionUpdated(IObjectEvent):
    """Reactor has been stoped.
    """
    pass


class ServiceDescriptionUpdated(object):

    def __init__(self, obj, updated_text):
        self.object = obj
        self.updated_text = updated_text