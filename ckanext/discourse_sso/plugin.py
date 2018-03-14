import logging
import ckan.plugins as p
from ckan.plugins.toolkit import c, redirect_to, request, config
from base64 import b64decode
from urlparse import parse_qs
import hashlib
import hmac
import os

log = logging.getLogger(__name__)

# Environment variable takes priority
sso_secret = config.get('discourse.sso.secret')
sso_secret = os.environ.get('CKAN_DISCOURSE_SSO_SECRET', sso_secret)
if sso_secret is None:
    raise Exception("Config 'discourse.sso.secret' or environment variable "
                    "CKAN_DISCOURSE_SSO_SECRET must be set")


class DiscourseSSOPlugin(p.SingletonPlugin):

    p.implements(p.IRoutes, inherit=True)

    def before_map(self, map_):
        # New route to custom action
        map_.connect(
            '/discourse/sso',
            controller='ckanext.discourse_sso.plugin:SSOController',
            action='sso')

        return map_


class SSOController(p.toolkit.BaseController):

    def sso(self):
        if not c.user:
            redirect_to(controller='user',
                        action='login', came_from=request.url)

        if not signature_is_valid(request):
            (401, _('Incorrect Discourse SSO Signature to CKAN - please contact us.'))

        redirect_to("https://discourse.vulekamali.gov.za")


def signature_is_valid(request):
    payload = b64decode(request.params.get('sso'))
    nonce = parse_qs(payload)['nonce'][0]
    their_sig = request.params.get('sig')
    hash = hmac.new(sso_secret, nonce, hashlib.sha256)
    our_sig = hash.hexdigest()

    return their_sig != our_sig
