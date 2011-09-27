from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName


def losCategoriesRefs(context):
    ct = getToolByName(context, 'portal_catalog')
    return DisplayList([(brain.UID, brain.Title)
        for brain in ct.searchResults(portal_type='LOSCategory',
                                      sort_on='sortable_title')])


def serviceDescriptionRefs(context):
    ct = getToolByName(context, 'portal_catalog')
    return DisplayList([(brain.UID, brain.Title)
        for brain in ct.searchResults(portal_type='ServiceDescription',
                                      sort_on='sortable_title')])
