from plone.app.iterate.interfaces import IWorkingCopy
from Products.Five.browser import BrowserView


class IsWorkingCopyView(BrowserView):

    def __call__(self):
        return IWorkingCopy.providedBy(self.context)
