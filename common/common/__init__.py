from multiprocessing.managers import (  # type: ignore
        BaseManager, NamespaceProxy, Namespace)
from typing import Tuple
import logging


class GlobManager(BaseManager):
    pass


def init_global_manager(addr: Tuple[str, int]
                        ) -> Tuple[Namespace, GlobManager]:
    logging.info(f'Attempting to create manager at {addr}')
    ns = Namespace()

    def _get_ns() -> Namespace:
        return ns

    GlobManager.register('get_ns', callable=_get_ns, proxytype=NamespaceProxy)
    manager = GlobManager(address=addr, authkey=b'GPIG')
    logging.info('Success')
    return ns, manager


def connect_global_manager(addr: Tuple[str, int]) -> GlobManager:
    manager = GlobManager(address=addr, authkey=b'GPIG')
    manager.register('get_ns', proxytype=NamespaceProxy)
    manager.connect()
    return manager
