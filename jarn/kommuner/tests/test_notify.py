import unittest2 as unittest

from zope.component import getUtility
from jarn.kommuner.testing import KOMMUNER_INTEGRATION_TESTING


class NotificationTest(unittest.TestCase):

    layer = KOMMUNER_INTEGRATION_TESTING

    def test_registry_keys(self):
        pass