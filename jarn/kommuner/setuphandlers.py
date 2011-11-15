# -*- coding: utf-8 -*-

import os
import transaction
import xml.etree.ElementTree as ET

from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from plone.app.upgrade.utils import loadMigrationProfile
from jarn.kommuner.interfaces import ILOSWords
from jarn.kommuner.utils import id_from_title

DEFAULT_POLICIES = ('at_edit_autoversion', 'version_on_revert')
TYPES_TO_VERSION = ['ServiceDescription']


def setupCatalogUpdateUser(context):
    if context.readDataFile('catalogupdater.txt') is None:
        return
    portal = context.getSite()
    portal._addRole('CatalogUpdater')
    portal.acl_users.userFolderAddUser('updater', '2Vy8XPVj', ('CatalogUpdater',), ())


def setVersionedTypes(context):
    if context.readDataFile('versioning.txt') is None:
        return
    portal = context.getSite()
    portal_repository = getToolByName(portal, 'portal_repository')
    versionable_types = list(portal_repository.getVersionableContentTypes())

    for type_id in TYPES_TO_VERSION:
        if type_id not in versionable_types:
            # use append() to make sure we don't overwrite any
            # content-types which may already be under version control
            versionable_types.append(type_id)
            # Add default versioning policies to the versioned type
            for policy_id in DEFAULT_POLICIES:
                portal_repository.addPolicyForContentType(type_id, policy_id)
    portal_repository.setVersionableContentTypes(versionable_types)


def setupKeywords(context):
    if context.readDataFile('kommuner-keywords.txt') is None:
        return
    xml_file = os.path.join(os.path.dirname(__file__), 'data', 'los-alt.xml')
    tree = ET.parse(xml_file)
    groups = tree.findall('//emne-gruppe')
    synonym_group = groups[1]
    synonym_elements = [elem for elem in synonym_group]
    los_words = getUtility(ILOSWords)
    for elem in synonym_elements:
        los_words[elem.find('identifikator').text] = elem.find('namn').text


def setupLOSContent(context):
    if context.readDataFile('kommuner-content.txt') is None:
        return
    parents = dict()
    synonyms = dict()
    synonym_ids = dict()

    portal = context.getSite()
    wftool = getToolByName(portal, "portal_workflow")
    xml_file = os.path.join(os.path.dirname(__file__), 'data', 'los-alt.xml')
    tree = ET.parse(xml_file)

    groups = tree.findall('//emne-gruppe')
    associations = tree.findall('//assosiasjon-gruppe')
    hierarchy_associations = associations[0]
    synonym_associations = associations[1]
    topic_group = groups[0]
    topic_elements = [elem
                      for elem in topic_group
                      if elem.find('identifikator').text != "http://psi.norge.no/los/tema/temastruktur"]

    synonym_group = groups[1]
    synonym_elements = [elem for elem in synonym_group]

    for association in hierarchy_associations:
        elems = association.findall('.//medlem')
        parent_id = [elem.attrib['referanse']
                     for elem in elems
                     if elem.attrib['type'] == 'http://www.techquila.com/psi/thesaurus/#broader'][0]
        child_id = [elem.attrib['referanse']
                 for elem in elems
                 if elem.attrib['type'] == 'http://www.techquila.com/psi/thesaurus/#narrower'][0]
        if parent_id == "http://psi.norge.no/los/tema/temastruktur":
            parent_id = None
        parents[child_id] = parent_id

    for association in synonym_associations:
        elems = association.findall('.//medlem')
        topic_id = [elem.attrib['referanse']
                  for elem in elems
                  if elem.attrib['type'] == 'http://www.techquila.com/psi/thesaurus/#broader'][0]
        word_id = [elem.attrib['referanse']
                 for elem in elems
                 if elem.attrib['type'] == 'http://www.techquila.com/psi/thesaurus/#narrower'][0]

        if topic_id not in synonyms:
            synonyms[topic_id] = set()
            synonym_ids[topic_id] = set()

        for elem in synonym_elements:
            if elem.find('identifikator').text == word_id:
                synonyms[topic_id].add(unicode(elem.find('namn').text))
                synonym_ids[topic_id].add(word_id)
                break

    main_topics = []
    sub_topics = []
    for elem in topic_elements:
        topic_id = elem.find('identifikator').text
        if parents[topic_id] is None:
            main_topics.append(elem)
        else:
            sub_topics.append(elem)

    if 'tema' not in portal.objectIds():
        portal.invokeFactory('Folder', 'tema',
            title='Tema')
        tema_folder = portal['tema']
        tema_folder.unmarkCreationFlag()
        tema_folder.setExcludeFromNav(True)
        tema_folder.setLayout('tema_view')
        wftool.doActionFor(tema_folder, 'publish')
        tema_folder.reindexObject()

    tema_folder = portal['tema']

    existing = tema_folder.objectIds(['LOSCategory'])
    for topic_id in existing:
        del tema_folder[topic_id]

    for elem in main_topics:
        title = unicode(elem.find('namn').text)
        topic_id = elem.find('identifikator').text
        folder_id = tema_folder.invokeFactory('LOSCategory', id_from_title(title),
            title=title, losId=topic_id)
        folder = tema_folder[folder_id]
        folder.unmarkCreationFlag()
        wftool.doActionFor(folder, 'publish')
        folder.reindexObject()
        for subtopic in sub_topics:
            subtopic_id = subtopic.find('identifikator').text
            if parents[subtopic_id] == topic_id:
                title = unicode(subtopic.find('namn').text)
                subtopic_synonyms = []
                subtopic_synonym_ids = []
                if subtopic_id in synonyms:
                    subtopic_synonyms = synonyms[subtopic_id]
                if subtopic_id in synonym_ids:
                    subtopic_synonym_ids = synonym_ids[subtopic_id]

                subfolder_id = folder.invokeFactory('LOSCategory', id_from_title(title),
                    title=title, losId=subtopic_id, synonyms=subtopic_synonyms, synonymIds=subtopic_synonym_ids)
                subfolder = folder[subfolder_id]
                subfolder.unmarkCreationFlag()
                wftool.doActionFor(subfolder, 'publish')
                subfolder.reindexObject()


