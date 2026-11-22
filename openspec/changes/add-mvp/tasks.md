# Tasks: add-mvp

Referências: comportamento em `specs/*/spec.md`, decisões em `design.md` (D1–D8). Testes com `python -m unittest` a partir da raiz do repositório.

## 1. Projeto e banco

- [ ] 1.1 Criar `requirements.txt` (Flask) e `.gitignore` (`instance/`, `__pycache__/`, `.venv/`); verificar que `pip install -r requirements.txt` instala sem erro num venv limpo
- [ ] 1.2 Criar `shuffle_meu/schema.sql` com as 5 tabelas exatamente como em design.md D3; verificar com `python -c "import sqlite3; sqlite3.connect(':memory:').executescript(open('shuffle_meu/schema.sql').read())"` sem erro
- [ ] 1.3 Criar `shuffle_meu/db.py` (`get_db` com `sqlite3.Row` e `PRAGMA foreign_keys = ON`, `close_db`, `init_db`) e `shuffle_meu/__init__.py` com `create_app(config=None)` que cria `instance/`, roda o schema e registra `close_db`; verificar que `flask --app shuffle_meu run` sobe e cria `instance/shuffle.db` com as 5 tabelas (`SELECT name FROM sqlite_master WHERE type='table'`)
- [ ] 1.4 Criar `tests/base.py` (TestCase com app em banco temporário e `test_client`) e `tests/test_schema.py` que confere: CHECK de dificuldade 0/6 (RN03), UNIQUE título+artista (RN02), CHECK nota sem tocada (RN07), `foreign_keys` ligado; verificar que `python -m unittest` passa
- [ ] 1.5 Criar `templates/base.html` (viewport, menu Início/Repertório/Artistas/Playlists/Histórico, mensagens flash), `static/style.css` mobile-first e `static/app.js` (confirmação em `form[data-confirmar]`), mais o filtro Jinja de data UTC → hora local; verificar abrindo `/` com o menu e sem rolagem horizontal a 360 px no modo responsivo do navegador

## 2. CRUD de artistas

- [ ] 2.1 Blueprint `artistas.py` com `GET /artistas` (ordem alfabética, contagem de músicas, mensagem de lista vazia) e template `artistas/lista.html`; verificar com teste da spec "Listar artistas" (ordem e contagem)
- [ ] 2.2 `GET/POST /artistas/novo` e template `artistas/form.html`, com trim, nome obrigatório e nome único sem diferenciar maiúsculas (inclusive acentos, via `casefold()`); verificar com testes dos cenários "Cadastro válido", "Nome vazio" e "Nome repetido"
- [ ] 2.3 `GET/POST /artistas/<id>/editar` reaproveitando o form e as validações, 404 para id inexistente; verificar com teste "Edição válida" e edição para nome repetido
- [ ] 2.4 `POST /artistas/<id>/excluir` com `data-confirmar`; bloquear se houver músicas, com a mensagem da spec; verificar com testes "Artista sem músicas" e "Artista com músicas" e, no navegador, que cancelar o `confirm()` mantém o artista

## 3. CRUD de músicas

- [ ] 3.1 Função `validar_musica(form)` em `musicas.py`: trim, RN01 (título e artista), RN03 (1–5, padrão 3), humor da lista, link http/https, vazios viram `None`; verificar com testes unitários para cada mensagem de erro da spec
- [ ] 3.2 `GET/POST /musicas/nova` e template `musicas/form.html` (select de artistas, select de humor, dificuldade preenchida com 3, link, checkboxes favorita/ativa só na edição); verificar com teste "Cadastro válido" (ativa = 1, favorita = 0) e que erro mantém os dados digitados
- [ ] 3.3 Tratar duplicata RN02 (checagem com `casefold()` + captura de `IntegrityError`) no cadastro e na edição; verificar com testes "Duplicata rejeitada" e "Mesmo título, outro artista"
- [ ] 3.4 `GET /musicas` com busca `q` (título ou artista, sem diferenciar maiúsculas), filtros gênero, humor e só favoritas, e mensagem "Nenhuma música encontrada."; template `musicas/lista.html` com editar/excluir; verificar com testes "Busca por artista", "Filtros combinados" e "Nada encontrado"
- [ ] 3.5 `GET/POST /musicas/<id>/editar` com favorita e ativa, 404 para id inexistente; verificar com testes "Marcar favorita e desativar" e "Edição inválida" (dificuldade 7 não grava)
- [ ] 3.6 `POST /musicas/<id>/excluir` com `data-confirmar`; verificar com teste "Exclusão remove histórico e vínculos (RN08)" inserindo sorteios e vínculo direto no banco antes de excluir
- [ ] 3.7 Verificar a persistência: teste que cria música, recria o app sobre o mesmo arquivo de banco e encontra a música (cenário "Reinício do servidor")

## 4. Playlists

- [ ] 4.1 Blueprint `playlists.py` com `GET /playlists` (ordem alfabética, contagem) e `POST /playlists` (nome obrigatório, descrição opcional); template `playlists/lista.html`; verificar com testes "Criação válida", "Nome vazio" e "Lista com contagem"
- [ ] 4.2 `GET /playlists/<id>` (músicas da playlist, seletor com as músicas que ainda não estão nela, formulário de edição) e `POST /playlists/<id>/editar`; template `playlists/detalhe.html`; verificar com teste "Renomear"
- [ ] 4.3 `POST /playlists/<id>/musicas` (adicionar; repetida mostra "Essa música já está na playlist.") e `POST /playlists/<id>/musicas/<musica_id>/remover`; verificar com testes "Adicionar", "Adicionar repetida", "Mesma música em várias playlists" e "Remover"
- [ ] 4.4 `POST /playlists/<id>/excluir` com `data-confirmar`; verificar com teste "Exclusão mantém as músicas"

