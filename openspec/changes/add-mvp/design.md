# Design: add-mvp

## Context

O repositório ainda não tem código: só o plano (`docs/plan.md`) e os artefatos OpenSpec. A motivação e o escopo estão em `proposal.md`; o comportamento esperado está nas specs (`specs/*/spec.md`). Restrições que moldam o design: prazo de ~2 dias até a apresentação (24/11), trio trabalhando em paralelo, stack fixa (Python 3 + Flask, SQLite, Jinja + HTML/CSS/JS puro) e preferência explícita por simplicidade.

## Goals / Non-Goals

**Goals:**
- Um único processo Flask, sem build de front-end, que roda com `pip install -r requirements.txt` e `flask --app shuffle_meu run`.
- Regras de negócio garantidas em dois lugares: validação no Python (mensagem amigável) e constraints no banco (última barreira).
- Algoritmo do sorteio isolado numa função pura, testável sem servidor e sem banco.
- Código dividido por capacidade, para os três integrantes trabalharem em arquivos diferentes.

**Non-Goals:**
- API JSON / SPA: todas as telas são HTML renderizado no servidor.
- Migrações de schema: o banco é criado do zero pelo `schema.sql`; mudança de schema no MVP = apagar `instance/shuffle.db`.
- Autenticação, CSRF token e implantação em servidor público (uso local, um usuário).

## Decisions

### D1. Acesso ao banco: `sqlite3` da biblioteca padrão (sem ORM)

São 5 tabelas e consultas simples. Com `sqlite3` + `row_factory = sqlite3.Row` o SQL fica explícito (bom para a apresentação e para conferir as RN no `schema.sql`) e não há dependência além do Flask.
- *Alternativa:* SQLAlchemy Core. Daria portabilidade para PostgreSQL, que ninguém pediu, e acrescenta uma dependência e uma API a aprender no prazo. Rejeitada.
- Toda conexão executa `PRAGMA foreign_keys = ON`. **Sem isso o SQLite ignora as chaves estrangeiras** e a cascata da RN08 e o bloqueio de exclusão de artista não funcionam.
- Uma conexão por requisição, guardada em `flask.g` e fechada em `teardown_appcontext` (padrão do tutorial oficial do Flask).

### D2. Estrutura de pastas: um pacote, um blueprint por capacidade

```
g2_eng_software/
├── shuffle_meu/
│   ├── __init__.py        # create_app(): config, cria o banco se faltar, registra blueprints, filtro de data
│   ├── db.py              # get_db(), close_db(), init_db()
│   ├── schema.sql         # CREATE TABLE IF NOT EXISTS ... (seção "Schema SQL")
│   ├── artistas.py        # blueprint /artistas
│   ├── musicas.py         # blueprint /musicas  (+ validar_musica())
│   ├── playlists.py       # blueprint /playlists
│   ├── sorteio.py         # blueprint /, /sortear, /sorteios/<id>  (+ escolher(), função pura)
│   ├── historico.py       # blueprint /historico, /sorteios/<id>/toquei, /sorteios/<id>/avaliar
│   ├── templates/
│   │   ├── base.html      # layout, menu, mensagens flash, <meta viewport>
│   │   ├── inicio.html
│   │   ├── artistas/lista.html, artistas/form.html
│   │   ├── musicas/lista.html, musicas/form.html
│   │   ├── playlists/lista.html, playlists/detalhe.html
│   │   ├── sorteio/resultado.html
│   │   └── historico.html
│   └── static/
│       ├── style.css      # mobile-first, sem framework
│       └── app.js         # só a confirmação de exclusão
├── tests/
│   ├── base.py            # TestCase com app + banco temporário
│   ├── test_artistas.py, test_musicas.py, test_playlists.py
│   ├── test_sorteio.py, test_historico.py
│   └── test_seed.py
├── instance/shuffle.db    # criado em tempo de execução (no .gitignore)
├── seed.py                # carga inicial de demonstração (D8)
├── requirements.txt       # Flask
└── README.md
```
- *Alternativa:* um `app.py` único. Menos arquivos, mas três pessoas editando o mesmo arquivo gera conflito de merge o tempo todo. Blueprints são nativos do Flask, sem custo extra.
- O banco é criado em `create_app()` executando `schema.sql` (idempotente por causa do `IF NOT EXISTS`). Assim o professor só precisa de `flask run`, sem comando de inicialização.
- Testes com `unittest` (biblioteca padrão) + `app.test_client()`; rodam com `python -m unittest`. Cada teste usa um arquivo de banco temporário via `create_app({"DATABASE": caminho})`.

### D3. Schema SQL

