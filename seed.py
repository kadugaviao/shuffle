"""Carga inicial de demonstração do Shuffle.

Uso: python seed.py
Pode ser rodado várias vezes: não duplica nada e não sobrescreve o que o usuário editou
(itens do seed que foram excluídos voltam a ser criados).
"""

from urllib.parse import quote_plus

from shuffle_meu import create_app
from shuffle_meu.db import get_db

ARTISTAS = [
    ("The Beatles", "Reino Unido"),
    ("Guns N' Roses", "Estados Unidos"),
    ("AC/DC", "Austrália"),
    ("Barão Vermelho", "Brasil"),
    ("Legião Urbana", "Brasil"),
    ("Titãs", "Brasil"),
    ("Metallica", "Estados Unidos"),
    ("Rammstein", "Alemanha"),
    ("Avenged Sevenfold", "Estados Unidos"),
    ("Adoniran Barbosa", "Brasil"),
    ("Seu Jorge", "Brasil"),
    ("Martinho da Vila", "Brasil"),
    ("Chitãozinho & Xororó", "Brasil"),
    ("Bruno & Marrone", "Brasil"),
    ("Zezé Di Camargo & Luciano", "Brasil"),
    ("Tim Maia", "Brasil"),
    ("Chico Buarque", "Brasil"),
    ("Djavan", "Brasil"),
]

# (título, artista, gênero, humor, dificuldade, favorita, ativa). Lista escolhida pelo trio (add-links-por-servico, D5b),
# mais duas calmas de bandas já presentes para o filtro "calma" não ficar com uma música só.
MUSICAS = [
    ("Here Comes the Sun", "The Beatles", "rock", "calma", 3, 1, 1),
    ("Sweet Child O' Mine", "Guns N' Roses", "rock", "animada", 5, 0, 1),
    ("Back in Black", "AC/DC", "rock", "animada", 4, 0, 1),
    ("Patience", "Guns N' Roses", "rock", "calma", 3, 0, 0),  # a única inativa
    ("Bete Balanço", "Barão Vermelho", "rock brasileiro", "animada", 3, 0, 1),
    ("Tempo Perdido", "Legião Urbana", "rock brasileiro", "triste", 2, 1, 1),
    ("Sonífera Ilha", "Titãs", "rock brasileiro", "animada", 2, 0, 1),
    ("Creeping Death", "Metallica", "metal", "animada", 5, 0, 1),
    ("Sonne", "Rammstein", "metal", "animada", 3, 0, 1),
    ("Nightmare", "Avenged Sevenfold", "metal", "animada", 5, 0, 1),
    ("Nothing Else Matters", "Metallica", "metal", "calma", 3, 0, 1),
    ("Trem das Onze", "Adoniran Barbosa", "samba", "animada", 2, 1, 1),
    ("Mina do Condomínio", "Seu Jorge", "samba", "animada", 2, 0, 1),
    ("Canta, Canta, Minha Gente", "Martinho da Vila", "samba", "animada", 1, 0, 1),
    ("Evidências", "Chitãozinho & Xororó", "sertanejo", "romantica", 2, 1, 1),
    ("Boate Azul", "Bruno & Marrone", "sertanejo", "triste", 1, 0, 1),
    ("É o Amor", "Zezé Di Camargo & Luciano", "sertanejo", "romantica", 1, 0, 1),
    ("Descobridor dos Sete Mares", "Tim Maia", "MPB", "animada", 3, 0, 1),
    ("Construção", "Chico Buarque", "MPB", "triste", 4, 0, 1),
    ("Samurai", "Djavan", "MPB", "romantica", 4, 1, 1),
]

