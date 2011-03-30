"""Definition of the Topic content type
"""
from zope.interface import implements
from plone.app.folder.bbb import IArchivable
from plone.app.folder.folder import IATUnifiedFolder
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.interface import IATBTreeFolder
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema

from jarn.kommuner.config import PROJECTNAME
from jarn.kommuner.interfaces import ILOSCategory
from jarn.kommuner import kommunerMessageFactory as _

LOSCategorySchema = ATFolderSchema.copy() + atapi.Schema((

    atapi.StringField("losId",
        required=False,
        languageIndependent=True,
        widget=atapi.StringWidget(label=_(u"LOS Id")),
    ),


))

schemata.finalizeATCTSchema(LOSCategorySchema,
                            folderish=True, moveDiscussion=False)


class LOSCategory(ATFolder):
    """A LOS Category"""

    implements(ILOSCategory, IATUnifiedFolder, IATBTreeFolder, IArchivable)

    meta_type = "LOSCategory"
    portal_type = 'LOSCategory'
    archetype_name = 'LOSCategory'

    schema = LOSCategorySchema


atapi.registerType(LOSCategory, PROJECTNAME)
