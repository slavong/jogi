import logging
import os
from typing import Optional

import cx_Oracle

from jogi.oracle.oracle import get_connection, get_cursor

logger = logging.getLogger(__name__)

SQL_EXTENSION = "sql"


def dump_schema(
    target_path: str,
    username: str,
    password: str,
    dsn: str,
    types: Optional[list[str]],
    names: Optional[list[str]],
) -> None:
    logger.info(f"dsn={dsn} username={username} password=***" f" types={types}" f" names={names}")
    connection = get_connection(username, password, dsn)
    if connection is None:
        logger.info("Exiting ...")
        return

    cursor = get_cursor()
    if cursor is None:
        logger.info("Exiting...")
        return

    _set_metadata_params()

    sql = _get_sql(types, names)
    cursor.execute(sql)

    _create_folder_if_not_exists(target_path)

    for row in cursor:
        schema, object_type, object_name, ddl = row
        logger.info(f"{schema} {object_type} {object_name}")
        _save_ddl(target_path, schema, object_type, object_name, ddl)

    # TODO: deleted objects? file stays there => cli option?: delete folder/schema/type/file.sql


def _set_metadata_params() -> None:
    cursor = get_cursor()
    for keyword in ("STORAGE", "TABLESPACE", "SEGMENT_ATTRIBUTES", "PARTITIONING"):
        cursor.execute(
            f"""BEGIN
                    DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM,'{keyword}',false);
                END;"""
        )

    cursor.execute(
        """BEGIN
               DBMS_METADATA.SET_TRANSFORM_PARAM(
                   DBMS_METADATA.SESSION_TRANSFORM, 'SQLTERMINATOR', true);
           END;"""
    )


def _get_sql(types: Optional[list[str]], names: Optional[list[str]]) -> str:
    where_object_type = "1=1"
    if types:
        types_upper = [t.upper() for t in types]
        types_as_str = "'" + "','".join(types_upper) + "'"
        where_object_type = f"object_type IN ({types_as_str})"

    where_object_name = "1=1"
    if names:
        name_conditions = [f"object_name LIKE '{n}'" for n in names]
        where_object_name = "\n OR ".join(name_conditions)

    sql = f"""SELECT USER AS schema, object_type, object_name,
                DBMS_METADATA.GET_DDL(
                  object_type=>CASE object_type
                    WHEN 'PACKAGE' THEN 'PACKAGE_SPEC'
                    ELSE REPLACE(object_type, ' ', '_') END,
                  name=>object_name,
                  schema=>USER) AS ddl
              FROM user_objects
              WHERE 1=1
                AND {where_object_type}
                AND ({where_object_name})
              ORDER BY object_type, object_name"""
    logger.debug(sql)
    return sql


def _create_folder_if_not_exists(folder: str) -> None:
    os.makedirs(folder, exist_ok=True)


def _save_ddl(
    target_path: str, schema: str, object_type: str, object_name: str, ddl: cx_Oracle.LOB
) -> None:
    folder_path = os.path.join(target_path, schema.lower(), object_type.lower())
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{object_name}.{SQL_EXTENSION}")
    with open(file_path, "w") as f:
        f.write(ddl.read())
