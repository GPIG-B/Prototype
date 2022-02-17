#!/usr/bin/env python3
import argparse
import random
import logging
import sys
import json
from pathlib import Path
from typing import Optional

import datagen as dg
import manager


LOG_LEVELS = {1: logging.INFO, 2: logging.WARNING, 3: logging.ERROR}
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


def _existing_file(p: str) -> Path:
    path = Path(p)
    if not path.exists():
        raise FileNotFoundError(f'File does not exist: {p}')
    return path


def find_config() -> Optional[Path]:
    str_paths = ['./configs/datagen.yaml', '../configs/datagen.yaml']
    for str_path in str_paths:
        path = Path(str_path)
        if path.exists():
            return path
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    msg = 'Seed of the random number generator'
    parser.add_argument('--seed', type=int, default=None, help=msg)
    parser.add_argument('--quiet', '-q', help='Quiet mode (additive)',
                        action='count', default=1)
    parser.add_argument('--logfile', '-log', type=Path, default=None)
    # Parser for simulations
    sim_parser = argparse.ArgumentParser(add_help=False)
    sim_parser.add_argument('--config', type=_existing_file,
                            default=find_config(),
                            help='The config file containing the simulation '
                                 'constants')
    sim_parser.add_argument('--warmup', type=int, default=10,
                            help='Number of ticks to "warm up" the simulation '
                                 'after initialisation')
    # Parser for the global state manager
    gsm_parser = argparse.ArgumentParser(add_help=False)
    manager.add_manager_arguments(gsm_parser)
    # JSON action
    p = subparsers.add_parser('json', parents=[sim_parser])
    p.add_argument('--ticks', type=int, default=10,
                   help='The number of ticks (timesteps) to simulate')
    p.set_defaults(func=json_action)
    # API action
    p = subparsers.add_parser('api', parents=[gsm_parser])
    p.add_argument('--host', type=str, default='127.0.0.1')
    p.add_argument('--port', '-p', type=int, default=8080)
    p.set_defaults(func=api_action)
    # SIM action
    p = subparsers.add_parser('sim', parents=[sim_parser, gsm_parser])
    p.set_defaults(func=sim_action)
    # Parse arguments
    args = parser.parse_args()
    # Check that a config exists
    if hasattr(args, 'config') and args.config is None:
        print('No config found or specified')
        exit(1)
    # Check if an action was specified
    if not hasattr(args, 'func'):
        print('No action specified')
        parser.print_usage()
        exit(1)
    m = '--ticks must be greater than 0, got %d'
    assert getattr(args, 'ticks', 1) > 0, m % args.ticks
    # Logging config
    if args.logfile is not None:
        args.logfile.parent.mkdir(parents=True, exist_ok=True)
        args.logfile.touch()
    logging.basicConfig(
            format=LOG_FORMAT,
            level=LOG_LEVELS[args.quiet],
            filename=args.logfile)
    # RNG seed
    if args.seed is not None:
        random.seed(args.seed)
    # Perform the specified action
    args.func(args)


def _build_sim(args: argparse.Namespace) -> dg.types.Simulation:
    cfg = dg.config.Config.from_yaml(args.config)
    env = dg.types.Environment.from_config(cfg)
    wts = [dg.types.WindTurbine.from_env(env)
           for _ in range(cfg.wts)]
    sim = dg.types.Simulation(cfg, wts, env)
    logging.info('Starting warmup')
    sim.tick(args.warmup)
    logging.info('Done')
    return sim


def json_action(args: argparse.Namespace) -> None:
    sim = _build_sim(args)
    for _ in range(args.ticks):
        readings = sim.get_readings()
        sim.tick()
        sys.stdout.write(json.dumps(readings) + '\n')


def api_action(args: argparse.Namespace) -> None:
    client = manager.Client.from_args('datagen_api', args)
    app = dg.api.standalone_app(client)
    logging.info(f'Running API on http://{args.host}:{args.port}')
    app.run(host=args.host, port=args.port)


def sim_action(args: argparse.Namespace) -> None:
    # Get the global namespace
    client = manager.Client.from_args('datagen_sim', args)

    def loop_callback(readings: dg.types.ReadingsT) -> None:
        """Write the simulation results to the global namespace."""
        client.get_ns().last_readings = readings

    # Initialise the simulation
    sim = _build_sim(args)
    sim.loop(loop_callback)


if __name__ == '__main__':
    main()
