from AccessControl import ClassSecurityInfo
from plone.app.blob.field import ImageField
from plone.app.folder.bbb import IArchivable
from plone.app.folder.folder import IATUnifiedFolder
from Products.Archetypes import atapi
from Products.ATBackRef import backref
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.interface import IATBTreeFolder
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.CMFCore.permissions import View
from zope.interface import implements

from jarn.kommuner.config import PROJECTNAME
from jarn.kommuner.interfaces import ILOSCategory
from jarn.kommuner import kommunerMessageFactory as _


LOSCategorySchema = ATFolderSchema.copy() + atapi.Schema((

    atapi.StringField("losId",
        required=False,
        languageIndependent=True,
        #widget=atapi.StringWidget(label=_(u"LOS Id"), visible=False),
        widget=atapi.StringWidget(label=_(u"LOS Id")),
    ),
    ImageField(
        'image',
        widget=atapi.ImageWidget(label=_(u"Image")),
        validators=('isNonEmptyFile'),
        languageIndependent=True
    ),
    backref.BackReferenceField(
        'services',
        relationship='sd_los',
        multiValued=True,
        widget=backref.BackReferenceWidget(
            label=_(u"Services"),
        ),
    ),
    atapi.LinesField(
        'synonyms',
        multiValued=1,
        searchable=True,
        #widget=atapi.LinesWidget(label=_(u'Synonyms'), visible=False),
        widget=atapi.LinesWidget(label=_(u'Synonyms')),
    ),
    atapi.LinesField(
        'synonymIds',
        multiValued=1,
        searchable=False,
        #widget=atapi.LinesWidget(label=_(u'Synonym Ids'), visible=False),
        widget=atapi.LinesWidget(label=_(u'Synonym Ids')),
    ),
))
LOSCategorySchema['losId'].widget.visible = \
    {"edit": "invisible", "view": "visible"}
LOSCategorySchema['services'].widget.visible = \
    {"edit": "invisible", "view": "visible"}
LOSCategorySchema['synonyms'].widget.visible = \
    {"edit": "invisible", "view": "visible"}
LOSCategorySchema['synonymIds'].widget.visible = \
    {"edit": "invisible", "view": "visible"}

schemata.finalizeATCTSchema(LOSCategorySchema,
                            folderish=True, moveDiscussion=False)


class LOSCategory(ATFolder):
    """A LOS Category"""

    implements(ILOSCategory, IATUnifiedFolder, IATBTreeFolder, IArchivable)

    meta_type = "LOSCategory"
    portal_type = 'LOSCategory'
    archetype_name = 'LOSCategory'

    schema = LOSCategorySchema
    security = ClassSecurityInfo()

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return super(LOSCategory, self).__bobo_traverse__(REQUEST, name)

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)


atapi.registerType(LOSCategory, PROJECTNAME)
