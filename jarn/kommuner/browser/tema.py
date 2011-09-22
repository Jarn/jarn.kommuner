from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class TemaView(BrowserView):

    def los(self):
        tema_path = '/'.join(self.context.getPhysicalPath())
        ct = getToolByName(self.context, 'portal_catalog')
        root_categories = ct.searchResults(
            portal_type='LOSCategory',
            path={'query': tema_path, 'depth':1},
            sort_on='sortable_title')
        results = []
        for brain in root_categories:
            child_categories = ct.searchResults(
                portal_type='LOSCategory',
                path={'query': brain.getPath(), 'depth':1},
                sort_on='sortable_title')
            results.append([brain, child_categories])
        return results


class TemaServiceDescriptionView(BrowserView):

    def services(self):
        tema_path = '/'.join(self.context.getPhysicalPath())
        ct = getToolByName(self.context, 'portal_catalog')
        results = ct.searchResults(
            portal_type='ServiceDescription',
            path={'query': tema_path, 'depth':1},
            sort_on='sortable_title')
        return results
