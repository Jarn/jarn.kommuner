from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from zope.configuration import xmlconfig
from plone.testing import z2


class KommunerFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import jarn.kommuner
        self.loadZCML(package=jarn.kommuner)
        z2.installProduct(app, 'jarn.kommuner')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'jarn.kommuner:default')
        applyProfile(portal, 'jarn.kommuner:kommunes-content')


KOMMUNER_FIXTURE = KommunerFixture()
KOMMUNER_INTEGRATION_TESTING = IntegrationTesting(bases=(KOMMUNER_FIXTURE, ),
    name="KommunerFixture:Integration")
KOMMUNER_FUNCTIONAL_TESTING = FunctionalTesting(bases=(KOMMUNER_FIXTURE, ),
    name="KommunerFixture:Functional")
