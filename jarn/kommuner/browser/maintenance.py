from datetime import datetime
import logging

from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zope.component import getUtility

from jarn.kommuner import sd_content

logger = logging.getLogger('jarn.kommuner')


class ImportActiveServiceDescriptionsView(BrowserView):

    def __call__(self):
        sd_content.importActiveServiceDescriptions(self.context)


class UpdateActiveServiceDescriptionsView(BrowserView):

    def __call__(self):
        registry = getUtility(IRegistry)
        last_update = registry['jarn.kommuner.lastUpdate']
        now = datetime.now()
        if last_update is None:
            logger.error('Error checking for updated national catalog updates, please import them.')
            return
        if (now-last_update).days > 1:
            logger.info('Checking for updated national catalog updates')
            sd_content.updateActiveServiceDescriptions(self.context)
