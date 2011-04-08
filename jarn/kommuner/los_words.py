from persistent.dict import PersistentDict
from zope.interface import implements

from jarn.kommuner.interfaces import ILOSWords


class LOSWords(PersistentDict):

    implements(ILOSWords)