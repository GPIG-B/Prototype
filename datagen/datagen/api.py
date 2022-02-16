from multiprocessing.managers import Namespace
import flask
from typing import Tuple, cast

import common


datagen_bp = flask.Blueprint('datagen', __name__)


@datagen_bp.route('/readings')
def status() -> flask.Response:
    return flask.jsonify(get_ns().last_readings)


def get_ns() -> Namespace:
    return cast(Namespace, flask.g.ns)


@datagen_bp.before_request
def _load_global_ns() -> None:
    if not hasattr(flask.g, 'ns'):
        manager_addr = flask.current_app.config['MANAGER_ADDR']
        manager = common.connect_global_manager(manager_addr)
        ns = manager.get_ns()  # type: ignore
        flask.g.ns = ns


def standalone_app(manager_addr: Tuple[str, int]) -> flask.Flask:
    app = flask.Flask(__name__)
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'
    app.config['MANAGER_ADDR'] = manager_addr
    app.register_blueprint(datagen_bp)
    return app
