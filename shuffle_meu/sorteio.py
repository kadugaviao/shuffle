import random
import re
from urllib.parse import parse_qs, urlsplit

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from .db import get_db
from .musicas import generos, rotulo_genero

bp = Blueprint("sorteio", __name__)

N_PADRAO = 5
AVISO_TODAS_RECENTES = "Você já tocou todas recentemente!"
MSG_NENHUMA = "Nada com esse filtro. Tira algum?"

# Player embutido (design D1 de add-player-embutido): host por igualdade, nunca "termina com".
HOSTS_YOUTUBE = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
ID_YOUTUBE = re.compile(r"[A-Za-z0-9_-]{11}")
CAMINHO_SPOTIFY = re.compile(r"/(?:intl-[a-z]{2}(?:-[a-z]{2})?/)?track/([A-Za-z0-9]{22})/?")

def player(link):
    """{"servico", "src"} do player oficial para vídeo do YouTube ou faixa do Spotify; None para qualquer outro link.
    O src é montado só com constantes e o ID validado: o link digitado nunca vai para o iframe."""
    if not link:
        return None
    try:
        partes = urlsplit(link)
        host = partes.hostname  # minúsculo, sem porta e sem "usuario@"
    except ValueError:
        return None
    if partes.scheme not in ("http", "https") or not host:
        return None
    caminho = partes.path
    id_video = None
    if host in HOSTS_YOUTUBE and caminho.rstrip("/") == "/watch":
        id_video = (parse_qs(partes.query).get("v") or [None])[0]
    elif host in HOSTS_YOUTUBE - {"music.youtube.com"} and caminho.startswith("/shorts/"):
        id_video = caminho[len("/shorts/"):].rstrip("/")
    elif host == "youtu.be":
        id_video = caminho[1:].rstrip("/")
    if id_video is not None:
        if ID_YOUTUBE.fullmatch(id_video):
            return {"servico": "YouTube", "src": f"https://www.youtube-nocookie.com/embed/{id_video}?autoplay=1"}
        return None
    if host == "open.spotify.com" and (m := CAMINHO_SPOTIFY.fullmatch(caminho)):
        return {"servico": "Spotify", "src": f"https://open.spotify.com/embed/track/{m.group(1)}"}
    return None


# filtro -> condição SQL (design.md D6, passo 1); os numéricos chegam como int
CONDICOES = {
    "genero": "genero = ? COLLATE NOCASE",
    "humor": "humor = ?",
    "dificuldade_max": "dificuldade <= ?",
    "artista_id": "artista_id = ?",
    "playlist_id": "id IN (SELECT musica_id FROM playlist_musica WHERE playlist_id = ?)",
}
NUMERICOS = ("dificuldade_max", "artista_id", "playlist_id")


def ler_filtros(args):
    """Filtros preenchidos (os numéricos inválidos são ignorados) e N normalizado: 0 a 50, senão 5."""
    filtros = {}
    for chave in CONDICOES:
        valor = (args.get(chave) or "").strip()
        if chave in NUMERICOS:
            valor = int(valor) if valor.isdigit() else None
        if valor:
            filtros[chave] = valor
    n = args.get("n", "")
    n = int(n) if n.isdigit() else N_PADRAO
    return filtros, n if n <= 50 else N_PADRAO


def candidatas(db, filtros):
    """Músicas ativas (RN04) que atendem a todos os filtros."""
    sql = "SELECT id, favorita FROM musica WHERE ativa = 1"
    for chave in filtros:
        sql += f" AND {CONDICOES[chave]}"  # só chaves fixas de CONDICOES; os valores vão como parâmetro
    return db.execute(sql, list(filtros.values())).fetchall()


def escolher(candidatas, recentes, rng=random):
    """Anti-repetição com fallback da RN06 e peso 2x para favoritas. `candidatas` não pode ser vazia."""
    livres = [c for c in candidatas if c["id"] not in recentes]
    aviso = None
    if not livres:
        livres, aviso = candidatas, AVISO_TODAS_RECENTES
    pesos = [2 if c["favorita"] else 1 for c in livres]
    return rng.choices(livres, weights=pesos)[0], aviso


@bp.get("/")
def inicio():
    db = get_db()
    filtros, n = ler_filtros(request.args)
    ultimo = db.execute(
        "SELECT s.sorteado_em, m.titulo, a.nome AS artista FROM sorteio s"
        " JOIN musica m ON m.id = s.musica_id JOIN artista a ON a.id = m.artista_id ORDER BY s.id DESC LIMIT 1"
    ).fetchone()
    return render_template(
        "inicio.html", f=filtros, n=n, ultimo=ultimo, generos=[(g, rotulo_genero(g)) for g in generos(db)],
        tem_musicas=db.execute("SELECT EXISTS (SELECT 1 FROM musica)").fetchone()[0],
        artistas=db.execute("SELECT id, nome FROM artista ORDER BY nome COLLATE PT").fetchall(),
        playlists=db.execute("SELECT id, nome FROM playlist ORDER BY nome COLLATE PT").fetchall(),
    )


@bp.post("/sortear")
def sortear():
    db = get_db()
    filtros, n = ler_filtros(request.form)
    musicas = candidatas(db, filtros)
    if not musicas:  # RN05: mensagem amigável, nada é gravado
        flash(MSG_NENHUMA, "erro")
        return redirect(url_for(".inicio", **filtros, n=n))
    recentes = {r[0] for r in db.execute("SELECT musica_id FROM sorteio ORDER BY id DESC LIMIT ?", (n,))}
    musica, aviso = escolher(musicas, recentes)
    cur = db.execute("INSERT INTO sorteio (musica_id) VALUES (?)", (musica["id"],))
    db.commit()
    session["revelar"] = cur.lastrowid  # só a primeira visualização anima (D4)
    if aviso:
        flash(aviso, "aviso")
    return redirect(url_for(".resultado", id=cur.lastrowid, **filtros, n=n))


@bp.get("/sorteios/<int:id>")
def resultado(id):
    db = get_db()
    s = db.execute(
        "SELECT s.*, m.titulo, m.link, a.nome AS artista FROM sorteio s"
        " JOIN musica m ON m.id = s.musica_id JOIN artista a ON a.id = m.artista_id WHERE s.id = ?",
        (id,),
    ).fetchone()
    if s is None:
        abort(404)
    filtros, n = ler_filtros(request.args)  # só para o "Pular" repetir os filtros
    roleta = None
    if session.pop("revelar", None) == id:
        roleta = [r[0] for r in db.execute(
            "SELECT titulo FROM musica WHERE ativa = 1 AND id != ? ORDER BY RANDOM() LIMIT 12", (s["musica_id"],))]
        roleta.append(s["titulo"])  # o rolo para sempre na música sorteada
    return render_template("sorteio/resultado.html", s=s, f=filtros, n=n, qs=dict(filtros, n=n), roleta=roleta,
                           player=player(s["link"]),
                           entrar_estrelas=session.pop("tocou", None) == id)
