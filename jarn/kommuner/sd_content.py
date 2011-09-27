import logging
import re, htmlentitydefs
from datetime import datetime

from Acquisition import aq_parent
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.event import notify

from jarn.kommuner import sd_client
from jarn.kommuner.utils import id_from_title
from jarn.kommuner.interfaces import ILOSWords
from jarn.kommuner.interfaces import ServiceDescriptionUpdated
from jarn.kommuner.interfaces import ServiceDescriptionCreated

logger = logging.getLogger('jarn.kommuner')


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    if text:
        return re.sub("&#?\w+;", fixup, text)
    else:
        return ''

def unparagraph(text):
    match = re.match("<p>(.*?)</p>", text)
    if match is None:
        return text
    return match.group(1)


def getServiceDescriptionData(context, sd_id):
    ct = context.portal_catalog
    los_words = getUtility(ILOSWords)

    sd = sd_client.getServiceDescription(sd_id)

    title = sd['navn'].encode('utf-8')

    description = unparagraph(unescape(sd['ingress'])).encode('utf-8') if 'ingress' in sd else ''

    general = {
        'htmlDescription': unescape(sd['beskrivelse']).encode('utf-8'),
        'targetGroup': unescape(sd['malgruppe']).encode('utf-8'),
        'criteria':  unescape(sd['kriterier']).encode('utf-8'),
        'price': unescape(sd['pris']).encode('utf-8'),
        'partners': unescape(sd['partnere']).encode('utf-8'),
        'brochures': unescape(sd['brosjyrer']).encode('utf-8'),
    }

    application = {
        'guidelines': unescape(sd['soknadVeiledning']).encode('utf-8'),
        'attachment': unescape(sd['soknadVedlegg']).encode('utf-8'),
        'form': unescape(sd['soknadSkjema']).encode('utf-8'),
        'recipient': unescape(sd['soknadMottaker']).encode('utf-8'),
        'notes': unescape(sd['soknadMerknader']).encode('utf-8'),
        'complaint': unescape(sd['soknadKlage']).encode('utf-8'),
        'deadline': unescape(sd['soknadFrist']).encode('utf-8'),
        'duration': unescape(sd['soknadBehandlingstid']).encode('utf-8'),
        'processing': unescape(sd['soknadBehandling']).encode('utf-8'),
    }

    laws = []
    if 'dokumentRef' in sd:
        doc_refs = sd['dokumentRef']
        for doc_ref in doc_refs:
            if doc_ref['dokumenttypeID'] in [1,2,3,8]:
                ref = {
                    'title': doc_ref['tittel'].encode('utf-8'),
                    'url': doc_ref['uri'],
                    'description': doc_ref['beskrivelse'] if 'beskrivelse' in doc_ref else ''
                }
                laws.append(ref)

    other = {
        'updated': sd['datoOppdatert'],
        'valid_from': sd['gyldigFra'] if 'gyldigFra' in sd else '',
        'state': sd['livsITRefs'] if 'livsITRefs' in sd else []
    }

    normalized_word_ids = [ref['psi'].replace('emneord', 'ord') for ref in sd['emneordRefs']] \
        if 'emneordRefs' in sd else []
    topic_refs = ct.searchResults(synonymIds={'query': normalized_word_ids, 'operator': 'or'})
    keywords = [los_words[word_id] for word_id in normalized_word_ids if word_id in los_words]

    return {
        'title': title,
        'description': description,
        'general': general,
        'application': application,
        'laws': laws,
        'other': other,
        'topic_refs': topic_refs,
        'keywords': keywords
    }


def linkTranslation(translation, serviceId):
    ct = getToolByName(translation, 'portal_catalog')
    canonical = ct.unrestrictedSearchResults(serviceId=serviceId, Language='no')
    translation.addTranslationReference(canonical[0].getObject())


def importActiveServiceDescriptions(context):
    lang = context.Language() or 'no'
    ct = getToolByName(context, 'portal_catalog')
    existing = ct.unrestrictedSearchResults(portal_type='ServiceDescription', Language=lang)
    for brain in list(existing):
        obj = brain.getObject()
        parent = aq_parent(obj)
        del parent[obj.getId()]

    active_sd_ids = [sd['tjenestebeskrivelseID']
                     for sd in sd_client.getActiveServiceDescriptionsOverview(lang=lang)]
    pu = getToolByName(context, 'plone_utils')
    for sd_id in active_sd_ids:
        internal_id = sd_id['tjenesteID']
        data = getServiceDescriptionData(context, sd_id)
        text = context.restrictedTraverse('@@sd-template')(data=data)
        los_categories = [brain.getObject() for brain in data['topic_refs']]
        logger.info("Creating service description '%s'" % data['title'])
        new_id = context.invokeFactory('ServiceDescription', id_from_title(data['title'], locale=lang),
            serviceId=internal_id, title=data['title'], description=data['description'],
            nationalText=text, text=text, los_categories=los_categories, subject=data['keywords'],
            language=lang)
        context[new_id].unmarkCreationFlag()
        if lang != 'no':
            linkTranslation(context[new_id], internal_id)
        pu.changeOwnershipOf(context[new_id], 'updater')
        context[new_id].reindexObject()
    registry = getUtility(IRegistry)

    # XXX: Should store time per language
    if lang == 'no':
        registry['jarn.kommuner.lastUpdate'] = datetime.now()

    logger.info('done')


def updateActiveServiceDescriptions(context):
    lang = context.Language() or 'no'
    ct = getToolByName(context, 'portal_catalog')
    registry = getUtility(IRegistry)
    last_update = registry['jarn.kommuner.lastUpdate']

    # XXX: Should store time per language
    if lang == 'no':
        registry['jarn.kommuner.lastUpdate'] = datetime.now()

    updated_ids = [sd['tjenestebeskrivelseID']
                   for sd in sd_client.getUpdatedServiceDescriptions(last_update, lang=lang)]
    pu = getToolByName(context, 'plone_utils')
    for sd_id in updated_ids:
        data = getServiceDescriptionData(context, sd_id)
        text = context.restrictedTraverse('@@sd-template')(data=data)
        los_categories = [brain.getObject() for brain in data['topic_refs']]

        sd = ct.unrestrictedSearchResults(serviceId=sd_id['tjenesteID'], Language=lang)

        if not sd:
            internal_id = sd_id['tjenesteID']
            logger.info("Creating service description '%s'" % data['title'])
            new_id = context.invokeFactory('ServiceDescription', id_from_title(data['title'], locale=lang),
                serviceId=internal_id, title=data['title'], description=data['description'],
                nationalText=text, text=text, los_categories=los_categories, subject=data['keywords'],
                language=lang)
            context[new_id].unmarkCreationFlag()
            if lang != 'no':
                linkTranslation(context[new_id], internal_id)
            pu.changeOwnershipOf(context[new_id], 'updater')
            context[new_id].reindexObject()
            ev = ServiceDescriptionCreated(context[context_id])
            notify(ev)
        else:
            sd = sd[0].getObject()
            logger.info("Updating service description '%s'" % data['title'])
            ev = ServiceDescriptionUpdated(sd, text, data)
            notify(ev)
