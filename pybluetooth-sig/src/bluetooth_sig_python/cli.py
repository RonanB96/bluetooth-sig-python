"""Console script for bluetooth_sig_python."""

import typer
from rich.console import Console

from bluetooth_sig_python import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for bluetooth_sig_python."""
    console.print("Replace this message by putting your code into "
               "bluetooth_sig_python.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
