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
    # logger.debug("Opening cursor")
    return _connection.cursor()


def run_plsql_procedure(
    procedure: str,
    package: Optional[str] = None,
    schema: Optional[str] = None,
    parameters: Optional[list[str]] = None,
) -> None:
    cursor = get_cursor()
    try:
        procedure_fullname = ".".join([e for e in [schema, package, procedure] if e is not None])
        if parameters and len(parameters) > 0:
            parameters_as_str = "(" + ", ".join(parameters) + ")"
        logger.debug(
            f"Running PL/SQL procedure {procedure_fullname} with params {parameters_as_str}"
        )
        cursor.execute(
            f"""BEGIN
                {procedure_fullname}{parameters_as_str};
                END;"""
        )
    finally:
        cursor.close()
