from plone.registry.interfaces import IRegistry
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import PLONE_FIXTURE
from plone.testing import z2
from zope.component import getUtility


class KommunerLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import jarn.kommuner
        import plone.app.registry
        self.loadZCML(package=jarn.kommuner)
        self.loadZCML(package=plone.app.registry)
        z2.installProduct(app, 'jarn.kommuner')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        applyProfile(portal, 'jarn.kommuner:default')
        #applyProfile(portal, 'jarn.kommuner:kommunes-content')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'test-folder')
        setRoles(portal, TEST_USER_ID, ['Member'])

        # XXX: This should go away. We should not store the client's password
        # in the generic package.
        registry = getUtility(IRegistry)
        registry['jarn.kommuner.katalogUserID'] = '29811'
        registry['jarn.kommuner.katalogUserPassword'] = u'ge_77_k'


KOMMUNER_FIXTURE = KommunerLayer()
KOMMUNER_INTEGRATION_TESTING = IntegrationTesting(bases=(KOMMUNER_FIXTURE, ),
    name="KommunerLayer:Integration")
KOMMUNER_FUNCTIONAL_TESTING = FunctionalTesting(bases=(KOMMUNER_FIXTURE, ),
    name="KommunerLayer:Functional")
