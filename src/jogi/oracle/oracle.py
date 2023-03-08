import logging
from typing import Optional

from cx_Oracle import Connection, Cursor, DatabaseError, connect

_connection: Optional[Connection] = None

logger = logging.getLogger(__name__)


def get_connection(username: str, password: str, dsn: str) -> Connection:
    global _connection
    if _connection is None:
        try:
            logger.info(f"Logging into database {dsn} as {username}")
            _connection = connect(user=username, password=password, dsn=dsn)
        except DatabaseError as ex:
            logger.exception(ex)
            return None
    return _connection


def get_cursor() -> Cursor:
    if _connection is None:
        logger.error("Connection not open, use get_connection first!")
        return None
    logger.debug("Opening cursor")
    return _connection.cursor()
