from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import PLONE_FIXTURE
from plone.testing import z2


class KommunerLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import jarn.kommuner
        self.loadZCML(package=jarn.kommuner)
        z2.installProduct(app, 'jarn.kommuner')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        applyProfile(portal, 'jarn.kommuner:default')
        applyProfile(portal, 'jarn.kommuner:kommunes-content')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory('Folder', 'test-folder')
        setRoles(portal, TEST_USER_ID, ['Member'])


KOMMUNER_FIXTURE = KommunerLayer()
KOMMUNER_INTEGRATION_TESTING = IntegrationTesting(bases=(KOMMUNER_FIXTURE, ),
    name="KommunerLayer:Integration")
KOMMUNER_FUNCTIONAL_TESTING = FunctionalTesting(bases=(KOMMUNER_FIXTURE, ),
    name="KommunerLayer:Functional")
