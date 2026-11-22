import sqlite3

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .db import get_db

bp = Blueprint("musicas", __name__, url_prefix="/musicas")

# valor gravado no banco -> rótulo da interface
HUMORES = {"animada": "Animada", "calma": "Calma", "triste": "Triste", "romantica": "Romântica"}
MSG_DUPLICADA = "Essa música já está cadastrada para esse artista."
MSG_ARTISTA = "Escolha o artista da música."
FILTROS_LISTA = ("q", "genero", "humor", "favorita")


def _filtros_lista(args):
    """Só as chaves de busca/filtro do Repertório (um ?id= solto quebraria o url_for das rotas com id)."""
    return {k: args[k] for k in FILTROS_LISTA if args.get(k)}


def validar_musica(form):
    """Valida o formulário de música (RN01, RN03, humor, link). Retorna (dados, erros {campo: mensagem})."""

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
    erros = {}
    if not dados["titulo"]:
        erros["titulo"] = "Informe o título da música."
    try:
        dados["artista_id"] = int(form.get("artista_id") or "")
    except ValueError:
        dados["artista_id"] = None
        erros["artista_id"] = MSG_ARTISTA
    try:
        dados["dificuldade"] = int(form.get("dificuldade") or "")
    except ValueError:
        dados["dificuldade"] = None
    if dados["dificuldade"] is None or not 1 <= dados["dificuldade"] <= 5:
        erros["dificuldade"] = "A dificuldade deve ser um número de 1 a 5."
    if dados["humor"] and dados["humor"] not in HUMORES:
        erros["humor"] = "Escolha um humor da lista."
    if dados["link"] and not dados["link"].lower().startswith(("http://", "https://")):
        erros["link"] = "O link deve começar com http:// ou https://."
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
    """Grava se não for duplicata (RN02). Retorna {campo: mensagem} (vazio se gravou)."""
    db = get_db()
    # shortcut: compara em Python porque o NOCASE do SQLite só trata ASCII; ok para repertórios pessoais.
    for outra in db.execute("SELECT id, titulo FROM musica WHERE artista_id = ?", (dados["artista_id"],)):
        if outra["id"] != musica_id and outra["titulo"].casefold() == dados["titulo"].casefold():
            return {"titulo": MSG_DUPLICADA}
    try:
        db.execute(sql, dados)
        db.commit()
    except sqlite3.IntegrityError as e:
        db.rollback()
        # UNIQUE: duplicata que passou pela checagem (RN02); FK: artista inexistente
        return {"titulo": MSG_DUPLICADA} if "UNIQUE" in str(e) else {"artista_id": MSG_ARTISTA}
    return {}


def _form(musica, id=None, erros=None):
    db = get_db()
    artistas = db.execute("SELECT id, nome FROM artista ORDER BY nome COLLATE PT").fetchall()
    return render_template("musicas/form.html", musica=musica, id=id, artistas=artistas, generos=generos(db),
                           erros=erros or {})


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
                           generos=[(g, g) for g in generos(db)], qs=_filtros_lista(request.args))


@bp.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        dados, erros = validar_musica(request.form)
        dados.update(favorita=0, ativa=1)  # toda música nova começa ativa e não favorita
        erros = erros or _gravar(
            "INSERT INTO musica (titulo, artista_id, genero, humor, dificuldade, link, favorita, ativa)"
            " VALUES (:titulo, :artista_id, :genero, :humor, :dificuldade, :link, :favorita, :ativa)",
            dados,
        )
        if not erros:
            flash("Música cadastrada.")
            return redirect(url_for(".lista"))
        return _form(request.form, erros=erros)
    return _form({"dificuldade": 3})


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    musica = _buscar(id)
    if request.method == "POST":
        dados, erros = validar_musica(request.form)
        dados["id"] = id
        erros = erros or _gravar(
            "UPDATE musica SET titulo = :titulo, artista_id = :artista_id, genero = :genero, humor = :humor,"
            " dificuldade = :dificuldade, link = :link, favorita = :favorita, ativa = :ativa WHERE id = :id",
            dados,
            id,
        )
        if not erros:
            flash("Música atualizada.")
            return redirect(url_for(".lista"))
        return _form(request.form, id, erros)
    return _form(musica, id)


def _atalho(id, coluna):
    """Grava o estado pedido (0/1), sem inverter: clique repetido não desfaz (D2)."""
    _buscar(id)
    valor = request.form.get("valor")
    if valor not in ("0", "1"):
        abort(400)
    db = get_db()
    db.execute(f"UPDATE musica SET {coluna} = ? WHERE id = ?", (int(valor), id))  # coluna vem só das rotas abaixo
    db.commit()
    # volta com a mesma busca/filtros (request.args, sem "next" livre) e à mesma posição
    return redirect(url_for(".lista", **_filtros_lista(request.args)) + f"#musica-{id}")


@bp.post("/<int:id>/favorita")
def favorita(id):
    return _atalho(id, "favorita")


@bp.post("/<int:id>/ativa")
def ativa(id):
    return _atalho(id, "ativa")


@bp.post("/<int:id>/excluir")
def excluir(id):
    _buscar(id)
    db = get_db()
    db.execute("DELETE FROM musica WHERE id = ?", (id,))  # histórico e vínculos saem por ON DELETE CASCADE (RN08)
    db.commit()
    flash("Música excluída.")
    return redirect(url_for(".lista"))
