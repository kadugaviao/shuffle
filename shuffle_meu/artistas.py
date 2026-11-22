import sqlite3

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .db import get_db

bp = Blueprint("artistas", __name__, url_prefix="/artistas")

MSG_DUPLICADO = "Já existe um artista com esse nome."


def _buscar(id):
    artista = get_db().execute("SELECT * FROM artista WHERE id = ?", (id,)).fetchone()
    if artista is None:
        abort(404)
    return artista


def _validar(form, artista_id=None):
    """Retorna (dados, erro). Nome obrigatório e único sem diferenciar maiúsculas, inclusive com acento."""
    nome = (form.get("nome") or "").strip()
    pais = (form.get("pais") or "").strip() or None
    if not nome:
        return None, "Informe o nome do artista."
    # shortcut: compara em Python porque o NOCASE do SQLite só trata ASCII; ok até alguns milhares de artistas.
    for outro in get_db().execute("SELECT id, nome FROM artista"):
        if outro["id"] != artista_id and outro["nome"].casefold() == nome.casefold():
            return None, MSG_DUPLICADO
    return {"nome": nome, "pais": pais, "id": artista_id}, None


def _gravar(sql, dados):
    db = get_db()
    try:
        db.execute(sql, dados)
        db.commit()
    except sqlite3.IntegrityError:  # outro cadastro igual entrou entre a checagem e o INSERT
        db.rollback()
        return MSG_DUPLICADO
    return None


@bp.get("")
def lista():
    artistas = get_db().execute(
        "SELECT a.*, COUNT(m.id) AS total FROM artista a"
        " LEFT JOIN musica m ON m.artista_id = a.id GROUP BY a.id ORDER BY a.nome COLLATE PT"
    ).fetchall()
    return render_template("artistas/lista.html", artistas=artistas)


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        dados, erro = _validar(request.form)
        erro = erro or _gravar("INSERT INTO artista (nome, pais) VALUES (:nome, :pais)", dados)
        if not erro:
            flash("Artista cadastrado.")
            return redirect(url_for(".lista"))
        flash(erro, "erro")
    return render_template("artistas/form.html", artista=request.form, id=None)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    artista = _buscar(id)
    if request.method == "POST":
        dados, erro = _validar(request.form, id)
        erro = erro or _gravar("UPDATE artista SET nome = :nome, pais = :pais WHERE id = :id", dados)
        if not erro:
            flash("Artista atualizado.")
            return redirect(url_for(".lista"))
        flash(erro, "erro")
        artista = request.form
    return render_template("artistas/form.html", artista=artista, id=id)


@bp.post("/<int:id>/excluir")
def excluir(id):
    _buscar(id)
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM musica WHERE artista_id = ?", (id,)).fetchone()[0]
    if total:
        flash(f"Este artista tem {total} música(s). Exclua as músicas antes de excluir o artista.", "erro")
    else:
        db.execute("DELETE FROM artista WHERE id = ?", (id,))
        db.commit()
        flash("Artista excluído.")
    return redirect(url_for(".lista"))
