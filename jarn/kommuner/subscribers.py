from Acquisition import aq_parent
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy

from jarn.kommuner.dmp import diff_match_patch


def serviceDescriptionUpdated(event):
    context = event.object
    updated_text = event.updated_text
    old_national_text = context.getRawNationalText()

    parent_folder = aq_parent(context)
    policy = ICheckinCheckoutPolicy(context)
    wc = policy.checkout(parent_folder)
    context.reindexObject('review_state')

    dmp = diff_match_patch()
    current_patch = dmp.patch_make(old_national_text, context.getRawText())
    updated_text_patch = dmp.patch_make(old_national_text, updated_text)
    final_patch = current_patch + updated_text_patch
    new_text, success = dmp.patch_apply(final_patch, old_national_text)
    if False in success:
        # XXX
        # We need to handle the possibility of patching failing
        return

    wc.setText(new_text)
