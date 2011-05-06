# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.event import notify

from jarn.kommuner.interfaces import ServiceDescriptionUpdated
from jarn.kommuner.testing import KOMMUNER_INTEGRATION_TESTING


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
