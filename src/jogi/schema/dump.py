import logging
import os
from typing import Optional

from cx_Oracle import LOB

from jogi.oracle.oracle import get_connection, get_cursor, run_plsql_procedure

logger = logging.getLogger(__name__)

SQL_EXTENSION = "sql"
SUPPORTED_OBJECT_TYPES = ("MATERIALIZED VIEW", "PACKAGE", "PACKAGE BODY", "TABLE", "VIEW")


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

    _dump_schema_to_folder(target_path, types, names)

    _delete_files_for_nonexistent_objects(
        path=target_path, schema=username, types=types, names=names
    )


def _dump_schema_to_folder(
    target_path: str, types: Optional[list[str]], names: Optional[list[str]]
) -> None:
    cursor = get_cursor()
    try:
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
    finally:
        cursor.close()


def _delete_files_for_nonexistent_objects(
    path: str, schema: str, types: Optional[list[str]], names: Optional[list[str]]
) -> None:
    schema_path = os.path.join(path, schema)
    os.walk(schema_path)
    for w in os.walk(schema_path):
        path, folders, files = w
        if path == schema_path:
            assert all([tf.upper() in SUPPORTED_OBJECT_TYPES for tf in folders])
            assert files == []
        else:
            _, type = os.path.split(path)
            type = type.upper()
            if types and len(types) > 0 and type not in types:
                continue
            _cleanup_type_folder(path, type, files)

    pass


def _cleanup_type_folder(path: str, object_type: str, files: list[str]) -> None:
    logger.debug(f"Cleaning up folder {path} with files {files} for type {object_type}...")
    for file in files:
        logger.debug(f"Checking file {file} ...")
        name, ext = file.split(".")
        assert ext == SQL_EXTENSION
        cursor = get_cursor()
        try:
            sql = f"""SELECT COUNT(1) AS c
                      FROM user_objects
                      WHERE object_type = '{object_type}'
                        AND object_name = '{name}'
                """
            cursor.execute(sql)
            rows = list(cursor)
            assert len(rows) == 1
            row = rows[0]
            assert len(row) == 1
            c = row[0]
            assert c in (0, 1)
            match c:
                case 0:
                    file_path = os.path.join(path, file)
                    logger.info(f"Deleting file {file_path}")
                    os.remove(file_path)
                case 1:
                    pass
        finally:
            cursor.close()
    pass


def _set_metadata_params() -> None:
    for keyword in ("STORAGE", "TABLESPACE", "SEGMENT_ATTRIBUTES", "PARTITIONING"):
        run_plsql_procedure(
            package="DBMS_METADATA",
            procedure="SET_TRANSFORM_PARAM",
            parameters=["DBMS_METADATA.SESSION_TRANSFORM", f"'{keyword}'", "FALSE"],
        )

    run_plsql_procedure(
        package="DBMS_METADATA",
        procedure="SET_TRANSFORM_PARAM",
        parameters=["DBMS_METADATA.SESSION_TRANSFORM", "'SQLTERMINATOR'", "TRUE"],
    )


def _get_sql(types: Optional[list[str]], names: Optional[list[str]]) -> str:
    sql = f"""SELECT USER AS schema, object_type, object_name,
                DBMS_METADATA.GET_DDL(
                  object_type=>CASE object_type
                    WHEN 'PACKAGE' THEN 'PACKAGE_SPEC'
                    ELSE REPLACE(object_type, ' ', '_') END,
                  name=>object_name,
                  schema=>USER) AS ddl
              FROM user_objects
              WHERE 1=1
                AND {_get_object_type_condition(types)}
                AND ({_get_object_name_condition(names)})
              ORDER BY object_type, object_name"""
    logger.debug(sql)
    return sql


def _get_object_type_condition(types: Optional[list[str]]) -> str:
    if not types:
        return "1=1"
    types_upper = [t.upper() for t in types]
    types_as_str = "'" + "','".join(types_upper) + "'"
    where_object_type = f"object_type IN ({types_as_str})"
    return where_object_type


def _get_object_name_condition(names: Optional[list[str]]) -> str:
    if not names:
        return "1=1"
    name_conditions = [f"object_name LIKE '{n}' ESCAPE '\\'" for n in names]
    where_object_name = "\n OR ".join(name_conditions)
    return where_object_name


def _create_folder_if_not_exists(folder: str) -> None:
    os.makedirs(folder, exist_ok=True)


def _save_ddl(target_path: str, schema: str, object_type: str, object_name: str, ddl: LOB) -> None:
    folder_path = os.path.join(target_path, schema.lower(), object_type.lower())
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{object_name}.{SQL_EXTENSION}")
    with open(file_path, "w") as f:
        f.write(ddl.read())
