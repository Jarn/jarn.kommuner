import unittest2 as unittest

from jarn.kommuner.testing import KOMMUNER_INTEGRATION_TESTING


class UpdateServiceDescriptionTest(unittest.TestCase):

    layer = KOMMUNER_INTEGRATION_TESTING

    def test_1(self):
        self.assertEqual(1,1)
