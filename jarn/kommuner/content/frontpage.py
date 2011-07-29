"""Definition of the Frontpage content type
"""
from AccessControl import ClassSecurityInfo

from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from jarn.kommuner.config import PROJECTNAME
from jarn.kommuner.interfaces import IFrontpage


FrontpageSchema = ATContentTypeSchema.copy()

schemata.finalizeATCTSchema(FrontpageSchema)


class Frontpage(ATCTContent):
    """A Frontpage"""
    implements(IFrontpage)

    meta_type = "Frontpage"
    schema = FrontpageSchema

    security = ClassSecurityInfo()

atapi.registerType(Frontpage, PROJECTNAME)
