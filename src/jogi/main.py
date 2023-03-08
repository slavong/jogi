import typer
from config import get_config

app = typer.Typer()


@app.command()
def main():
    pass


if __name__ == "__main__":
    _ = get_config()
    app()
