from multiprocessing.managers import Namespace
import flask
from typing import cast, Optional


datagen_bp = flask.Blueprint('datagen', __name__)
_cached_ns: Optional[Namespace] = None


@datagen_bp.route('/readings')
def readings() -> flask.Response:
    return flask.jsonify(get_ns().last_readings)


def get_ns() -> Namespace:
    ns = flask.current_app.config['MANAGER_CLIENT'].get_ns()
    return cast(Namespace, ns)