# Links verificados no Chrome com tools/verificar_links.py (ver docs/links-verificados.md, com data e tipo de vídeo).
# (youtube, spotify); None quando não houve link que passasse na verificação. Nenhum ID foi escrito de memória.
LINKS = {
    'Here Comes the Sun': (None, 'https://open.spotify.com/track/6dGnYIeXmHdcikdzNNDMm2'),
    "Sweet Child O' Mine": (None, 'https://open.spotify.com/track/7snQQk1zcKl8gZ92AnueZW'),
    'Back in Black': (None, 'https://open.spotify.com/track/08mG3Y1vljYA6bvDt4Wqkj'),
    'Patience': (None, 'https://open.spotify.com/track/2uKcU4FPX5eOjmd6RWb9OF'),
    'Bete Balanço': (None, 'https://open.spotify.com/track/545yUenhKzU5ndLVCtnn7m'),
    'Tempo Perdido': ('https://www.youtube.com/watch?v=ilybyuWjBGY', 'https://open.spotify.com/track/7B5ZOuMdaxYvn2px1dHUEi'),
    'Sonífera Ilha': ('https://www.youtube.com/watch?v=aBrEIgQyd9Q', 'https://open.spotify.com/track/5NtT8MYB3S2Vw8ko5NNa6Z'),
    'Creeping Death': (None, 'https://open.spotify.com/track/1Gn1FeIYUMZ2a7PrbaaQhl'),
    'Sonne': (None, 'https://open.spotify.com/track/3gVhsZtseYtY1fMuyYq06F'),
    'Nightmare': (None, 'https://open.spotify.com/track/5meaBghEX13kjojRrLmncU'),
    'Nothing Else Matters': (None, 'https://open.spotify.com/track/2CtemffYhT0DJWcT1XW047'),
    'Trem das Onze': ('https://www.youtube.com/watch?v=4IqD4hK3D_c', 'https://open.spotify.com/track/7vx5AIzcGwFoUwTzeFEMna'),
    'Mina do Condomínio': (None, 'https://open.spotify.com/track/5aGx8GTUwagGMMqt2btrH4'),
    'Canta, Canta, Minha Gente': (None, 'https://open.spotify.com/track/5VwEjqrI6E5tE7gMtuyflM'),
    'Evidências': ('https://www.youtube.com/watch?v=tMOPMfcW_6Q', 'https://open.spotify.com/track/5FTGXGd1oPB2CRss5FbA4r'),
    'Boate Azul': (None, 'https://open.spotify.com/track/0Zx6LJJI4o6loyPi8T7ksI'),
    'É o Amor': (None, 'https://open.spotify.com/track/3oMk1VNl1N7dgibHwHw1j2'),
    'Descobridor dos Sete Mares': (None, 'https://open.spotify.com/track/4Mm9qSuCRoMl8H4yByoaNS'),
    'Construção': (None, 'https://open.spotify.com/track/1ECean5dVz7mYQ07mdVGKT'),
    'Samurai': (None, 'https://open.spotify.com/track/3BQAK2pnTpfZvLg2MUUU5i'),
}


def busca_youtube(titulo, artista):
    """Busca do YouTube que fica no "Outro link" quando a música não tem vídeo verificado."""
    return "https://www.youtube.com/results?search_query=" + quote_plus(f"{titulo} {artista}")


PLAYLISTS = [
    ("Roda de violão", "Fáceis de tocar no violão",
     ["Tempo Perdido", "Here Comes the Sun", "Evidências", "É o Amor", "Boate Azul", "Trem das Onze", "Samurai",
      "Patience"]),
    ("Churrasco", "Para animar a galera",
     ["Mina do Condomínio", "Canta, Canta, Minha Gente", "Bete Balanço", "Sonífera Ilha", "Evidências", "Boate Azul",
      "Descobridor dos Sete Mares", "Back in Black"]),
]

def semear(db):
    """Insere os dados de exemplo que ainda não existem, numa única transação."""
    artista_de = {m[0]: m[1] for m in MUSICAS}
    # INSERT OR IGNORE usa as chaves naturais: nome do artista e título + artista da música (RN02)
    db.executemany("INSERT OR IGNORE INTO artista (nome, pais) VALUES (?, ?)", ARTISTAS)
    linhas = []
    for t, a, g, h, d, f, at in MUSICAS:
        youtube, spotify = LINKS.get(t, (None, None))
        linhas.append((t, g, h, d, None if youtube else busca_youtube(t, a), youtube, spotify, f, at, a))
    db.executemany(
        "INSERT OR IGNORE INTO musica (titulo, artista_id, genero, humor, dificuldade, link, youtube, spotify, favorita, ativa)"
        " SELECT ?, id, ?, ?, ?, ?, ?, ?, ?, ? FROM artista WHERE nome = ?",
        linhas,
    )
    _completar_links(db)
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


def _completar_links(db):
    """Bancos que já tinham as músicas do seed (o INSERT OR IGNORE não as altera): preenche youtube e spotify só
    onde estão vazios, e limpa o "Outro link" só se ainda for a busca gerada pelo seed (design D5)."""
    musica = "id = (SELECT m.id FROM musica m JOIN artista a ON a.id = m.artista_id WHERE m.titulo = ? AND a.nome = ?)"
    for t, a, *_ in MUSICAS:
        youtube, spotify = LINKS.get(t, (None, None))
        if youtube:
            db.execute(f"UPDATE musica SET youtube = ? WHERE youtube IS NULL AND {musica}", (youtube, t, a))
            db.execute(f"UPDATE musica SET link = NULL WHERE link = ? AND youtube = ? AND {musica}",
                       (busca_youtube(t, a), youtube, t, a))
        if spotify:
            db.execute(f"UPDATE musica SET spotify = ? WHERE spotify IS NULL AND {musica}", (spotify, t, a))


if __name__ == "__main__":
    with create_app().app_context():
        db = get_db()
        semear(db)
        totais = [db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("artista", "musica", "playlist")]
        print("Carga inicial concluída: {} artistas, {} músicas, {} playlists no banco.".format(*totais))
