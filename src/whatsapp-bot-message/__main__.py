import typer

from .worker.whatsapp_bot import WhatsAppBot

app = typer.Typer()


@app.callback()
def callback():
    pass


@app.command()
def execute(message: str = typer.Option()):
    worker = WhatsAppBot(message)
    worker()


if __name__ == '__main__':
    app()
