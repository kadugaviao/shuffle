# Proposal: add-mvp

## Why

Quem toca um instrumento ou anima uma roda de amigos acaba repetindo sempre as mesmas músicas, e o aleatório dos aplicativos de streaming toca músicas que a pessoa não conhece (ver `docs/plan.md`, seções 1 e 2). O trabalho de G2 exige um sistema com banco de no mínimo 2 tabelas e CRUD completo, apresentado em 24/11. Esta mudança entrega o MVP da seção 12 do plano: o mínimo que cumpre o escopo e demonstra o sorteio inteligente.

## What Changes

- Cria o banco SQLite com as 5 tabelas da seção 4: `artista`, `musica`, `playlist`, `playlist_musica` e `sorteio`, com as constraints das regras RN01, RN02, RN03, RN07 e a cascata da RN08.
- CRUD completo de **artistas** (cadastrar, listar, editar, excluir; exclusão bloqueada se o artista tiver músicas).
- CRUD completo de **músicas**, com busca por título/artista e filtros por gênero, humor e favorita; marcar favorita e ativar/desativar pela edição.
- CRUD de **playlists**: criar, renomear, excluir, adicionar e remover músicas.
- **Sorteio**: simples (só músicas ativas, RN04), com filtros (gênero, humor, dificuldade máxima, artista, playlist), mensagem amigável quando não há candidatas (RN05), anti-repetição das últimas N rodadas (padrão 5) com o fallback da RN06 e peso 2x para favoritas.
- **Histórico**: cada sorteio é registrado; na tela de resultado o usuário escolhe "Toquei", "Pular" (sorteia de novo e mantém `tocada = falso`) ou "Avaliar" (nota de 1 a 5, só para sorteios tocados, RN07); lista dos últimos sorteios.
- Script `seed.py` de carga inicial (8 artistas, ~25 músicas variadas, 2 playlists), idempotente, para a demonstração.
- README com integrantes, instalação, carga inicial e execução.

### Fora do escopo (trabalho futuro, cada item pode virar uma nova mudança)

- **Estatísticas** (seção 5.3): top 5 mais tocadas, músicas nunca sorteadas, média de notas por música, contagem por gênero.
- **Modo "Esquecidas"** e **Setlist** (seção 5.2): não estão na lista do MVP.
- **Extras** (seção 5.4): modo festa com roleta animada, importar/exportar CSV, botão dedicado "Abrir link", modo desafio.
- Guardar o N da anti-repetição como preferência permanente (no MVP ele é um campo do formulário de sorteio, com padrão 5).
- Exclusão de artista em cascata (no MVP a exclusão é bloqueada enquanto houver músicas).
- Login e múltiplos usuários: o sistema é de uso pessoal, um repertório por instalação.

## Capabilities

### New Capabilities

Nenhuma. As cinco capacidades já foram especificadas antes do código em `openspec/specs/` (abordagem spec-first combinada pelo trio).

### Modified Capabilities

Os deltas usam `MODIFIED` e repetem integralmente os requisitos das specs base, confirmando-os como o comportamento entregue por esta mudança. Ao arquivar, as specs base ficam iguais ao que foi implementado.

- `artistas`: cadastro, listagem, edição e exclusão de artistas; nome único.
- `musicas`: CRUD de músicas com RN01, RN02, RN03 e RN08; busca e filtros do repertório; persistência.
- `playlists`: criação, edição e exclusão de playlists; vínculo N:N com músicas.
- `sorteio`: sorteio simples e com filtros, RN04, RN05, RN06, anti-repetição, peso de favoritas, desempenho e interface responsiva.
- `historico`: registro dos sorteios, Toquei / Pular / Avaliar (RN07), listagem e remoção junto com a música (RN08).

## Impact

- Código novo: pacote Flask `shuffle_meu/` (rotas, templates Jinja, CSS/JS estáticos, `schema.sql`), testes em `tests/`.
- Dependência nova: Flask (única; banco via `sqlite3` da biblioteca padrão).
- Arquivos novos na raiz: `requirements.txt`, `seed.py`, `README.md`, `.gitignore` (ignora `instance/` com o arquivo do banco).
- Nenhum sistema existente é afetado: o repositório ainda não tem código de aplicação.
