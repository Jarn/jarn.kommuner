import datetime
import suds
import unittest2 as unittest

from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from jarn.kommuner import sd_client
from jarn.kommuner.testing import KOMMUNER_INTEGRATION_TESTING


class UpdateServiceDescriptionTest(unittest.TestCase):

    layer = KOMMUNER_INTEGRATION_TESTING

    def test_registry_entries(self):
        registry = getUtility(IRegistry)
        self.assertTrue('jarn.kommuner.katalogURL' in registry)
        self.assertTrue('jarn.kommuner.katalogUserID' in registry)
        self.assertTrue('jarn.kommuner.katalogUserPassword' in registry)
        self.assertTrue('jarn.kommuner.lastUpdate' in registry)

    def test_client(self):
        client = sd_client.getClient()
        self.assertTrue(client.sd)

    def test_sd_overview(self):
        overview = sd_client.getServiceDescriptionOverview()
        self.assertTrue(overview)
        sd = overview[0]
        self.assertTrue('navn' in sd)
        self.assertTrue('status' in sd)
        self.assertTrue('endret' in sd)
        self.assertTrue('revisjon' in sd)
        self.assertTrue('tjenestebeskrivelseID' in sd)

    def test_get_sd_norwegian(self):
        sd_id = {'land': 'NO', 'sprak': 'no', 'tjenesteID': 93156, 'variant': None, 'versjon': 2}
        sd = sd_client.getServiceDescription(sd_id)
        self.assertTrue(sd)
        attributes = ['navn', 'beskrivelse', 'malgruppe', 'kriterier',
                      'partnere', 'pris', 'brosjyrer', 'beslektedeTjenester',
                      'lover', 'internSaksgang', 'soknadVeiledning',
                      'soknadVedlegg', 'soknadSkjema', 'soknadMottaker',
                      'soknadMerknader', 'soknadKlage', 'soknadFrist',
                      'soknadBehandlingstid', 'soknadBehandling',
                      'servicevilkar', 'internOpplysninger']
        self.assertTrue(set(attributes).issubset(set(dir(sd))))

    def test_get_sd_english(self):
        sd_id = {'land': None, 'sprak': 'en', 'tjenesteID': 93156, 'variant': None, 'versjon': 1}
        sd = sd_client.getServiceDescription(sd_id)
        self.assertTrue(sd)
        attributes = ['navn', 'beskrivelse', 'malgruppe', 'kriterier',
                      'partnere', 'pris', 'brosjyrer', 'beslektedeTjenester',
                      'lover', 'internSaksgang', 'soknadVeiledning',
                      'soknadVedlegg', 'soknadSkjema', 'soknadMottaker',
                      'soknadMerknader', 'soknadKlage', 'soknadFrist',
                      'soknadBehandlingstid', 'soknadBehandling',
                      'servicevilkar', 'internOpplysninger']
        self.assertTrue(set(attributes).issubset(set(dir(sd))))

    def test_get_active_sd_norwegian(self):
        active = sd_client.getActiveServiceDescriptionsOverview()
        active_ids = [x['tjenestebeskrivelseID']['tjenesteID'] for x in active]
        self.assertEqual(len(active_ids), len(set(active_ids)))

    def test_get_active_sd_english(self):
        active = sd_client.getActiveServiceDescriptionsOverview(lang='en')
        active_ids = [x['tjenestebeskrivelseID']['tjenesteID'] for x in active]
        self.assertEqual(len(active_ids), len(set(active_ids)))

    def test_get_updated_sds_norwegian(self):
        since = datetime.datetime(2011, 1, 1)
        updated = sd_client.getUpdatedServiceDescriptions(since)
        self.assertTrue(len(updated) > 0)
        updated_ids = [x['tjenestebeskrivelseID']['tjenesteID'] for x in updated]
        self.assertEqual(len(updated_ids), len(set(updated_ids)))

    def test_get_updated_sds_english(self):
        since = datetime.datetime(2011, 1, 1)
        updated = sd_client.getUpdatedServiceDescriptions(since, lang='en')
        self.assertTrue(len(updated) > 0)
        updated_ids = [x['tjenestebeskrivelseID']['tjenesteID'] for x in updated]
        self.assertEqual(len(updated_ids), len(set(updated_ids)))

    def test_get_los_text(self):
        self.assertRaises(suds.WebFault,
            sd_client.getLOSText, u'http://psi.norge.no/los/ord/alkoholsalg')
