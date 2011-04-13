from Products.Five.browser import BrowserView

from jarn.kommuner import sd_content


class ImportActiveServiceDescriptionsView(BrowserView):

    def __call__(self):
        sd_content.importActiveServiceDescriptions(self.context)


class UpdateActiveServiceDescriptionsView(BrowserView):

    def __call__(self):
        sd_content.updateActiveServiceDescriptions(self.context)
