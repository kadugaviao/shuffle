import os
from datetime import datetime, timezone

from flask import Flask

from . import db


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # shortcut: chave fixa para uso local; defina SECRET_KEY no ambiente se o sistema for publicado.
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.path.join(app.instance_path, "shuffle.db"),
    )
    if config:
        app.config.update(config)
    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    from . import artistas, historico, musicas, playlists, sorteio

    for modulo in (artistas, musicas, playlists, sorteio, historico):
        app.register_blueprint(modulo.bp)
    app.jinja_env.filters["data_local"] = data_local
    app.jinja_env.globals["HUMORES"] = musicas.HUMORES
    return app


def data_local(texto):
    """'2026-11-22 23:05:00' (UTC, como o SQLite grava) -> '22/11/2026 20:05' na hora local do servidor."""
    dt = datetime.strptime(texto, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return dt.astimezone().strftime("%d/%m/%Y %H:%M")
