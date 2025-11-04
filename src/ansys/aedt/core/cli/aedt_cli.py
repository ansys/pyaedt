import typer

from ansys.aedt.core import Circuit, Desktop

NAME = "AEDT"


app = typer.Typer(help=f"CLI for {NAME}", no_args_is_help=True)


@app.command()
def start():
    f"""Start {NAME}"""
    typer.echo(f"{NAME} started.")


@app.command()
def stop():
    f"""Stop {NAME}"""
    typer.echo(f"{NAME} stopped.")


@app.command()
def list():
    f"""List {NAME} status"""
    typer.echo(f"{NAME} status: running")


if __name__ == "__main__":
    app()
