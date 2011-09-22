from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IURLNormalizer


def id_from_title(text, locale=None):
    n = getUtility(IURLNormalizer)
    if not isinstance(text, unicode):
        text = text.decode('utf-8')
    return n.normalize(text, locale=locale, max_length=100)
