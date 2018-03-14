import logging
from flask import Blueprint
import ckan.plugins as p
import ckan.lib.helpers as h
from urllib import urlencode

from ckan.common import _, c, request, response

log = logging.getLogger(__name__)


def sso():
    if not c.user:
        log.info(request.url)
        return h.redirect_to('/user/login?' + urlencode({'came_from': request.url}))

    return h.redirect_to("https://discourse.vulekamali.gov.za")


class DiscourseSSOPlugin(p.SingletonPlugin):

    p.implements(p.IBlueprint)

    def get_blueprint(self):
        blueprint = Blueprint('discourse-sso', self.__module__)
        rules = [
            ('/discourse/sso', 'sso', sso),
        ]
        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint
