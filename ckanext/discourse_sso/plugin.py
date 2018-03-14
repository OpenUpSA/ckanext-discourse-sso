import logging
import ckan.plugins as p
from ckan.plugins.toolkit import c, redirect_to, request, config, abort, _
from base64 import b64decode, b64encode
from urlparse import parse_qs
import hashlib
import hmac
import os
from urllib import urlencode

log = logging.getLogger(__name__)

# Environment variable takes priority
sso_secret = config.get('discourse.sso.secret')
sso_secret = os.environ.get('CKAN_DISCOURSE_SSO_SECRET', sso_secret)
if sso_secret is None:
    raise Exception("Config 'discourse.sso.secret' or environment variable "
                    "CKAN_DISCOURSE_SSO_SECRET must be set")

discourse_url = config.get('discourse.url')
discourse_url = os.environ.get('CKAN_DISCOURSE_URL', sso_secret)
if sso_secret is None:
    raise Exception("Config 'discourse.url' or environment variable "
                    "CKAN_DISCOURSE_URL must be set")


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

        payload_b64 = make_payload(request, c.userobj)
        sig = sign(payload_b64)
        query_string = urlencode({
            'sso': payload_b64,
            'sig': sig,
        })

        redirect_to("https://discourse.vulekamali.gov.za?" + query_string)


def signature_is_valid(request):
    payload_b64 = request.params.get('sso')
    log.debug("Payload Base64-encoded %s", payload_b64)
    their_sig = request.params.get('sig')
    log.debug("Their signature %r", their_sig)

    log_safer_secret = "%s...hidden...%s" % (sso_secret[:3], sso_secret[-3:])
    log.debug("SSO Secret %s", log_safer_secret)

    hash = sign(payload_b64)
    our_sig = unicode(hash.hexdigest())
    log.debug("Our signature %r", our_sig)

    return hmac.compare_digest(their_sig, our_sig.hexdigest())


def make_payload(payload_b64, userobj):
    payload_b64 = request.params.get('sso')
    payload = b64decode(payload_b64)
    log.debug("Payload %s", payload)
    nonce = parse_qs(payload)['nonce'][0]
    log.debug("Nonce %s", nonce)

    return b64encode(urlencode({
        'nonce': nonce,
        'email': userobj.email,
        'external_id': userobj.id,
        'username': userobj.name,
        'name': userobj.fullname,
        'bio': userobj.about,
    }))


def sign(payload_b64):
    return hmac.new(sso_secret, payload_b64, hashlib.sha256)
