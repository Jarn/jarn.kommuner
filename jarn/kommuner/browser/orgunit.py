from Products.Five.browser import BrowserView


class OrgUnitView(BrowserView):

    def persons(self):
        return self.context.listFolderContents(
            contentFilter={'portal_type': 'Person',
                           'sort_on': 'getObjPositionInParent'})

    def subunits(self):
        return self.context.listFolderContents(
            contentFilter={'portal_type': 'OrgUnit',
                           'sort_on': 'getObjPositionInParent'})