```sql
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
```
- Booleanos como `INTEGER` 0/1 (o SQLite não tem tipo booleano).
- `CHECK` com `NULL` passa (ex.: `humor` ou `link` vazios), por isso os campos opcionais são gravados como `NULL`, nunca como `''`. O Python converte texto vazio em `None` antes de gravar.
- Datas gravadas em UTC (`CURRENT_TIMESTAMP`) e exibidas em hora local por um filtro Jinja.
- Sem índices extras: com até 1.000 músicas as varreduras completas ficam bem abaixo de 1 s. `AUTOINCREMENT` garante que `sorteio.id` cresce com o tempo, o que a anti-repetição usa para ordenar.
- *Alternativa para artista:* `ON DELETE CASCADE` (o plano permite). Rejeitada no MVP porque apaga músicas e histórico com um clique; `RESTRICT` + mensagem é mais seguro.

### D4. Validação e mensagens

Cada blueprint valida o formulário antes de gravar (`validar_musica(form) -> (dados, erros)` e equivalentes) e, se houver erro, renderiza o mesmo formulário com as mensagens das specs e os dados digitados. As constraints do banco são a segunda barreira: `sqlite3.IntegrityError` de `UNIQUE` é convertido na mensagem de duplicata (RN02 / nome de artista), evitando a corrida "consulta e depois insere". Mensagens de sucesso e avisos usam `flash()`.

### D5. Rotas HTTP por tela (seção 10 do plano)

Formulários HTML só enviam GET e POST, então escrita é sempre `POST` e toda escrita bem-sucedida termina em redirect (Post/Redirect/Get), para F5 não repetir a ação.

| Tela | Método e rota | O que faz |
|---|---|---|
| 1. Início | `GET /` | Formulário de sorteio (gênero, humor, dificuldade máx., artista, playlist, N) e a última música sorteada |
| | `POST /sortear` | Roda o algoritmo (D6), grava o sorteio e redireciona para `/sorteios/<id>`; sem candidatas volta para `/` com a mensagem da RN05 e os filtros na query string |
| 2. Repertório | `GET /musicas?q=&genero=&humor=&favorita=` | Lista com busca e filtros, botões editar e excluir |
| 3. Formulário de música | `GET /musicas/nova`, `POST /musicas/nova` | Cadastro |
| | `GET /musicas/<id>/editar`, `POST /musicas/<id>/editar` | Edição (inclui favorita e ativa) |
| | `POST /musicas/<id>/excluir` | Exclusão (RN08 via cascata) |
| 4. Artistas | `GET /artistas` | Lista com contagem de músicas |
| | `GET /artistas/novo`, `POST /artistas/novo` | Cadastro |
| | `GET /artistas/<id>/editar`, `POST /artistas/<id>/editar` | Edição |
| | `POST /artistas/<id>/excluir` | Exclusão (bloqueada se tiver músicas) |
| 5. Playlists | `GET /playlists`, `POST /playlists` | Lista e criação (formulário na própria lista) |
| | `GET /playlists/<id>` | Detalhe: músicas da playlist + seletor para adicionar + formulário de editar nome/descrição |
| | `POST /playlists/<id>/editar` | Renomear / alterar descrição |
| | `POST /playlists/<id>/excluir` | Exclusão (vínculos em cascata) |
| | `POST /playlists/<id>/musicas` | Adiciona a música `musica_id` do formulário |
| | `POST /playlists/<id>/musicas/<musica_id>/remover` | Remove a música da playlist |
| 6. Resultado do sorteio | `GET /sorteios/<id>?<filtros>` | Música, artista, link (nova aba, `rel="noopener"`), aviso da RN06 se houver, botões |
| | "Pular" → `POST /sortear` | O formulário do botão reenvia os filtros e o N em campos ocultos; o sorteio atual já está com `tocada = 0`, então pular não precisa de rota própria |
| | `POST /sorteios/<id>/toquei` | `tocada = 1`, volta para o resultado |
| | `POST /sorteios/<id>/avaliar` | Grava `nota` (RN07), volta para o resultado |
| 7. Histórico | `GET /historico` | Últimos 50 sorteios; cada linha abre `/sorteios/<id>` |

- O botão "Avaliar" é um pequeno formulário com nota 1–5 que só aparece habilitado depois de "Toquei"; o servidor valida a RN07 de qualquer forma (requisições podem ser forjadas).
- Exclusões usam `<form method="post" data-confirmar="...">`; o `app.js` chama `confirm()` no `submit` e cancela se o usuário recusar.
- Os filtros vão na query string do resultado só para o botão "Pular" poder reenviá-los; o resultado não depende deles.
- Rota de id inexistente responde 404.

### D6. Algoritmo do sorteio

Entrada: filtros do formulário e N (inteiro de 0 a 50; qualquer outro valor vira 5).

1. **Filtros:** monta um único `SELECT m.id, m.favorita FROM musica m WHERE ...` com parâmetros `?` (nunca concatenando texto do usuário), acrescentando só os filtros preenchidos:
   `m.genero = ? COLLATE NOCASE`, `m.humor = ?`, `m.dificuldade <= ?`, `m.artista_id = ?`, `m.id IN (SELECT musica_id FROM playlist_musica WHERE playlist_id = ?)`.
