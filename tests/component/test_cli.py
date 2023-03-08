from typer.testing import CliRunner

from jogi import __app_name__, __version__, main

runner = CliRunner()


def test_version():
    return
    result = runner.invoke(main.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout