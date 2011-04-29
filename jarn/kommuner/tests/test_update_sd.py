# -*- coding: utf-8 -*-
from os.path import dirname, join
import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from zope.event import notify

from jarn.kommuner import tests
from jarn.kommuner.interfaces import ServiceDescriptionUpdated
from jarn.kommuner.testing import KOMMUNER_INTEGRATION_TESTING


def getFileData(filename):
    """ return a file object from the test data folder """
    filename = join(dirname(tests.__file__), 'data', filename)
    return open(filename, 'r').read()


class UpdateServiceDescriptionTest(unittest.TestCase):

    layer = KOMMUNER_INTEGRATION_TESTING

    def test_dummy_update_service_description(self):
        portal = self.layer['portal']
        folder = portal['test-folder']

        shakespeare = """
        Hamlet: Do you see yonder cloud that's almost in shape of a camel?
        Polonius: By the mass, and 'tis like a camel, indeed.
        Hamlet: Methinks it is like a weasel.
        Polonius: It is backed like a weasel.
        Hamlet: Or like a whale?
        Polonius: Very like a whale.
        -- Shakespeare
        """

        modern = """
        Hamlet: Do you see the cloud over there that's almost the shape of a camel?
        Polonius: By golly, it is like a camel, indeed.
        Hamlet: I think it looks like a weasel.
        Polonius: It is shaped like a weasel.
        Hamlet: Or like a whale?
        Polonius: It's totally like a whale.
        -- Shakespeare
        """

        trekkie = """
        Kirk: Do you see yonder cloud that's almost in shape of a Klingon?
        Spock: By the mass, and 'tis like a Klingon, indeed.
        Kirk: Methinks it is like a Vulcan.
        Spock: It is backed like a Vulcan.
        Kirk: Or like a Romulan?
        Spock: Very like a Romulan.
        -- Trekkie
        """

        final = """
        Kirk: Do you see the cloud over there that's almost the shape of a Klingon?
        Spock: By golly, it is like a Klingon, indeed.
        Kirk: I think it looks like a Vulcan.
        Spock: It is shaped like a Vulcan.
        Kirk: Or like a Romulan?
        Spock: It's totally like a Romulan.
        -- Trekkie
        """

        folder.invokeFactory('ServiceDescription', 'sd',
                             title="Foo Bar",
                             description="Some description",
                             nationalText=shakespeare,
                             text=modern)
        sd = folder['sd']
        ev = ServiceDescriptionUpdated(sd, trekkie)
        notify(ev)
        self.assertTrue('copy_of_sd' in folder.objectIds())
        copy_sd = folder['copy_of_sd']
        self.assertEqual(copy_sd.getRawText(), final)

    def test_real_update_service_description(self):
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
                             text=custom_national_text)
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