2. **Remove inativas (RN04):** o mesmo `WHERE` inclui `m.ativa = 1`. Como os critérios são combinados por `AND`, a ordem filtros → ativas não muda o resultado; fazer tudo numa consulta evita trazer o repertório inteiro para o Python.
3. **Vazio → RN05:** sem candidatas, retorna a mensagem amigável e **não** grava sorteio.
4. **Anti-repetição com fallback (RN06):** `recentes = {musica_id das últimas N linhas de sorteio, ORDER BY id DESC LIMIT N}` (global, independente dos filtros, inclui pulados). `livres = candidatas − recentes`. Se `livres` ficar vazio, usa todas as candidatas e define o aviso "Você já tocou todas recentemente!".
5. **Peso 2x para favoritas:** `random.choices(livres, weights=[2 if favorita else 1 ...], k=1)`.
6. Grava `INSERT INTO sorteio (musica_id)` e redireciona para o resultado, levando o aviso por `flash()`.

Os passos 4 e 5 ficam em `escolher(candidatas, recentes, rng=random) -> (musica, aviso)`, função pura que os testes chamam com um `random.Random(semente)` para verificar anti-repetição, fallback e a proporção de ~2/3 das favoritas sem depender do acaso.

### D7. Front-end

`base.html` com `<meta name="viewport" content="width=device-width, initial-scale=1">`, menu simples (Início, Repertório, Artistas, Playlists, Histórico) e área de mensagens flash. CSS mobile-first em um arquivo: colunas empilhadas abaixo de 600 px, tabelas do repertório e do histórico viram cartões no celular, botão "Sortear" grande. Jinja escapa HTML por padrão, o que protege os campos de texto livre; o link só é exibido porque passou pela validação http/https.

### D8. Carga inicial: `seed.py` idempotente

Script na raiz, rodado com `python seed.py`. Ele usa `create_app()` e `get_db()`, ou seja, o mesmo banco, schema e `PRAGMA` da aplicação, e grava tudo numa única transação. O conteúdo fica em listas Python dentro do próprio script (sem CSV):
- 8 artistas; 25 músicas cobrindo pelo menos 4 gêneros, os 4 humores e as dificuldades de 1 a 5, com algumas favoritas e exatamente 1 inativa; 2 playlists ("Roda de violão" e "Churrasco") com músicas vinculadas.
- **Idempotência pelas chaves naturais:** artistas por `nome` (UNIQUE), músicas por `(titulo, artista_id)` (RN02) e vínculos por `(playlist_id, musica_id)` usam `INSERT OR IGNORE`. A playlist não tem nome único, por isso é procurada por `nome` antes de ser inserida. Rodar duas vezes não duplica nada, e dados que o usuário editou não são sobrescritos. Se o usuário excluiu um item do seed, rodar o script de novo recria esse item.
- `INSERT OR IGNORE` do SQLite também descarta em silêncio as linhas que violam um `CHECK`. Por isso o teste confere as contagens exatas depois da carga: uma música de exemplo inválida derruba o teste em vez de sumir sem aviso.
- A lógica fica em `semear(db)`, separada do bloco `__main__`, para o teste chamá-la sobre um banco temporário.
- *Alternativa:* comando `flask seed` via `app.cli`. Rejeitada porque o trio pediu um script `seed.py`, que também é mais fácil de explicar no README.

## Risks / Trade-offs

- [`COLLATE NOCASE` do SQLite só ignora maiúsculas em letras ASCII: "LEGIÃO" e "legião" não colidem pelo banco] → a validação em Python compara com `casefold()` antes de gravar; o banco segura os casos ASCII.
- [Esquecer `PRAGMA foreign_keys = ON` desliga a RN08 em silêncio] → feito em `get_db()`, único ponto de abertura de conexão, e coberto por teste que exclui uma música e confere histórico e playlist.
- [Anti-repetição global: com filtros muito restritos, músicas sorteadas em outros filtros também ficam bloqueadas] → é o comportamento da spec ("últimas N rodadas"); o fallback da RN06 impede que o sorteio trave.
- [Sem token CSRF, outro site poderia enviar POSTs para o servidor local] → aceito para uso local de um usuário; registrado como dívida no README.
- [Mudança de schema exige apagar o banco] → aceitável no MVP, sem dados reais; o README explica.
- [Teste de desempenho com 1.000 músicas depende da máquina] → limite de 1 s é folgado para SQLite local; o teste mede só o tempo do servidor (test client), não a rede.

## Migration Plan

Não há sistema anterior. Implantação = clonar, instalar o Flask e rodar; o banco nasce vazio. Rollback = voltar o commit e apagar `instance/shuffle.db`.