## 5. Sorteio

- [ ] 5.1 Função pura `escolher(candidatas, recentes, rng)` em `sorteio.py` (anti-repetição, fallback RN06 com aviso, peso 2x); verificar com testes usando `random.Random(semente)`: música recente nunca sai, todas bloqueadas sorteia com aviso, favorita entre 60% e 73% em 3.000 rodadas
- [ ] 5.2 Função que lê e normaliza os filtros e o N (0–50, senão 5) e monta a consulta parametrizada de candidatas com `ativa = 1` (design.md D6 passos 1–2); verificar com testes "Só ativas participam (RN04)", "Filtro por humor e dificuldade", "Filtro por playlist", "Filtro por artista" e "N inválido"
- [ ] 5.3 `GET /` com o formulário de filtros (selects de gênero vindos do banco, humor, artista, playlist; dificuldade máx.; N com padrão 5) e template `inicio.html`; verificar abrindo `/` e vendo os filtros preenchidos a partir da query string
- [ ] 5.4 `POST /sortear`: RN05 (redireciona para `/` com a mensagem e os filtros, sem gravar), grava o sorteio, aviso RN06 por flash e redirect para `/sorteios/<id>`; verificar com testes "Filtro sem resultado (RN05)", "Repertório vazio (RN05)", "Música recente é ignorada", "Bloqueio expira depois de N rodadas" e "Todas as músicas bloqueadas (RN06)"
- [ ] 5.5 `GET /sorteios/<id>` e template `sorteio/resultado.html` (título, artista, link em nova aba, botões Toquei / Pular / Avaliar; Pular reenvia filtros e N em campos ocultos para `/sortear`); verificar com teste "Tela de resultado" e 404 para id inexistente
- [ ] 5.6 Teste de desempenho: 1.000 músicas e 1.000 sorteios inseridos em lote, `POST /sortear` com filtros em menos de 1 s (cenário "Repertório grande")
- [ ] 5.7 Verificar a interface responsiva: no modo responsivo do navegador a 360 px, Início e Resultado sem rolagem horizontal e botões utilizáveis (cenário "Sorteio pelo celular")

## 6. Histórico

- [ ] 6.1 Verificar o registro: teste "Novo registro" (sorteio gravado com `tocada = 0`) e "Recarregar o resultado" (GET repetido de `/sorteios/<id>` não cria linha)
- [ ] 6.2 Blueprint `historico.py` com `POST /sorteios/<id>/toquei`; resultado passa a mostrar "Tocada" e habilita "Avaliar"; verificar com teste "Toquei"
- [ ] 6.3 `POST /sorteios/<id>/avaliar` com nota 1–5 só se tocada (RN07), substituindo nota anterior; verificar com testes "Avaliar música tocada (RN07)", "Avaliar sem ter tocado (RN07)" e "Nota fora da faixa"
- [ ] 6.4 Verificar o "Pular": teste que sorteia com humor "calma" e N = 5, envia o POST do botão Pular e confere que o primeiro sorteio continua com `tocada = 0` e o novo é de outra música calma (cenário "Pular")
- [ ] 6.5 `GET /historico` (50 mais recentes, hora local, situação, nota, link para `/sorteios/<id>`, mensagem de histórico vazio) e template `historico.html`; verificar com testes "Ordem e conteúdo" e "Histórico vazio"
- [ ] 6.6 Mostrar a última sorteada em `inicio.html`; verificar com teste "Com sorteio anterior" e teste "Exclusão da música (RN08)" (sorteios somem do histórico e da anti-repetição)

## 7. Carga inicial

- [ ] 7.1 Criar `seed.py` com `semear(db)` e bloco `__main__` (design.md D8): 8 artistas, 25 músicas (pelo menos 4 gêneros, os 4 humores, dificuldades de 1 a 5, pelo menos 4 favoritas, exatamente 1 inativa) e as playlists "Roda de violão" e "Churrasco" com músicas, tudo idempotente; verificar com `tests/test_seed.py`, que roda `semear` duas vezes num banco temporário e confere 8 artistas, 25 músicas, 2 playlists, o mesmo número de vínculos nas duas execuções, 1 inativa, os 4 humores e as dificuldades de 1 a 5
- [ ] 7.2 Verificar no banco real: `python seed.py` duas vezes seguidas, sem erro, e `/musicas` mostra 25 músicas e `/playlists` mostra 2 playlists

## 8. README e verificação final

- [ ] 8.1 Escrever `README.md`: nome do projeto, integrantes do trio, pré-requisitos (Python 3), instalação (`python -m venv .venv`, `pip install -r requirements.txt`), carga inicial opcional (`python seed.py`: o que cria, que pode ser rodado mais de uma vez sem duplicar e que recria itens do seed excluídos), execução (`flask --app shuffle_meu run`), testes (`python -m unittest`), como zerar o banco, limitações conhecidas (sem CSRF, uso local) e link para `openspec/`; verificar seguindo o README do zero num clone limpo
- [ ] 8.2 Verificação de ponta a ponta no navegador, partindo do banco com o seed: sortear com filtro de playlist, pular, marcar Toquei, avaliar, conferir histórico, cadastrar um artista e uma música novos, excluir uma música e conferir que some do histórico e da playlist; `python -m unittest`, `openspec validate add-mvp --strict` e `openspec validate --specs --strict` sem erros

## Workflow follow-up

- Revisão do trio sobre o código entregue em relação às specs.
- Arquivar a mudança com `openspec archive add-mvp` e conferir que `openspec/specs/` continua válido (`openspec validate --specs`).
- Conferir no histórico do Git que os commits das specs vêm antes dos commits de código.
