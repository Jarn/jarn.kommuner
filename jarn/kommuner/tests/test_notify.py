import unittest2 as unittest

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from jarn.kommuner import sd_content
from jarn.kommuner.testing import KOMMUNER_INTEGRATION_TESTING


class NotificationTest(unittest.TestCase):

    layer = KOMMUNER_INTEGRATION_TESTING

    def test_registry_keys(self):
        registry = getUtility(IRegistry)
        self.assertTrue('jarn.kommuner.lastNotified' in registry)
        self.assertTrue('jarn.kommuner.notifyEmail' in registry)
