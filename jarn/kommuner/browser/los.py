from Products.Five.browser import BrowserView

class LOSView(BrowserView):

    def subcategories(self):
        return self.context.listFolderContents(
            contentFilter={'portal_type' :'LOSCategory'})

    def services(self):
        linked_services = self.context.getServices()
        contained_services = self.context.listFolderContents(
            contentFilter={'portal_type' :'ServiceDescription'})
        combined = list(set(contained_services + linked_services))
        combined.sort(key=lambda sd: sd.title)
        return combined

    def other_contents(self):
        all_content = self.context.listFolderContents()
        return list(
            set(all_content) - 
            set(self.services()).union(set(self.subcategories()))
        )