"""Carga inicial de demonstração do Shuffle Meu.

Uso: python seed.py
Pode ser rodado várias vezes: não duplica nada e não sobrescreve o que o usuário editou
(itens do seed que foram excluídos voltam a ser criados).
"""

from urllib.parse import quote_plus

from shuffle_meu import create_app
from shuffle_meu.db import get_db

ARTISTAS = [
    ("Legião Urbana", "Brasil"),
    ("Djavan", "Brasil"),
    ("Marisa Monte", "Brasil"),
    ("Jorge Ben Jor", "Brasil"),
    ("Chitãozinho & Xororó", "Brasil"),
    ("The Beatles", "Reino Unido"),
    ("Queen", "Reino Unido"),
    ("Adele", "Reino Unido"),
]

# (título, artista, gênero, humor, dificuldade, favorita, ativa)
MUSICAS = [
    ("Tempo Perdido", "Legião Urbana", "rock", "triste", 2, 1, 1),
    ("Índios", "Legião Urbana", "rock", "calma", 3, 0, 1),
    ("Pais e Filhos", "Legião Urbana", "rock", "triste", 2, 0, 1),
    ("Eduardo e Mônica", "Legião Urbana", "rock", "animada", 3, 1, 1),
    ("Oceano", "Djavan", "MPB", "romantica", 4, 1, 1),
    ("Flor de Lis", "Djavan", "MPB", "animada", 4, 0, 1),
    ("Se...", "Djavan", "MPB", "romantica", 5, 0, 1),
    ("Ainda Bem", "Marisa Monte", "MPB", "romantica", 2, 0, 1),
    ("Amor I Love You", "Marisa Monte", "MPB", "romantica", 3, 0, 1),
    ("Infinito Particular", "Marisa Monte", "MPB", "calma", 3, 0, 1),
    ("País Tropical", "Jorge Ben Jor", "samba", "animada", 2, 1, 1),
    ("Mas Que Nada", "Jorge Ben Jor", "samba", "animada", 3, 0, 1),
    ("Taj Mahal", "Jorge Ben Jor", "samba", "animada", 2, 0, 1),
    ("Evidências", "Chitãozinho & Xororó", "sertanejo", "romantica", 2, 1, 1),
    ("Fio de Cabelo", "Chitãozinho & Xororó", "sertanejo", "triste", 1, 0, 1),
    ("Galopeira", "Chitãozinho & Xororó", "sertanejo", "animada", 5, 0, 1),
    ("Let It Be", "The Beatles", "rock", "calma", 2, 0, 1),
    ("Yesterday", "The Beatles", "rock", "triste", 3, 0, 1),
    ("Here Comes the Sun", "The Beatles", "rock", "animada", 3, 1, 1),
    ("Hey Jude", "The Beatles", "rock", "calma", 1, 0, 1),
    ("Bohemian Rhapsody", "Queen", "rock", "triste", 5, 0, 1),
    ("Love of My Life", "Queen", "rock", "romantica", 4, 0, 1),
    ("We Will Rock You", "Queen", "rock", "animada", 1, 0, 0),  # a única inativa
    ("Someone Like You", "Adele", "pop", "triste", 3, 0, 1),
    ("Rolling in the Deep", "Adele", "pop", "animada", 4, 0, 1),
]

PLAYLISTS = [
    ("Roda de violão", "Fáceis de tocar no violão",
     ["Tempo Perdido", "Pais e Filhos", "Eduardo e Mônica", "Ainda Bem", "Evidências", "Fio de Cabelo",
      "Let It Be", "Hey Jude"]),
    ("Churrasco", "Para animar a galera",
     ["País Tropical", "Mas Que Nada", "Taj Mahal", "Evidências", "Galopeira", "Eduardo e Mônica",
      "We Will Rock You", "Rolling in the Deep"]),
]


def semear(db):
    """Insere os dados de exemplo que ainda não existem, numa única transação."""
    artista_de = {m[0]: m[1] for m in MUSICAS}
    # INSERT OR IGNORE usa as chaves naturais: nome do artista e título + artista da música (RN02)
    db.executemany("INSERT OR IGNORE INTO artista (nome, pais) VALUES (?, ?)", ARTISTAS)
    db.executemany(
        "INSERT OR IGNORE INTO musica (titulo, artista_id, genero, humor, dificuldade, link, favorita, ativa)"
        " SELECT ?, id, ?, ?, ?, ?, ?, ? FROM artista WHERE nome = ?",
        [(t, g, h, d, "https://www.youtube.com/results?search_query=" + quote_plus(f"{t} {a}"), f, at, a)
         for t, a, g, h, d, f, at in MUSICAS],
    )
    for nome, descricao, titulos in PLAYLISTS:
        linha = db.execute("SELECT id FROM playlist WHERE nome = ?", (nome,)).fetchone()  # nome não é UNIQUE
        playlist_id = linha[0] if linha else db.execute(
            "INSERT INTO playlist (nome, descricao) VALUES (?, ?)", (nome, descricao)).lastrowid
        db.executemany(
            "INSERT OR IGNORE INTO playlist_musica (playlist_id, musica_id)"
            " SELECT ?, m.id FROM musica m JOIN artista a ON a.id = m.artista_id WHERE m.titulo = ? AND a.nome = ?",
            [(playlist_id, t, artista_de[t]) for t in titulos],
        )
    db.commit()


if __name__ == "__main__":
    with create_app().app_context():
        db = get_db()
        semear(db)
        totais = [db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("artista", "musica", "playlist")]
        print("Carga inicial concluída: {} artistas, {} músicas, {} playlists no banco.".format(*totais))
