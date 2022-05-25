from __future__ import annotations
from multiprocessing.managers import (  # type: ignore
        BaseManager, NamespaceProxy, Namespace)
from typing import cast, Dict, Any
import logging
import argparse
import time

from . import common  # noqa: F401


logger = logging.getLogger('manager')


class _GlobManager(BaseManager):
    pass


class Server:

    def __init__(self, host: str, port: int, authkey: bytes) -> None:
        self.h = host
        self.p = port
        self.k = authkey
        self.manager = _GlobManager(address=(self.h, self.p), authkey=self.k)
        logger.info(f'Attempting to create manager at {self.h}:{self.p}')
        self.ns = Namespace()

        def _get_ns(client_name: str) -> Namespace:
            msg = f'Client in {client_name} retrieved global namespace'
            logger.debug(msg)
            return self.ns

        def _on_connect_hook(client_name: str) -> None:
            logger.info(f'Client "{client_name}" connected')

        def _on_disconnect_hook(client_name: str) -> None:
            logger.info(f'Client "{client_name}" disconnected')

        self.manager.register('get_ns', callable=_get_ns,
                              proxytype=NamespaceProxy)
        self.manager.register('on_connect_hook', callable=_on_connect_hook)
        self.manager.register('on_disconnect_hook',
                              callable=_on_disconnect_hook)
        logger.info('Success')

    def run(self) -> None:
        logger.info(f'Running manager on {self.h}:{self.p}')
        self.manager.get_server().serve_forever()

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> Server:
        h, p, k = args.manager_host, args.manager_port, args.manager_authkey
        return cls(h, p, k)


class Client:

    def __init__(self, name: str, host: str, port: int, authkey: bytes
                 ) -> None:
        self.h = host
        self.p = port
        self.k = authkey
        self.manager = _GlobManager(address=(self.h, self.p), authkey=self.k)
        self.name = name
        self.manager.register('get_ns', proxytype=NamespaceProxy)
        self.manager.register('on_connect_hook')
        self.manager.register('on_disconnect_hook')
        self._connect()
        ns = self.get_ns()
        if not hasattr(ns, 'logs'):
            ns.logs = []

    def __del__(self) -> None:
        try:
            self.manager.on_disconnect_hook(self.name)  # type: ignore
        except ConnectionRefusedError:
            pass

    def get_ns(self) -> Namespace:
        try:
            ns = self.manager.get_ns(self.name)  # type: ignore
            return cast(Namespace, ns)
        except ConnectionRefusedError:
            self._connect()
            ns = self.manager.get_ns(self.name)  # type: ignore
            return cast(Namespace, ns)

    def _connect(self) -> None:
        attempts = 10
        for attempt in range(attempts):
            try:
                self.manager.connect()
                self.manager.on_connect_hook(self.name)  # type: ignore
                logger.info(f'Connected to manager as "{self.name}"')
                break
            except ConnectionRefusedError:
                logger.warning('Failed to connect to manager, attempt '
                               f'{attempt + 1}/{attempts}')
                time.sleep(1)
        else:
            raise ConnectionRefusedError('Could not connect to the manager')

    @classmethod
    def from_args(cls, name: str, args: argparse.Namespace) -> Client:
        h, p, k = args.manager_host, args.manager_port, args.manager_authkey
        return cls(name, h, p, k)

    def log(self, msg: str, lvl: str = 'info') -> None:
        ns = self.get_ns()
        if not hasattr(ns, 'logs'):
            ns.logs = []
        logs = ns.logs
        t = ns.time_seconds if hasattr(ns, 'time_seconds') else 0
        logs.append({'msg': msg, 'level': lvl, 'time_seconds': t})
        ns.logs = logs


def add_manager_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--manager_host', type=str, default='127.0.0.1')
    parser.add_argument('--manager_port', type=int, default=6789)
    parser.add_argument('--manager_authkey', type=str.encode, default=b'GPIG')
