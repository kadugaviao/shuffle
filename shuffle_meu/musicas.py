import sqlite3

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .db import get_db

bp = Blueprint("musicas", __name__, url_prefix="/musicas")

# valor gravado no banco -> rótulo da interface
HUMORES = {"animada": "Animada", "calma": "Calma", "triste": "Triste", "romantica": "Romântica"}
MSG_DUPLICADA = "Essa música já está cadastrada para esse artista."
MSG_ARTISTA = "Escolha o artista da música."


def validar_musica(form):
    """Valida o formulário de música (RN01, RN03, humor, link). Retorna (dados, erros)."""

    def campo(nome):
        return (form.get(nome) or "").strip() or None

    dados = {
        "titulo": campo("titulo"),
        "genero": campo("genero"),
        "humor": campo("humor"),
        "link": campo("link"),
        "favorita": 1 if form.get("favorita") else 0,
        "ativa": 1 if form.get("ativa") else 0,
    }
    erros = []
    if not dados["titulo"]:
        erros.append("Informe o título da música.")
    try:
        dados["artista_id"] = int(form.get("artista_id") or "")
    except ValueError:
        dados["artista_id"] = None
        erros.append(MSG_ARTISTA)
    try:
        dados["dificuldade"] = int(form.get("dificuldade") or "")
    except ValueError:
        dados["dificuldade"] = None
    if dados["dificuldade"] is None or not 1 <= dados["dificuldade"] <= 5:
        erros.append("A dificuldade deve ser um número de 1 a 5.")
    if dados["humor"] and dados["humor"] not in HUMORES:
        erros.append("Escolha um humor da lista.")
    if dados["link"] and not dados["link"].lower().startswith(("http://", "https://")):
        erros.append("O link deve começar com http:// ou https://.")
    return dados, erros


def generos(db):
    """Gêneros já usados no repertório, sem repetir 'rock' e 'Rock'."""
    return [r[0] for r in db.execute(
        "SELECT MIN(genero) FROM musica WHERE genero IS NOT NULL"
        " GROUP BY genero COLLATE NOCASE ORDER BY 1 COLLATE PT"
    )]


def _buscar(id):
    musica = get_db().execute("SELECT * FROM musica WHERE id = ?", (id,)).fetchone()
    if musica is None:
        abort(404)
    return musica


def _gravar(sql, dados, musica_id=None):
    """Grava se não for duplicata (RN02). Retorna a mensagem de erro ou None."""
    db = get_db()
    # shortcut: compara em Python porque o NOCASE do SQLite só trata ASCII; ok para repertórios pessoais.
    for outra in db.execute("SELECT id, titulo FROM musica WHERE artista_id = ?", (dados["artista_id"],)):
        if outra["id"] != musica_id and outra["titulo"].casefold() == dados["titulo"].casefold():
            return MSG_DUPLICADA
    try:
        db.execute(sql, dados)
        db.commit()
    except sqlite3.IntegrityError as e:
        db.rollback()
        return MSG_DUPLICADA if "UNIQUE" in str(e) else MSG_ARTISTA  # FK: artista inexistente
    return None


def _form(musica, id=None):
    db = get_db()
    artistas = db.execute("SELECT id, nome FROM artista ORDER BY nome COLLATE PT").fetchall()
    return render_template("musicas/form.html", musica=musica, id=id, artistas=artistas, generos=generos(db))


@bp.get("")
def lista():
    db = get_db()
    q = request.args.get("q", "").strip()
    f = {k: request.args.get(k, "").strip() for k in ("genero", "humor", "favorita")}
    sql = "SELECT m.*, a.nome AS artista FROM musica m JOIN artista a ON a.id = m.artista_id WHERE 1 = 1"
    params = []
    if f["genero"]:
        sql += " AND m.genero = ? COLLATE NOCASE"
        params.append(f["genero"])
    if f["humor"]:
        sql += " AND m.humor = ?"
        params.append(f["humor"])
    if f["favorita"]:
        sql += " AND m.favorita = 1"
    musicas = db.execute(sql + " ORDER BY m.titulo COLLATE PT", params).fetchall()
    if q:  # em Python para ignorar maiúsculas também em letras acentuadas ("LEGIÃO" acha "Legião")
        q = q.casefold()
        musicas = [m for m in musicas if q in m["titulo"].casefold() or q in m["artista"].casefold()]
    return render_template("musicas/lista.html", musicas=musicas, q=request.args.get("q", ""), f=f,
                           generos=generos(db))


@bp.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        dados, erros = validar_musica(request.form)
        dados.update(favorita=0, ativa=1)  # toda música nova começa ativa e não favorita
        if not erros:
            erro = _gravar(
                "INSERT INTO musica (titulo, artista_id, genero, humor, dificuldade, link, favorita, ativa)"
                " VALUES (:titulo, :artista_id, :genero, :humor, :dificuldade, :link, :favorita, :ativa)",
                dados,
            )
            if not erro:
                flash("Música cadastrada.")
                return redirect(url_for(".lista"))
            erros = [erro]
        for erro in erros:
            flash(erro, "erro")
        return _form(request.form)
    return _form({"dificuldade": 3})


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    musica = _buscar(id)
    if request.method == "POST":
        dados, erros = validar_musica(request.form)
        dados["id"] = id
        if not erros:
            erro = _gravar(
                "UPDATE musica SET titulo = :titulo, artista_id = :artista_id, genero = :genero, humor = :humor,"
                " dificuldade = :dificuldade, link = :link, favorita = :favorita, ativa = :ativa WHERE id = :id",
                dados,
                id,
            )
            if not erro:
                flash("Música atualizada.")
                return redirect(url_for(".lista"))
            erros = [erro]
        for erro in erros:
            flash(erro, "erro")
        musica = request.form
    return _form(musica, id)


@bp.post("/<int:id>/excluir")
def excluir(id):
    _buscar(id)
    db = get_db()
    db.execute("DELETE FROM musica WHERE id = ?", (id,))  # histórico e vínculos saem por ON DELETE CASCADE (RN08)
    db.commit()
    flash("Música excluída.")
    return redirect(url_for(".lista"))
