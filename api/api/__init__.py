import flask
import os
import logging
from multiprocessing.managers import Namespace
from typing import cast, Optional, Callable, TypeVar
from flask_cors import CORS  # type: ignore

import manager
import datagen


api_bp = flask.Blueprint('api', __name__)
logger = logging.getLogger('api')


ORIGINS = ['http://localhost:80*', '*', '34.142.109.41:80*']


@api_bp.route('/', methods=['GET'])
def index() -> flask.Response:
    routes = [str(r) for r in flask.current_app.url_map.iter_rules()]
    return flask.jsonify(msg='Running', routes=routes)

@api_bp.route('/logs')
def logs() -> flask.Response:
    ns = get_ns()
    if not hasattr(ns, 'logs'):
        return flask.jsonify([])
    logs = ns.logs
    return flask.jsonify(logs)


@api_bp.route('/drones', methods=['GET'])
def drone_positions() -> flask.Response:
    return flask.jsonify(get_ns().drone_positions)


def get_ns() -> Namespace:
    ns = flask.current_app.config['MANAGER_CLIENT'].get_ns()
    return cast(Namespace, ns)


T = TypeVar('T')


def _get_env_var(key: str, typ: Callable[[str], T]) -> T:
    if key not in os.environ:
        raise OSError(f'Environment variable not set: "{key}"')
    return typ(os.environ[key])


def dev_app(manager_client: Optional[manager.Client]) -> flask.Flask:
    logger.info('Using passed manager client')
    # instantiate the flask app
    app = flask.Flask('GPIG-api')
    CORS(app, resources={r"/*": {"origins": ORIGINS}})
    app.register_blueprint(api_bp)
    app.register_blueprint(datagen.api.datagen_bp)
    app.config['MANAGER_CLIENT'] = manager_client
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'
    return app


def deployment_app() -> flask.Flask:
    logging_cfg = _get_env_var('LOGGING_CONFIG', manager.common.existing_file)
    manager.common.init_logging(logging_cfg)
    logger.info('Attempting to construct manager client from environment '
                'variables')
    # Set up the manager client
    h = _get_env_var('MANAGER_HOST', str)
    p = _get_env_var('MANAGER_PORT', int)
    k = _get_env_var('MANAGER_AUTHKEY', str.encode)
    manager_client = manager.Client('api', h, p, k)
    logger.info('Success')
    # Initialise the app
    app = flask.Flask('GPIG-api')
    CORS(app, resources={r"/*": {"origins": ORIGINS}})
    app.register_blueprint(api_bp)
    app.register_blueprint(datagen.api.datagen_bp)
    app.config['MANAGER_CLIENT'] = manager_client
    app.config['DEBUG'] = False
    app.config['ENV'] = 'development'
    return app
