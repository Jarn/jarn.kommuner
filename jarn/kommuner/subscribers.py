import logging
import socket
from smtplib import SMTPException
from sys import stdin, stdout
import traceback

from Acquisition import aq_parent
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.MailHost.MailHost import MailHostError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.browser import setDefaultSkin
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.HTTPRequest import HTTPRequest
from jarn.kommuner.dmp import diff_match_patch

logger = logging.getLogger('jarn.kommuner')


def makerequest():
    environ = {}
    resp = HTTPResponse(stdout=stdout)
    environ.setdefault('SERVER_NAME', 'foo')
    environ.setdefault('SERVER_PORT', '80')
    environ.setdefault('REQUEST_METHOD', 'GET')
    req = HTTPRequest(stdin, environ, resp)
    setDefaultSkin(req)
    return req


def serviceDescriptionCreated(event):
    registry = getUtility(IRegistry)
    mail_to = registry['jarn.kommuner.notifyEmail']
    if not mail_to:
        return
    context = event.object
    request = makerequest()
    mail_template = getMultiAdapter((context, request),
                                    name='updated_sd_mail')
    mail_text = mail_template(
                         sd_title=context.Title(),
                         sd_url=context.absolute_url(),
                         charset='utf-8')

    portal_state = getMultiAdapter((context, request),
                                   name=u"plone_portal_state")
    portal = portal_state.portal()
    mail_from = portal.getProperty('email_from_address')
    mail_host = getToolByName(context, 'MailHost')

    try:
        mail_host.send(mail_text.encode('utf-8'), mto=mail_to, mfrom=mail_from,
                       subject='Service Update', charset='utf-8', msg_type=None)
    except (MailHostError, SMTPException, socket.error):
        logger.error(
            """mail error: Attempt to send mail failed.\n%s""" %
            traceback.format_exc())


def serviceDescriptionUpdated(event):
    context = event.object
    updated_text = event.updated_text
    data = event.data
    old_national_text = context.getRawNationalText().decode('utf-8')
    old_text = context.getRawText().decode('utf-8')

    parent_folder = aq_parent(context)
    policy = ICheckinCheckoutPolicy(context)
    wc = policy.checkout(parent_folder)
    context.reindexObject('review_state')

    dmp = diff_match_patch()
    current_patch = dmp.patch_make(old_national_text, old_text)
    updated_text_patch = dmp.patch_make(old_national_text, updated_text)
    final_patch = current_patch + updated_text_patch
    new_text, success = dmp.patch_apply(final_patch, old_national_text)
    if False in success:
        # XXX
        # We need to handle the possibility of patching failing
        return
    wc.setNationalText(updated_text)
    wc.setText(new_text)
    if data:
        wc.setTitle(data['title'])
        wc.setDescription(data['description'])

    logger.info("Patched Service Description %s at %s" % \
        (context.Title(), context.absolute_url()))

    # Send notification
    creator = context.Creator()
    pm = getToolByName(context, 'portal_membership')
    creator = pm.getMemberById(creator)
    mail_to = None
    if creator is not None:
        mail_to = creator.getProperty('email')
    if not mail_to:
        registry = getUtility(IRegistry)
        mail_to = registry['jarn.kommuner.notifyEmail']
    if not mail_to:
        return

    request = makerequest()
    mail_template = getMultiAdapter((context, request),
                                    name='updated_sd_mail')
    mail_text = mail_template(
                         sd_title=wc.Title(),
                         sd_url=wc.absolute_url(),
                         charset='utf-8')

    portal_state = getMultiAdapter((context, request),
                                   name=u"plone_portal_state")
    portal = portal_state.portal()
    mail_from = portal.getProperty('email_from_address')
    mail_host = getToolByName(context, 'MailHost')

    try:
        mail_host.send(mail_text.encode('utf-8'), mto=mail_to, mfrom=mail_from,
                       subject='Service Update', charset='utf-8', msg_type=None)
    except (MailHostError, SMTPException, socket.error):
        logger.error(
            """mail error: Attempt to send mail failed.\n%s""" %
            traceback.format_exc())
