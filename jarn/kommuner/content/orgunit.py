from AccessControl import ClassSecurityInfo
from plone.app.blob.field import ImageField
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.CMFCore.permissions import View
from zope.interface import implements

from jarn.kommuner.config import PROJECTNAME
from jarn.kommuner.interfaces import IOrgUnit
from jarn.kommuner import kommunerMessageFactory as _


OrgUnitSchema = ATFolderSchema.copy() + atapi.Schema((

    atapi.TextField('unitlocation',
        required=False,
        searchable=False,
        widget = atapi.TextAreaWidget(
                description = '',
                label = _(u'Location'),
                rows = 25),
    ),

    atapi.TextField('contact',
        required=False,
        searchable=False,
        widget = atapi.TextAreaWidget(
                description = '',
                label = _(u'Contact'),
                rows = 25),
    ),

    ImageField(
        'image',
        widget=atapi.ImageWidget(label=_(u"Image")),
        validators=('isNonEmptyFile'),
        languageIndependent=True
    ),

))


schemata.finalizeATCTSchema(OrgUnitSchema,
                            folderish=True, moveDiscussion=False)


class OrgUnit(ATFolder):
    """An organization"""

    implements(IOrgUnit)

    meta_type = "OrgUnit"
    portal_type = 'OrgUnit'
    archetype_name = 'OrgUnit'

    schema = OrgUnitSchema
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

        return super(OrgUnit, self).__bobo_traverse__(REQUEST, name)

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)


atapi.registerType(OrgUnit, PROJECTNAME)
