import suds

from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def getClient():
    registry = getUtility(IRegistry)
    url = registry['jarn.kommuner.katalogURL']
    user = registry['jarn.kommuner.katalogUserID']
    password = registry['jarn.kommuner.katalogUserPassword']
    client = suds.client.Client(url)
    client.service.autentisering(user, password)
    return client


def getServiceDescriptionOverview():
    client = getClient()
    overview = client.service.hentOversikt()
    return overview


def getServiceDescription(sd_id):
    client = getClient()
    return client.service.hentTjenestebeskrivelser(sd_id)


def getActiveServiceDescriptionsOverview():
    client = getClient()
    overview = getServiceDescriptionOverview()
    active = [item
              for item in overview
              if item['status']=="publisert" and
              item['tjenestebeskrivelseID']['variant']=="NY"]
    return active