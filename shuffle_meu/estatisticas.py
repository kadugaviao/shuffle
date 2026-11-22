"""Estatísticas da tela "Histórico e estatísticas" (spec estatisticas, design.md D1). Só leitura."""

from collections import Counter

from .db import _chave

JUNTA = "FROM sorteio s JOIN musica m ON m.id = s.musica_id JOIN artista a ON a.id = m.artista_id"


def calcular(db):
    """Recebe a conexão da app (precisa da collation PT registrada em get_db)."""
    musicas, sorteios, tocadas, media = db.execute(
        "SELECT (SELECT COUNT(*) FROM musica), (SELECT COUNT(*) FROM sorteio),"
        " (SELECT COUNT(*) FROM sorteio WHERE tocada = 1), (SELECT AVG(nota) FROM sorteio WHERE nota IS NOT NULL)"
    ).fetchone()
    return {
        "resumo": {"musicas": musicas, "sorteios": sorteios, "tocadas": tocadas, "media": media},
        "top5": db.execute(
            f"SELECT m.id, m.titulo, a.nome AS artista, COUNT(*) AS vezes {JUNTA}"
            " WHERE s.tocada = 1 GROUP BY m.id ORDER BY vezes DESC, m.titulo COLLATE PT LIMIT 5"
        ).fetchall(),
        "nunca": db.execute(
            "SELECT m.id, m.titulo, a.nome AS artista FROM musica m JOIN artista a ON a.id = m.artista_id"
            " WHERE m.ativa = 1 AND NOT EXISTS (SELECT 1 FROM sorteio s WHERE s.musica_id = m.id)"
            " ORDER BY m.titulo COLLATE PT"
        ).fetchall(),
        "medias": db.execute(
            f"SELECT m.id, m.titulo, a.nome AS artista, AVG(s.nota) AS media, COUNT(s.nota) AS avaliacoes {JUNTA}"
            " WHERE s.nota IS NOT NULL GROUP BY m.id ORDER BY media DESC, avaliacoes DESC, m.titulo COLLATE PT"
        ).fetchall(),
        "generos": por_genero(r[0] for r in db.execute("SELECT genero FROM musica")),
    }


def por_genero(valores):
    """[(rótulo, quantidade)]: junta 'rock'/'Rock', rótulo = grafia mais usada; sem gênero vira 'Sem gênero'."""
    grupos = {}
    for genero in valores:
        grupos.setdefault(genero.casefold() if genero else None, []).append(genero or "Sem gênero")
    linhas = []
    for grafias in grupos.values():
        contagem = Counter(grafias)
        rotulo = min(contagem, key=lambda g: (-contagem[g], g))  # mais usada; empate: ordem alfabética
        linhas.append((rotulo, len(grafias)))
    return sorted(linhas, key=lambda linha: (-linha[1], _chave(linha[0])))
