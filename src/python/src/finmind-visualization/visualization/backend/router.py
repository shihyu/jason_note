import time
import typing

import redis
from loguru import logger
from sqlalchemy import engine

from visualization.backend import clients


def check_alive(connect: engine.base.Connection):
    connect.execute("SELECT 1 + 1")


def check_connect_alive(
    connect: typing.Union[engine.base.Connection, redis.Redis],
    connect_func: typing.Callable,
):
    if connect:
        try:
            check_alive(connect)
            return connect
        except Exception as e:
            logger.info(f"{connect_func.__name__} reconnect, error: {e}")
            time.sleep(1)
            try:
                connect = connect_func()
            except Exception as e:
                logger.info(f"{connect_func.__name__} connect error {e}")
            return check_connect_alive(connect, connect_func)
    else:
        try:
            connect = connect_func()
        except Exception as e:
            logger.info(f"{connect_func.__name__} connect error {e}")
        return check_connect_alive(connect, connect_func)


class Router:
    def __init__(self):
        self._mysql_redash_conn = clients.get_redash_mysql_conn()

    def check_mysql_redash_conn_alive(self):
        self._mysql_redash_conn = check_connect_alive(
            self._mysql_redash_conn, clients.get_redash_mysql_conn
        )
        return self._mysql_redash_conn

    @property
    def mysql_redash_conn(self):
        return self.check_mysql_redash_conn_alive()
