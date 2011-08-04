from Acquisition import aq_parent
from AccessControl import ClassSecurityInfo
from zExceptions import Redirect
from Products.Archetypes import atapi
from Products.Archetypes.atapi import AnnotationStorage
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.interface import IATContentType
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.base import ATContentTypeSchema
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View
from zope.interface import implements

from jarn.kommuner.config import PROJECTNAME
from jarn.kommuner.interfaces import IServiceDescription
from jarn.kommuner.interfaces import ILOSCategory
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

    security.declareProtected(View, 'losCategoriesVocab')
    def losCategoriesVocab(self):
        return losCategoriesRefs(self)

    security.declareProtected(View, 'listContacts')
    def listContacts(self):
        return listPersons(self)

    security.declareProtected(View, 'inplace_url')
    def inplace_url(self):
        # Find our category. If there's more than one, pick the
        # alphabetically first.
        categories = sorted(self.getLos_categories(), key=lambda x:x.getId())
        if categories:
            # Base our URL on the category
            return '%s/%s' % (categories[0].absolute_url(), self.getId())
        # If we can't find a category, return the absolute URL.
        return self.absolute_url()

    security.declareProtected(View, 'put_in_place')
    def put_in_place(self):
        # Redirect a ServiceDescription to its "place".
        if not ILOSCategory.providedBy(aq_parent(self)):
            url = self.inplace_url()
            if url != self.absolute_url():
                raise Redirect(url)
        return ''


atapi.registerType(ServiceDescription, PROJECTNAME)
