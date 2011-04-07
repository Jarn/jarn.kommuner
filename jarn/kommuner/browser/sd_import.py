from Products.Five.browser import BrowserView

from jarn.kommuner.sd_content import importActiveServiceDescriptions

class ImportActiveServiceDescriptionsView(BrowserView):

    def __call__(self):
        importActiveServiceDescriptions(self.context)
