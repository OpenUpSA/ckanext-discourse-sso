import logging
import ckan.plugins as p
from ckan.plugins.toolkit import c, redirect_to, request, config, abort, _
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
            raise Exception('Incorrect Discourse SSO Signature to CKAN')

        redirect_to("https://discourse.vulekamali.gov.za")


def signature_is_valid(request):
    payload_b64 = request.params.get('sso')
    log.debug("Payload Base64-encoded %s", payload_b64)
    payload = b64decode(payload_b64)
    log.debug("Payload %s", payload)
    nonce = parse_qs(payload)['nonce'][0]
    log.debug("Nonce %s", nonce)
    their_sig = request.params.get('sig')
    log.debug("Their signature %r", their_sig)

    log_safer_secret = "%s...hidden...%s" % (sso_secret[:3], sso_secret[-3:])
    log.debug("SSO Secret %s", log_safer_secret)

    hash = hmac.new(sso_secret, payload_b64, hashlib.sha256)
    our_sig = unicode(hash.hexdigest())
    log.debug("Our signature %r", our_sig)

    return hmac.compare_digest(their_sig, our_sig)
