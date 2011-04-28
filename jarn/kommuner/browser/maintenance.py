from datetime import datetime
import logging

from AccessControl.SecurityManagement import newSecurityManager
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zope.component import getUtility

from jarn.kommuner import sd_content

logger = logging.getLogger('jarn.kommuner')


def loginAsAdmin(context):
    root = context.getPhysicalRoot()
    user = root.acl_users.getUserById('admin').__of__(root.acl_users)
    newSecurityManager(None, user)


class ImportActiveServiceDescriptionsView(BrowserView):

    def __call__(self):
        sd_content.importActiveServiceDescriptions(self.context)


class UpdateActiveServiceDescriptionsView(BrowserView):

    def __call__(self):
        registry = getUtility(IRegistry)
        last_update = registry['jarn.kommuner.lastUpdate']
        now = datetime.now()
        if last_update is None:
            logger.error('Error checking for national catalog updates, please import the catalog first.')
            return
        if (now-last_update).days > 0:
            logger.info('Checking for national catalog updates')
            loginAsAdmin(self.context)
            sd_content.updateActiveServiceDescriptions(self.context)
