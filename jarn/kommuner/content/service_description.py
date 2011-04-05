from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.interface import IATContentType
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.base import ATContentTypeSchema
from Products.CMFCore.permissions import View
from zope.interface import implements

from jarn.kommuner.config import PROJECTNAME
from jarn.kommuner.interfaces import IServiceDescription
from jarn.kommuner import kommunerMessageFactory as _

ServiceDescriptionSchema = ATContentTypeSchema.copy() + atapi.Schema((

    atapi.TextField('nationalText',
        required=False,
        searchable=False,
        storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup', ),
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(
                description = '',
                label = _(u'National catalog text'),
                rows = 25),
    ),
    atapi.TextField('text',
        required=False,
        searchable=False,
        storage = AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup', ),
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(
                description = '',
                label = _(u'Service description text'),
                rows = 25),
    ),

))

schemata.finalizeATCTSchema(ServiceDescriptionSchema,
                            folderish=True, moveDiscussion=False)


class ServiceDescription(ATCTContent):
    """A service description"""

    implements(IServiceDescription, IATContentType)

    meta_type = "ServiceDescription"
    portal_type = 'ServiceDescription'
    archetype_name = 'ServiceDescription'

    schema = ServiceDescriptionSchema
    security = ClassSecurityInfo()


atapi.registerType(ServiceDescription, PROJECTNAME)
