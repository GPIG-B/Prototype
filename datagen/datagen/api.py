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
    readings = get_ns().readings_queue[0]['wts']
    IDLE_DEVICES = set(list_idle_devices())
    for turbine in readings:
        add_status(turbine, turbine["wt_id"] in IDLE_DEVICES)
    return flask.jsonify(readings)


@datagen_bp.route('/add-fault/<wt_id>', methods=['GET', 'POST'])
def add_fault(wt_id: str) -> flask.Response:
    ns = get_ns()
    if hasattr(ns, 'add_faults'):
        add_faults = ns.add_faults
    else:
        add_faults = []
    add_faults.append(wt_id)
    ns.add_faults = add_faults
    return flask.jsonify({'msg': 'success'})


@datagen_bp.route('/wind-turbines/<wt_id>', methods=['GET'])
def wind_turbines_detail(wt_id: str) -> Tuple[flask.Response, int]:
    readings = get_ns().readings_queue[-24:] # Get last 24 readings (24h if 1 tick = 1h) for historical data
    wts = readings[0]['wts']
    filtered = [wt for wt in wts if wt['wt_id'] == wt_id]
    if not filtered:
        return flask.jsonify({'msg': 'Not found'}), 404
    assert len(filtered) == 1

    turbine = filtered[0]
    add_status(turbine, is_idle_device(turbine["wt_id"]))

    rotor_rps = []
    power = []

    for reading in readings:
        wt = [wt for wt in reading['wts'] if wt['wt_id'] == wt_id][0]
        rotor_rps.append(wt['rotor_rps'])
        power.append(wt['power'])

    turbine['rotor_rps'] = rotor_rps
    turbine['power'] = power

    return flask.jsonify(turbine), 200


@datagen_bp.route('/wind-turbines/<wt_id>/disable', methods=['POST'])
def wind_turbines_disable(wt_id: str) -> Tuple[flask.Response, int]:
    readings = get_ns().readings_queue[0]['wts']
    filtered = [wt for wt in readings if wt['wt_id'] == wt_id]
    if not filtered:
        return flask.jsonify({'msg': 'Not found'}), 404
    assert len(filtered) == 1
    set_idle_device(wt_id, True)
    return flask.jsonify({'msg': 'Success'}), 200


@datagen_bp.route('/wind-turbines/<wt_id>/enable', methods=['POST'])
def wind_turbines_enable(wt_id: str) -> Tuple[flask.Response, int]:
    readings = get_ns().readings_queue[0]['wts']
    filtered = [wt for wt in readings if wt['wt_id'] == wt_id]
    if not filtered:
        return flask.jsonify({'msg': 'Not found'}), 404
    assert len(filtered) == 1
    set_idle_device(wt_id, False)
    return flask.jsonify({'msg': 'Success'}), 200


@datagen_bp.route('/env-sensors', methods=['GET'])
def env_readings() -> flask.Response:
    readings = copy(get_ns().readings_queue[0])
    del readings['wts']
    return flask.jsonify(readings)


@datagen_bp.route('/map', methods=['GET'])
def map_() -> flask.Response:
    m = get_ns().map_cfg
    drones = get_ns().drone_positions
    m['drones'] = drones
    return flask.jsonify(m)


def get_ns() -> Namespace:
    ns = flask.current_app.config['MANAGER_CLIENT'].get_ns()
    return cast(Namespace, ns)
