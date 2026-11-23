import sqlite3
import unicodedata

from flask import current_app, g


def _chave(texto):
    """'Índios' -> 'indios': ordem alfabética sem acentos e sem maiúsculas."""
    return "".join(c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c)).casefold()


def _comparar_pt(a, b):
    a, b = _chave(a), _chave(b)
    return (a > b) - (a < b)


def get_db():
    """Conexão da requisição atual (uma por requisição, fechada no teardown)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.create_collation("PT", _comparar_pt)  # o SQLite ordena por bytes: "Índios" viria depois de "Zé"
        # Sem isso o SQLite ignora as chaves estrangeiras: some a cascata da RN08 e o bloqueio de excluir artista.
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# Colunas acrescentadas depois da primeira versão do schema (add-links-por-servico, D2). O schema.sql já as cria
# em bancos novos; aqui elas chegam a bancos antigos, sem perder dados. Definição igual à do schema.sql.
COLUNAS_NOVAS = {
    "youtube": "TEXT CHECK (youtube LIKE 'http://%' OR youtube LIKE 'https://%')",
    "spotify": "TEXT CHECK (spotify LIKE 'http://%' OR spotify LIKE 'https://%')",
}


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))
    existentes = {linha[1] for linha in db.execute("PRAGMA table_info(musica)")}
    for nome, definicao in COLUNAS_NOVAS.items():
        if nome not in existentes:  # idempotente: na próxima inicialização não há nada a acrescentar
            db.execute(f"ALTER TABLE musica ADD COLUMN {nome} {definicao}")  # nomes fixos acima, sem entrada do usuário
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
