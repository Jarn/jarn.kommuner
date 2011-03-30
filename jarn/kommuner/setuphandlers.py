from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType


def setupLOSContent(context):
    if context.readDataFile('content.txt') is None:
        return

    portal = context.getSite()
    existing = portal.keys()
    wftool = getToolByName(portal, "portal_workflow")
