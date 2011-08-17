# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.i18n.normalizer.interfaces import IURLNormalizer

from jarn.kommuner.utils import id_from_title
from jarn.kommuner.testing import KOMMUNER_INTEGRATION_TESTING


class URLNormalizerTest(unittest.TestCase):

    layer = KOMMUNER_INTEGRATION_TESTING

    def test_german_id(self):
        n = getUtility(IIDNormalizer)
        self.assertEqual(n.normalize(u'Schöne Mädchen muß man küssen'),
                                      'schone-madchen-muss-man-kussen')

    def test_german_url(self):
        n = getUtility(IURLNormalizer)
        self.assertEqual(n.normalize(u'Schöne Mädchen muß man küssen'),
                                      'schone-madchen-muss-man-kussen')

    def test_norwegian_id(self):
        n = getUtility(IIDNormalizer)
        self.assertEqual(n.normalize(u'Jeg kjører til Ålesund for været'),
                                      'jeg-kjorer-til-alesund-for-vaeret')

    def test_norwegian_url(self):
        n = getUtility(IURLNormalizer)
        self.assertEqual(n.normalize(u'Jeg kjører til Ålesund for været'),
                                      'jeg-kjorer-til-alesund-for-vaeret')

    # Garbage in - garbage out...

    def test_norwegian_id_utf8(self):
        n = getUtility(IIDNormalizer)
        self.assertEqual(n.normalize('Jeg kjører til Ålesund for været'),
                                     'jeg-kja-rer-til-alesund-for-va-ret')

    def test_norwegian_url_utf8(self):
        n = getUtility(IURLNormalizer)
        self.assertEqual(n.normalize('Jeg kjører til Ålesund for været'),
                                     'jeg-kja-rer-til-alesund-for-va-ret')

    # Save the day with id_from_title

    def test_norwegian_id_from_title(self):
        self.assertEqual(id_from_title(u'Jeg kjører til Ålesund for været'),
                                        'jeg-kjorer-til-alesund-for-vaeret')


    def test_norwegian_id_from_title_utf8(self):
        self.assertEqual(id_from_title('Jeg kjører til Ålesund for været'),
                                       'jeg-kjorer-til-alesund-for-vaeret')

