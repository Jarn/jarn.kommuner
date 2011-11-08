from persistent.list import PersistentList
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import PLONE_FIXTURE
from plone.testing import z2
#from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from Products.MailHost.MailHost import MailBase
from Products.MailHost.MailHost import _mungeHeaders
from zope.component import getSiteManager


class MockMailHost(MailBase):
    """A MailHost that collects messages instead of sending them.
    """

    def __init__(self, id):
        self.reset()

    def reset(self):
        self.messages = PersistentList()

    def _send(self, mfrom, mto, messageText, immediate=False):
        """ Send the message """
        self.messages.append(messageText)

    def send(self, messageText, mto=None, mfrom=None, subject=None,
             encode=None, immediate=False, charset=None, msg_type=None):
        messageText, mto, mfrom = _mungeHeaders(messageText,
                                                mto, mfrom, subject,
                                                charset=charset,
                                                msg_type=msg_type)
        self.messages.append(messageText)


class KommunerLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import jarn.kommuner
        import plone.app.registry
        import Products.ATBackRef
        import collective.monkeypatcher
        import plone.app.iterate

        self.loadZCML(package=collective.monkeypatcher)
        self.loadZCML(package=jarn.kommuner)
        self.loadZCML(package=plone.app.registry)
        self.loadZCML(package=Products.ATBackRef)
        self.loadZCML(package=plone.app.iterate)
        z2.installProduct(app, 'jarn.kommuner')
        z2.installProduct(app, 'Products.ATBackRef')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.ATBackRef')
        z2.uninstallProduct(app, 'jarn.kommuner')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        applyProfile(portal, 'jarn.kommuner:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'test-folder')
        setRoles(portal, TEST_USER_ID, ['Member'])

        sp = portal.portal_properties.site_properties
        sp.manage_changeProperties(title='Kommuner Site')
        # Setup mailhost
        portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        portal.manage_changeProperties(email_from_address='info@jarn.com')

KOMMUNER_FIXTURE = KommunerLayer()
KOMMUNER_INTEGRATION_TESTING = IntegrationTesting(bases=(KOMMUNER_FIXTURE, ),
    name="KommunerLayer:Integration")
KOMMUNER_FUNCTIONAL_TESTING = FunctionalTesting(bases=(KOMMUNER_FIXTURE, ),
    name="KommunerLayer:Functional")
