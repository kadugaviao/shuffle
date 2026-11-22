from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from .db import get_db

bp = Blueprint("historico", __name__)


def _buscar(id):
    s = get_db().execute("SELECT * FROM sorteio WHERE id = ?", (id,)).fetchone()
    if s is None:
        abort(404)
    return s


def _voltar(id):
    # a query string guarda os filtros do sorteio, para o "Pular" continuar funcionando
    return redirect(url_for("sorteio.resultado", id=id, **request.args.to_dict()))


@bp.post("/sorteios/<int:id>/toquei")
def toquei(id):
    _buscar(id)
    db = get_db()
    db.execute("UPDATE sorteio SET tocada = 1 WHERE id = ?", (id,))
    db.commit()
    session["tocou"] = id  # as estrelas entram com pop na próxima visualização
    flash("Marcada como tocada. Agora você pode avaliar.")
    return _voltar(id)


@bp.post("/sorteios/<int:id>/avaliar")
def avaliar(id):
    s = _buscar(id)
    nota = request.form.get("nota", type=int)
    if not s["tocada"]:  # RN07
        flash("Marque como tocada antes de avaliar.", "erro")
    elif nota is None or not 1 <= nota <= 5:
        flash("A nota deve ser de 1 a 5.", "erro")
    else:
        db = get_db()
        db.execute("UPDATE sorteio SET nota = ? WHERE id = ?", (nota, id))
        db.commit()
        flash("Avaliação salva.")
    return _voltar(id)


@bp.get("/historico")
def lista():
    sorteios = get_db().execute(
        "SELECT s.*, m.titulo, a.nome AS artista FROM sorteio s"
        " JOIN musica m ON m.id = s.musica_id JOIN artista a ON a.id = m.artista_id ORDER BY s.id DESC LIMIT 50"
    ).fetchall()
    return render_template("historico.html", sorteios=sorteios)
