import sqlite3

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .db import get_db

bp = Blueprint("playlists", __name__, url_prefix="/playlists")


def _buscar(id):
    playlist = get_db().execute("SELECT * FROM playlist WHERE id = ?", (id,)).fetchone()
    if playlist is None:
        abort(404)
    return playlist


def _dados(form):
    nome = (form.get("nome") or "").strip()
    return nome, (form.get("descricao") or "").strip() or None


MSG_NOME = "Informe o nome da playlist."


def _erros(nome, descricao):
    """Erros por campo; os limites são os mesmos maxlength do formulário, valendo para qualquer POST."""
    if not nome:
        return {"nome": MSG_NOME}
    if len(nome) > 120:
        return {"nome": "O nome pode ter no máximo 120 caracteres."}
    if descricao and len(descricao) > 200:
        return {"descricao": "A descrição pode ter no máximo 200 caracteres."}
    return {}


@bp.route("", methods=["GET", "POST"])
def lista():
    db = get_db()
    erros, form = {}, {}
    if request.method == "POST":
        nome, descricao = _dados(request.form)
        erros = _erros(nome, descricao)
        if not erros:
            db.execute("INSERT INTO playlist (nome, descricao) VALUES (?, ?)", (nome, descricao))
            db.commit()
            flash("Playlist criada.")
            return redirect(url_for(".lista"))
        form = request.form  # erro junto ao campo, na própria tela (D5)
    playlists = db.execute(
        "SELECT p.*, COUNT(pm.musica_id) AS total FROM playlist p"
        " LEFT JOIN playlist_musica pm ON pm.playlist_id = p.id GROUP BY p.id ORDER BY p.nome COLLATE PT"
    ).fetchall()
    return render_template("playlists/lista.html", playlists=playlists, erros=erros, form=form)


def _detalhe(id, erros=None, form=None):
    playlist = _buscar(id)
    db = get_db()
    base = "SELECT m.id, m.titulo, a.nome AS artista FROM musica m JOIN artista a ON a.id = m.artista_id WHERE m.id"
    filtro = " IN (SELECT musica_id FROM playlist_musica WHERE playlist_id = ?) ORDER BY m.titulo COLLATE PT"
    musicas = db.execute(base + filtro, (id,)).fetchall()
    disponiveis = db.execute(base + " NOT" + filtro, (id,)).fetchall()
    return render_template("playlists/detalhe.html", playlist=playlist, musicas=musicas, disponiveis=disponiveis,
                           erros=erros or {}, form=form or playlist)


@bp.get("/<int:id>")
def detalhe(id):
    return _detalhe(id)


@bp.post("/<int:id>/editar")
def editar(id):
    _buscar(id)
    nome, descricao = _dados(request.form)
    erros = _erros(nome, descricao)
    if erros:
        return _detalhe(id, erros, request.form)
    db = get_db()
    db.execute("UPDATE playlist SET nome = ?, descricao = ? WHERE id = ?", (nome, descricao, id))
    db.commit()
    flash("Playlist atualizada.")
    return redirect(url_for(".detalhe", id=id))


@bp.post("/<int:id>/excluir")
def excluir(id):
    _buscar(id)
    db = get_db()
    db.execute("DELETE FROM playlist WHERE id = ?", (id,))  # vínculos saem por ON DELETE CASCADE; músicas ficam
    db.commit()
    flash("Playlist excluída.")
    return redirect(url_for(".lista"))


@bp.post("/<int:id>/musicas")
def adicionar(id):
    _buscar(id)
    musica_id = request.form.get("musica_id", type=int)
    db = get_db()
    try:
        if musica_id is None:  # OR IGNORE engoliria o NOT NULL e pareceria "já está na playlist"
            raise sqlite3.IntegrityError
        cur = db.execute("INSERT OR IGNORE INTO playlist_musica (playlist_id, musica_id) VALUES (?, ?)",
                         (id, musica_id))
        db.commit()
    except sqlite3.IntegrityError:  # vazio ou música inexistente (FK não é coberta pelo OR IGNORE)
        db.rollback()
        flash("Escolha uma música do repertório.", "erro")
    else:
        if cur.rowcount:
            flash("Música adicionada.")
        else:
            flash("Essa música já está na playlist.", "erro")
    return redirect(url_for(".detalhe", id=id))


@bp.post("/<int:id>/musicas/<int:musica_id>/remover")
def remover(id, musica_id):
    _buscar(id)
    db = get_db()
    apagadas = db.execute("DELETE FROM playlist_musica WHERE playlist_id = ? AND musica_id = ?", (id, musica_id)).rowcount
    db.commit()
    if apagadas:
        flash("Música removida da playlist.")
    else:
        flash("Essa música não está na playlist.", "erro")
    return redirect(url_for(".detalhe", id=id))
