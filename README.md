# Shuffle Meu 🎵

Sistema web para cadastrar as músicas que você **já conhece** e **sortear qual tocar** a seguir. O sorteio só usa músicas ativas, aceita filtros (gênero, humor, dificuldade máxima, artista, playlist), evita repetir as últimas N sorteadas e dá o dobro de chance às favoritas.

Trabalho de G2 da disciplina de Engenharia de Software, desenvolvido com **OpenSpec** (especificar antes de programar).

## Integrantes

- Kadu Brum Gavião
- Miguel Mombach Foza
- Josiel Paz

## Pré-requisitos

- Python 3 (testado com 3.12)

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Carga inicial (opcional)

```bash
python seed.py
```

Cria dados de exemplo para a demonstração: 8 artistas, 25 músicas (rock, MPB, samba, sertanejo e pop; os 4 humores; dificuldades de 1 a 5; 6 favoritas e 1 inativa) e as playlists "Roda de violão" e "Churrasco".

- Pode ser rodado mais de uma vez: não duplica nada e não sobrescreve o que você editou.
- Itens do seed que você excluiu **voltam a ser criados** se rodar de novo.

## Execução

```bash
flask --app shuffle_meu run
```

Abra http://127.0.0.1:5000. O banco SQLite é criado sozinho em `instance/shuffle.db` na primeira execução.

## Testes

```bash
python -m unittest
```

## Zerar o banco

Pare o servidor e apague o arquivo `instance/shuffle.db`. Ele é recriado vazio na próxima execução; rode `python seed.py` se quiser os dados de exemplo de novo. O mesmo vale se o `schema.sql` mudar: não há migrações.

## Estrutura

```
shuffle_meu/
  __init__.py      create_app(): configuração, banco e blueprints
  db.py            conexão SQLite (foreign_keys ligado)
  schema.sql       as 5 tabelas e as regras de negócio no banco
  artistas.py      CRUD de artistas
  musicas.py       CRUD de músicas e validações
  playlists.py     playlists e suas músicas
  sorteio.py       algoritmo do sorteio e tela de resultado
  historico.py     Toquei / Avaliar e lista de sorteios
  templates/       telas (Jinja)
  static/          CSS e JS
tests/             testes (unittest)
seed.py            carga inicial
openspec/          especificação (specs, proposta, design e tarefas)
```

## Especificação (OpenSpec)

Os requisitos, as regras de negócio RN01 a RN08 e os cenários de cada funcionalidade estão em [`openspec/specs/`](openspec/specs/). A mudança que implementou o MVP está arquivada em [`openspec/changes/archive/2026-11-22-add-mvp/`](openspec/changes/archive/2026-11-22-add-mvp/).

```bash
openspec validate --specs --strict
```

## Limitações conhecidas

- Feito para uso local por uma pessoa: não há login nem proteção CSRF. Não publique o servidor na internet sem adicionar isso e definir a variável de ambiente `SECRET_KEY`.
- A anti-repetição vale para o histórico inteiro, independentemente dos filtros usados no sorteio.
- Estatísticas, modo "Esquecidas", setlist e os extras do plano ficaram para trabalhos futuros (ver [`proposal.md`](openspec/changes/archive/2026-11-22-add-mvp/proposal.md) da mudança arquivada).
