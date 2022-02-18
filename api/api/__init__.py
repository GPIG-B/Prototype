import flask
from multiprocessing.managers import Namespace
from typing import cast

import manager
import datagen


api_bp = flask.Blueprint('api', __name__)


@api_bp.route('/', methods=['GET'])
def index() -> flask.Response:
    routes = [str(r) for r in flask.current_app.url_map.iter_rules()]
    return flask.jsonify(msg='Running', routes=routes)


def get_ns() -> Namespace:
    ns = flask.current_app.config['MANAGER_CLIENT'].get_ns()
    return cast(Namespace, ns)


def build_app(manager_client: manager.Client, debug: bool = False
              ) -> flask.Flask:
    app = flask.Flask(__name__)
    app.register_blueprint(api_bp)
    app.register_blueprint(datagen.api.datagen_bp)
    app.config['MANAGER_CLIENT'] = manager_client
    app.config['DEBUG'] = debug
    return app
