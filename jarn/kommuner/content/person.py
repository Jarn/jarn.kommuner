"""Definition of the Person content type
"""
from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent

from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from plone.app.blob.field import ImageField
from jarn.kommuner.config import PROJECTNAME
from jarn.kommuner.interfaces import IPerson
from jarn.kommuner import kommunerMessageFactory as _


PersonSchema = ATContentTypeSchema.copy() + atapi.Schema((
    atapi.TextField('body',
              required=False,
              searchable=True,
              validators = ('isTidyHtmlWithCleanup', ),
              default_output_type = 'text/x-html-safe',
              widget = atapi.RichWidget(
                        description = '',
                        label = _(u'label_body_text', default=u'Body Text'),
                        rows = 25),
    ),

    atapi.StringField(
        'description',
        widget=atapi.StringWidget(
            label=_(u"Job title"),
            description=_(u"The position the person holds.")
        ),
        searchable=True,
        required = False
    ),
    atapi.StringField(
        'email',
        validators=('isEmail', ),
        widget=atapi.StringWidget(
            label=_(u"Email address"),
            description=_(u"Contact email address."),
        ),
        required=False,
        languageIndependent=True
    ),
    atapi.StringField(
        'phone',
        widget=atapi.StringWidget(
            label=_(u"Phone number"),
            description=_(u"Contact phone number"),
        ),
        required=False,
        languageIndependent=True
    ),
    ImageField(
        'photo',
        widget=atapi.ImageWidget(
            label=_(u"Photo"),
            description=_(u"A portrait of the person."),
        ),
        validators=('isNonEmptyFile'),
        languageIndependent=True
    ),
    atapi.StringField(
        'department',
        widget=atapi.StringWidget(
            label=_(u"Department"),
            description=''
        ),
        required = False
    ),

))

PersonSchema["title"].widget.label = _(u"Fullname")
PersonSchema["title"].languageIndependent = True

schemata.finalizeATCTSchema(PersonSchema, moveDiscussion=False)


class Person(ATCTContent):
    """A Person"""
    implements(IPerson)

    meta_type = "Person"
    schema = PersonSchema

    security = ClassSecurityInfo()

    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('photo'):
            field = self.getField('photo')
            image = None
            if name == 'photo':
                image = field.getScale(self)
            else:
                scalename = name[len('photo_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)
            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return super(Person, self).__bobo_traverse__(REQUEST, name)

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('photo').tag(self, **kwargs)

    security.declareProtected(View, 'getDepartment')
    def getDepartment(self):
        parent = aq_parent(self)
        if parent.portal_type=='OrgUnit':
            return parent

atapi.registerType(Person, PROJECTNAME)
