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
    sd = client.service.hentTjenestebeskrivelser(sd_id)
    if sd:
        return sd[0]


def _getActiveServiceDescriptionsOverview():
    overview = getServiceDescriptionOverview()
    active = [item
              for item in overview
              if item['status'] == "publisert"]
    return active


def getActiveServiceDescriptionsOverview(lang='no', country=None, variant=None):
    active = _getActiveServiceDescriptionsOverview()
    if lang == 'no':
        country = 'NO'

    lang_specific = [item
        for item in active
        if item['tjenestebeskrivelseID']['land'] == country and
        item['tjenestebeskrivelseID']['sprak'] == lang and
        item['tjenestebeskrivelseID']['variant'] == variant]
    return lang_specific


def _getUpdatedServiceDescriptions(since):
    client = getClient()
    updated = client.service.hentOversiktEndringer(since)
    return [item
            for item in updated
            if item['status'] == "publisert"]


def getUpdatedServiceDescriptions(since, lang='no', country=None, variant=None):
    all_lang = _getUpdatedServiceDescriptions(since)
    if lang == 'no':
        country = 'NO'

    lang_specific = [item
        for item in all_lang
        if item['tjenestebeskrivelseID']['land'] == country and
        item['tjenestebeskrivelseID']['sprak'] == lang and
        item['tjenestebeskrivelseID']['variant'] == variant]
    return lang_specific


def getLOSText(psi):
    # XXX: Not working
    # Throws:
    # WebFault: Server raised fault: 'com.mysql.jdbc.exceptions.jdbc4.MySQLSyntaxErrorException: Unknown column 'LT.oppdatert' in 'field list''
    client = getClient()
    return client.service.hentLostekst(psi)