def setupLanguageFolders(context):
    if context.readDataFile('kommuner-multilang.txt') is None:
        return
    portal = context.getSite()
    setup = getToolByName(portal, 'portal_setup')
    loadMigrationProfile(portal, 'profile-Products.LinguaPlone:LinguaPlone')
    setup.runImportStepFromProfile('profile-jarn.kommuner:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-jarn.kommuner:default', 'skins')
    transaction.savepoint(True)
    setup.runImportStepFromProfile('profile-jarn.kommuner:multilang-helper', 'languagetool')
    transaction.savepoint(True)
    portal.restrictedTraverse('@@language-setup-folders')()
    transaction.savepoint(True)
    setup.runImportStepFromProfile('profile-jarn.kommuner:multilang-helper', 'viewlets')
    setup.runImportStepFromProfile('profile-jarn.kommuner:multilang-helper', 'portlets')
    portal.setLayout('uncached-language-switcher')

    langs = ['no', 'en', 'fr', 'ar', 'ru', 'tr']

    # Move content to /no folder
    ct = getToolByName(portal, 'portal_catalog')
    keep = langs
    move = ct.unrestrictedSearchResults(path={'query':portal.getId(), 'depth':1})
    move = [brain.getId for brain in move if brain.getId not in keep]
    cp = portal.manage_cutObjects(move)
    portal['no'].manage_pasteObjects(cp)

    # Make sure all objects in /no are 'no'
    def set_no(ob, path):
        getLanguage = getattr(ob, 'getLanguage', None)
        setLanguage = getattr(ob, 'setLanguage', None)
        if None not in (getLanguage, setLanguage):
            if getLanguage() != 'no':
                setLanguage('no')
                ob.reindexObject()
    portal['no'].ZopeFindAndApply(portal['no'], search_sub=True, apply_func=set_no)

    # Move portlets to /no folder
    for manager in (u'plone.leftcolumn', u'plone.rightcolumn'):
        portal_col = getUtility(IPortletManager, name=manager, context=portal)
        portal_map = getMultiAdapter((portal, portal_col), IPortletAssignmentMapping, context=portal)
        no_col = getUtility(IPortletManager, name=manager, context=portal['no'])
        no_map = getMultiAdapter((portal['no'], no_col), IPortletAssignmentMapping, context=portal['no'])

        keep = ['navigation', 'quick-upload']
        move = [x for x in portal_map if x not in keep]
        for key in move:
            no_map[key] = portal_map[key]
        for key in move:
            del portal_map[key]

    # Create default pages
    titles = {
        'no': 'Velkommen til FOOBAR kommune!',
        'en': 'Welcome to FOOBAR kommune!',
        'fr': 'Bienvenue sur FOOBAR kommune!',
        'ar': 'مرحبا بكم في FOOBAR kommune',
        'ru': 'Добро пожаловать в FOOBAR Kommune!',
        'tr': 'FOOBAR yenize hoş geldiniz!',
    }

    wf = getToolByName(portal, 'portal_workflow')
    portal['no'].invokeFactory('Document', id='landing-page', title=titles['no'])
    page = portal['no']['landing-page']
    page.unmarkCreationFlag()
    wf.doActionFor(page, 'publish')
    portal['no'].setDefaultPage('landing-page')
    portal['no'].reindexObject()

    for id in langs[1:]:
        translation = page.addTranslation(id, title=titles[id])
        translation.unmarkCreationFlag()
        wf.doActionFor(translation, 'publish')
        translation.reindexObject()
        portal[id].setDefaultPage('landing-page')
        portal[id].reindexObject()

    if 'front-page' in portal['en']:
        portal['en'].manage_delObjects('front-page')

    # Translate tema folder
    titles = {
        'no': 'Tema',
        'en': 'Services',
        'fr': 'Services',
        'ar': 'الخدمات',
        'ru': 'услуги',
        'tr': 'Hizmetleri',
    }
    tema = portal['no']['tema']
    for id in langs[1:]:
        translation = tema.addTranslation(id, title=titles[id])
        translation.unmarkCreationFlag()
        translation.setLayout('tema_sd_view')
        wf.doActionFor(translation, 'publish')
        translation.reindexObject()

    transaction.commit()

