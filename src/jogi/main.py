import logging
import sys

import typer
from cli import schema
from config import get_config

from jogi.config.config import Settings

app = typer.Typer(help="jogi - Jinxy Oracle git integration")

app.add_typer(schema.app, name="schema")

logger = logging.getLogger(__name__)


@app.command()
def jump() -> None:
    # TODO: replace by real command, is required so that "schema" is recognized as command
    pass


def init_logging(config: Settings) -> None:
    log_level = config.log.level
    log_format = "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"
    logging.basicConfig(level=log_level, format=log_format, stream=sys.stdout, force=True)


if __name__ == "__main__":
    config = get_config()
    init_logging(config)
    app()
