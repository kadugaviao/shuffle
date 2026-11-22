-- Schema do Shuffle (design.md D3). Idempotente: roda a cada início da aplicação.

CREATE TABLE IF NOT EXISTS artista (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT    NOT NULL UNIQUE COLLATE NOCASE CHECK (trim(nome) <> ''),
    pais       TEXT,
    criado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS musica (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo       TEXT    NOT NULL COLLATE NOCASE CHECK (trim(titulo) <> ''),          -- RN01
    artista_id   INTEGER NOT NULL REFERENCES artista(id) ON DELETE RESTRICT,           -- RN01; bloqueia excluir artista com músicas
    genero       TEXT,
    humor        TEXT    CHECK (humor IN ('animada', 'calma', 'triste', 'romantica')),
    dificuldade  INTEGER NOT NULL DEFAULT 3 CHECK (dificuldade BETWEEN 1 AND 5),       -- RN03
    link         TEXT    CHECK (link LIKE 'http://%' OR link LIKE 'https://%'),
    favorita     INTEGER NOT NULL DEFAULT 0 CHECK (favorita IN (0, 1)),
    ativa        INTEGER NOT NULL DEFAULT 1 CHECK (ativa IN (0, 1)),
    criado_em    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (titulo, artista_id)                                                        -- RN02 (usa o COLLATE NOCASE de titulo)
);

CREATE TABLE IF NOT EXISTS playlist (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT NOT NULL CHECK (trim(nome) <> ''),
    descricao  TEXT
);

CREATE TABLE IF NOT EXISTS playlist_musica (
    playlist_id  INTEGER NOT NULL REFERENCES playlist(id) ON DELETE CASCADE,
    musica_id    INTEGER NOT NULL REFERENCES musica(id)   ON DELETE CASCADE,          -- RN08
    PRIMARY KEY (playlist_id, musica_id)                                               -- sem música repetida na playlist
);

CREATE TABLE IF NOT EXISTS sorteio (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    musica_id    INTEGER NOT NULL REFERENCES musica(id) ON DELETE CASCADE,            -- RN08
    sorteado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tocada       INTEGER NOT NULL DEFAULT 0 CHECK (tocada IN (0, 1)),
    nota         INTEGER CHECK (nota BETWEEN 1 AND 5),
    CHECK (nota IS NULL OR tocada = 1)                                                 -- RN07
);
