from multiprocessing.managers import Namespace
import flask
from typing import cast, Optional

import manager


datagen_bp = flask.Blueprint('datagen', __name__)
_cached_ns: Optional[Namespace] = None


@datagen_bp.route('/readings')
def status() -> flask.Response:
    return flask.jsonify(get_ns().last_readings)


def get_ns() -> Namespace:
    ns = flask.current_app.config['MANAGER_CLIENT'].get_ns()
    return cast(Namespace, ns)


def standalone_app(manager_client: manager.Client) -> flask.Flask:
    app = flask.Flask(__name__)
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'
    app.config['MANAGER_CLIENT'] = manager_client
    app.register_blueprint(datagen_bp)
    return app
