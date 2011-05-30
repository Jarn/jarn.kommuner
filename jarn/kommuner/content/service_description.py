from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.interface import IATContentType
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.base import ATContentTypeSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

from jarn.kommuner.config import PROJECTNAME
from jarn.kommuner.interfaces import IServiceDescription
from jarn.kommuner.vocabularies import losCategoriesRefs
from jarn.kommuner import kommunerMessageFactory as _


def listPersons(context):
    ct = getToolByName(context, 'portal_catalog')
    brains = ct.searchResults(portal_type='Person')
    results = [(item.UID, item.Title, ) for item in brains]
    results.insert(0, ('', '--None--'))
    return atapi.DisplayList(results)


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
    atapi.ReferenceField(
        'los_categories',
        multiValued=True,
        allowed_types=('LOSCategory', ),
        relationship='sd_los',
        vocabulary = 'losCategoriesVocab',
        widget=atapi.ReferenceWidget(
            label=_(u"LOS categories"),
        ),
        languageIndependent=True,
        required=False,
    ),

    atapi.IntegerField(
        'serviceId',
        required=False,
        searchable=False,
        storage = AnnotationStorage(migrate=True),
        validators = ('isInt', ),
        widget = atapi.IntegerWidget(
            description = '',
            label = _(u'Service Id')),
    ),

    atapi.ReferenceField(
        'contacts',
        multiValued=True,
        allowed_types=('Person', ),
        relationship='contacts_cfp_person',
        widget=atapi.ReferenceWidget(
            label=_(u"Contact persons"),
        ),
        vocabulary='listContacts',
        languageIndependent=True,
        required=False,
    ),

))

ServiceDescriptionSchema['nationalText'].widget.visible = \
    {"edit": "invisible", "view": "visible"}
ServiceDescriptionSchema['serviceId'].widget.visible = \
    {"edit": "invisible", "view": "visible"}
schemata.finalizeATCTSchema(ServiceDescriptionSchema, moveDiscussion=False)


class ServiceDescription(ATCTContent):
    """A service description"""

    implements(IServiceDescription, IATContentType)

    meta_type = "ServiceDescription"
    portal_type = 'ServiceDescription'
    archetype_name = 'ServiceDescription'

    schema = ServiceDescriptionSchema
    security = ClassSecurityInfo()

    def losCategoriesVocab(self):
        return losCategoriesRefs(self)

    def listContacts(self):
        return listPersons(self)

atapi.registerType(ServiceDescription, PROJECTNAME)
