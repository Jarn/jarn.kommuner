# -*- coding: utf-8 -*-
from os.path import dirname, join
import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.event import notify

from jarn.kommuner import tests
from jarn.kommuner.interfaces import ServiceDescriptionCreated
from jarn.kommuner.interfaces import ServiceDescriptionUpdated
from jarn.kommuner.testing import KOMMUNER_INTEGRATION_TESTING


def getFileData(filename):
    """ return a file object from the test data folder """
    filename = join(dirname(tests.__file__), 'data', filename)
    return open(filename, 'r').read()


class ServiceDescriptionSubscriberTest(unittest.TestCase):

    layer = KOMMUNER_INTEGRATION_TESTING

    def test_update_service_description(self):
        """ The data used here are real. They come from:
        {'sprak': 'no', 'versjon': 2, 'land': 'NO', 'variant': None, 'tjenesteID': 114}
        {'sprak': 'no', 'versjon': 1, 'land': 'NO', 'variant': None, 'tjenesteID': 114}
        """
        portal = self.layer['portal']
        folder = portal['test-folder']
        old_national_text = getFileData('114-ver-1.html')
        custom_national_text = getFileData('114-ver-1-custom.html')
        new_national_text = getFileData('114-ver-2.html').decode('utf-8')
        folder.invokeFactory('ServiceDescription', 'sd',
                             title="Test SD",
                             nationalText=old_national_text,
                             text=custom_national_text,
                             creators=['test_user_1_'])
        sd = folder['sd']

        # Set an email for test_user_1_ so that he receives a notification
        mt = getToolByName(portal, 'portal_membership')
        member = mt.getAuthenticatedMember()
        member.setMemberProperties(
            {'fullname': 'Bob Døe', 'email': 'bobdoe@jarn.com'})
        ev = ServiceDescriptionUpdated(sd, new_national_text)
        notify(ev)
        self.assertTrue('copy_of_sd' in folder.objectIds())
        copy_sd = folder['copy_of_sd']
        self.assertEqual(copy_sd.getRawText(), getFileData('114-ver-2-custom.html'))
        self.assertEqual(len(portal.MailHost.messages), 1)
        message = portal.MailHost.messages[0]
        self.assertTrue('To: bobdoe@jarn.com' in message)
        self.assertTrue('From: info@jarn.com' in message)
        self.assertTrue('Test SD' in message)
        self.assertTrue('http://nohost/plone/test-folder/copy_of_sd' in message)
        self.assertTrue('Kommuner Site' in message)

    def test_create_service_description(self):
        portal = self.layer['portal']
        folder = portal['test-folder']
        old_national_text = getFileData('114-ver-1.html')
        custom_national_text = getFileData('114-ver-1-custom.html')
        folder.invokeFactory('ServiceDescription', 'sd',
                             title="Test SD",
                             nationalText=old_national_text,
                             text=custom_national_text,
                             creators=['test_user_1_'])
        sd = folder['sd']
        # Set an email for the generic email catcher
        registry = getUtility(IRegistry)
        registry['jarn.kommuner.notifyEmail'] = 'foo@jarn.com'
        ev = ServiceDescriptionCreated(sd)
        notify(ev)
        self.assertEqual(len(portal.MailHost.messages), 1)
        message = portal.MailHost.messages[0]
        self.assertTrue('To: foo@jarn.com' in message)
        self.assertTrue('From: info@jarn.com' in message)
        self.assertTrue('Test SD' in message)
        self.assertTrue('http://nohost/plone/test-folder/sd' in message)
        self.assertTrue('Kommuner Site' in message)
