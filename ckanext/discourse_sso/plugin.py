import ckan.plugins as p


def custom_action():
    print "DEADBEEF"
    # ...


class DiscourseSSOPlugin(p.SingletonPlugin):

    p.implements(p.IBlueprint)

    def get_blueprint(self):
        blueprint = Blueprint('foo', self.__module__)
        rules = [
            ('/foo', 'custom_action', custom_action),
        ]
        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint
