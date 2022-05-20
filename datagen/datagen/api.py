from multiprocessing.managers import Namespace
import flask
from copy import copy
from typing import cast
from flask_cors import cross_origin  # type: ignore


datagen_bp = flask.Blueprint('datagen', __name__)


@datagen_bp.route('/readings')
@cross_origin()
def readings() -> flask.Response:
    return flask.jsonify(get_ns().readings_queue)


@datagen_bp.route('/wind-turbines', methods=['GET'])
@cross_origin()
def wind_turbines_list() -> flask.Response:
    return flask.jsonify(get_ns().readings_queue[-1]['wts'])


@datagen_bp.route('/wind-turbines/<wt_id>', methods=['GET'])
@cross_origin()
def wind_turbines_detail(wt_id: str) -> flask.Response:
    readings = get_ns().readings_queue[-1]['wts']
    filtered = [wt for wt in readings if wt['wt_id'] == wt_id]
    if not filtered:
        return flask.jsonify({'msg': 'Not found'}, 404)
    assert len(filtered) == 1
    return flask.jsonify(filtered[0])


@datagen_bp.route('/env-sensors', methods=['GET'])
@cross_origin()
def env_readings() -> flask.Response:
    readings = copy(get_ns().readings_queue[-1])
    del readings['wts']
    return flask.jsonify(readings)


@datagen_bp.route('/map', methods=['GET'])
@cross_origin()
def map_() -> flask.Response:
    return flask.jsonify(get_ns().map_cfg)


def get_ns() -> Namespace:
    ns = flask.current_app.config['MANAGER_CLIENT'].get_ns()
    return cast(Namespace, ns)
