from multiprocessing.managers import Namespace
from typing import Tuple
import flask
from copy import copy
from typing import cast

from .utils import is_idle_device, set_idle_device, list_idle_devices


datagen_bp = flask.Blueprint('datagen', __name__)


@datagen_bp.route('/readings')
def readings() -> flask.Response:
    return flask.jsonify(get_ns().readings_queue)


def add_status(turbine, is_idle):
    if is_idle:
        status = "idle"
    elif len(turbine["_faults"]) > 0:
        status = "warning"
    else:
        status = "running"
    turbine["status"] = status


@datagen_bp.route('/wind-turbines', methods=['GET'])
def wind_turbines_list() -> flask.Response:
    readings = get_ns().readings_queue[-1]['wts']
    IDLE_DEVICES = set(list_idle_devices())
    for turbine in readings:
        add_status(turbine, turbine["wt_id"] in IDLE_DEVICES)
    return flask.jsonify(readings)


@datagen_bp.route('/wind-turbines/<wt_id>', methods=['GET'])
def wind_turbines_detail(wt_id: str) -> Tuple[flask.Response, int]:
    readings = get_ns().readings_queue[-1]['wts']
    filtered = [wt for wt in readings if wt['wt_id'] == wt_id]
    if not filtered:
        return flask.jsonify({'msg': 'Not found'}), 404
    assert len(filtered) == 1
    turbine = filtered[0]
    add_status(turbine, is_idle_device(turbine["wt_id"]))
    return flask.jsonify(turbine), 200


@datagen_bp.route('/wind-turbines/<wt_id>/disable', methods=['POST'])
def wind_turbines_disable(wt_id: str) -> Tuple[flask.Response, int]:
    readings = get_ns().readings_queue[-1]['wts']
    filtered = [wt for wt in readings if wt['wt_id'] == wt_id]
    if not filtered:
        return flask.jsonify({'msg': 'Not found'}), 404
    assert len(filtered) == 1
    set_idle_device(wt_id, True)
    return flask.jsonify({'msg': 'Success'}), 200


@datagen_bp.route('/wind-turbines/<wt_id>/enable', methods=['POST'])
def wind_turbines_enable(wt_id: str) -> Tuple[flask.Response, int]:
    readings = get_ns().readings_queue[-1]['wts']
    filtered = [wt for wt in readings if wt['wt_id'] == wt_id]
    if not filtered:
        return flask.jsonify({'msg': 'Not found'}), 404
    assert len(filtered) == 1
    set_idle_device(wt_id, False)
    return flask.jsonify({'msg': 'Success'}), 200


@datagen_bp.route('/env-sensors', methods=['GET'])
def env_readings() -> flask.Response:
    readings = copy(get_ns().readings_queue[-1])
    del readings['wts']
    return flask.jsonify(readings)


@datagen_bp.route('/map', methods=['GET'])
def map_() -> flask.Response:
    return flask.jsonify(get_ns().map_cfg)


def get_ns() -> Namespace:
    ns = flask.current_app.config['MANAGER_CLIENT'].get_ns()
    return cast(Namespace, ns)
