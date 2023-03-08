from typing import Optional

import typer

from jogi.schema.dump import dump_schema

app = typer.Typer()


@app.command()
def dump(
    username: str = typer.Argument(..., help="Database user name = schema, e.g. SCOTT"),
    password: str = typer.Argument(..., help="Password for the database user, e.g. TIGER"),
    dsn: str = typer.Argument(..., help="Data source name, e.g. localhost:1521/localdb"),
    target_path: str = typer.Argument(
        default=".", dir_okay=True, help="Target directory for saving DDL scripts, must be empty"
    ),
    types: Optional[str] = typer.Option(
        default=None,
        case_sensitive=False,
        help="Comma delimited list of object types" " (no spaces!)," " e.g. 'TABLE,VIEW'",
    ),
    names: Optional[str] = typer.Option(
        default=None, help="Object names with optional wildcards," " e.g. 'EMP%,DEPT'"
    ),
) -> None:
    types_as_list = types.split(",") if types is not None else []
    names_as_list = names.split(",") if names is not None else []
    dump_schema(target_path, username, password, dsn, types_as_list, names_as_list)


if __name__ == "__main__":
    app()
