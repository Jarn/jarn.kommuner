from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.browser.switcher import LanguageSwitcher


class UncachedLanguageSwitcher(LanguageSwitcher):

    def __call__(self):
        """Redirect to the preferred language top-level folder.

        Always prefer the language cookie if it is set.
        If no folder for preferred language exists, redirect to default
        language.
        """
        context = aq_inner(self.context)
        plt = getToolByName(context, 'portal_languages')

        # Explicitly check the language cookie
        langCookie = self.request.cookies.get('I18N_LANGUAGE')
        if langCookie:
            pref = langCookie
        else:
            pref = plt.getPreferredLanguage()

        default = plt.getDefaultLanguage()
        ids = self.context.keys()
        target = (pref in ids) and pref or default
        url = "%s/%s" % (context.absolute_url(), target)

        # We need to set the language cookie on the first response or it will
        # be set on the frontpage itself, making it uncachable
        if not langCookie or langCookie != target:
            self.request.response.setCookie('I18N_LANGUAGE', target, path='/')

        # Disallow caching of the redirect
        self.request.response.setHeader('Cache-Control', 'no-cache')
        self.request.response.redirect(url, status=301)
