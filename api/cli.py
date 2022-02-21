#!/usr/bin/env python3
import argparse
import logging
import subprocess
import os

import manager
import api


logger = logging.getLogger('api')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--port', '-p', type=int, default=8080)
    parser.add_argument('--debug', action='store_true')
    manager.common.add_logging_args(parser)
    manager.add_manager_arguments(parser)

    subparsers = parser.add_subparsers()
    p = subparsers.add_parser('dev')
    p.set_defaults(func=dev_action)
    p = subparsers.add_parser('deploy')
    p.add_argument('--workers', type=int, default=2)
    p.set_defaults(func=deploy_action)
    # Parse arguments
    args = parser.parse_args()
    args.func(args)


def dev_action(args: argparse.Namespace) -> None:
    # Logging config
    manager.common.init_logging(args)
    logger.info(f'Loaded logging config from {args.logging_config}')
    # Start the server
    manager_client = manager.Client.from_args('api', args)
    app = api.dev_app(manager_client)
    app.run(host=args.host, port=args.port)


def deploy_action(args: argparse.Namespace) -> None:
    assert args.workers >= 1
    env = os.environ.copy()
    env['MANAGER_HOST'] = args.manager_host
    env['MANAGER_PORT'] = str(args.manager_port)
    env['MANAGER_AUTHKEY'] = bytes(args.manager_authkey).decode('utf-8')
    env['LOGGING_CONFIG'] = str(args.logging_config)
    cmd = ['gunicorn',
           '--bind', f'{args.host}:{args.port}',
           '--workers', str(args.workers),
           '--log-level', str(logger.level),
           'wsgi:app']
    subprocess.run(cmd, env=env)


if __name__ == '__main__':
    main()
