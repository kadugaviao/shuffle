"""Links de YouTube e Spotify (design D1 de add-links-por-servico): extração estrita do ID e montagem do player.

Usado pela validação do formulário (musicas.py) e pela tela de resultado (sorteio.py). O host é comparado por
igualdade numa lista fechada, nunca por "termina com", e o src do player é montado só com constantes e o ID.
"""

import re
from urllib.parse import parse_qs, urlsplit

HOSTS_YOUTUBE = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
ID_YOUTUBE = re.compile(r"[A-Za-z0-9_-]{11}")
CAMINHO_SPOTIFY = re.compile(r"/(?:intl-[a-z]{2}(?:-[a-z]{2})?/)?track/([A-Za-z0-9]{22})/?")


def _partes(link):
    """(host, caminho, query) de um link http(s), ou None."""
    if not link:
        return None
    try:
        partes = urlsplit(link)
        host = partes.hostname  # minúsculo, sem porta e sem "usuario@"
    except ValueError:
        return None
    if partes.scheme not in ("http", "https") or not host:
        return None
    return host, partes.path, partes.query


def youtube_id(link):
    """ID do vídeo para youtube.com|www|m|music /watch?v=, youtu.be/<ID> e /shorts/<ID>; None para o resto."""
    partes = _partes(link)
    if not partes:
        return None
    host, caminho, query = partes
    if host in HOSTS_YOUTUBE and caminho.rstrip("/") == "/watch":
        id_video = (parse_qs(query).get("v") or [""])[0]
    elif host in HOSTS_YOUTUBE - {"music.youtube.com"} and caminho.startswith("/shorts/"):
        id_video = caminho[len("/shorts/"):].rstrip("/")
    elif host == "youtu.be":
        id_video = caminho[1:].rstrip("/")
    else:
        return None
    return id_video if ID_YOUTUBE.fullmatch(id_video) else None


def spotify_id(link):
    """ID da faixa para open.spotify.com/track/<ID> e /intl-xx[-yy]/track/<ID>; None para o resto."""
    partes = _partes(link)
    if not partes or partes[0] != "open.spotify.com":
        return None
    m = CAMINHO_SPOTIFY.fullmatch(partes[1])
    return m.group(1) if m else None


def players(youtube, spotify):
    """Players disponíveis, sempre YouTube antes de Spotify: [{"chave", "servico", "src"}]."""
    lista = []
    if id_video := youtube_id(youtube):
        lista.append({"chave": "youtube", "servico": "YouTube",
                      "src": f"https://www.youtube-nocookie.com/embed/{id_video}?autoplay=1"})
    if id_faixa := spotify_id(spotify):
        lista.append({"chave": "spotify", "servico": "Spotify", "src": f"https://open.spotify.com/embed/track/{id_faixa}"})
    return lista
