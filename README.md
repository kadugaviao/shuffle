# Shuffle

Sistema web para cadastrar as músicas que você **já conhece** e **sortear qual tocar** a seguir. O sorteio só usa músicas ativas, aceita filtros (gênero, humor, dificuldade máxima, artista, playlist), evita repetir as últimas N sorteadas e dá o dobro de chance às favoritas. A tela de histórico mostra as estatísticas: músicas mais tocadas, nunca sorteadas, média de notas e músicas por gênero. Cada música pode ter três links: um vídeo do YouTube (inclusive YouTube Music), uma faixa do Spotify e um "Outro link" (cifra, letra, busca). No resultado do sorteio há um botão para abrir cada link preenchido ("Abrir no YouTube", "Abrir no Spotify", "Abrir link") e o player embutido toca a música na própria tela: "Ouvir aqui" quando há um serviço, ou "Ouvir no YouTube" / "Ouvir no Spotify" quando há os dois.

A interface segue o design system "Lambe-lambe", inspirado nos cartazes de show colados nos muros e na folha de setlist presa com fita no chão do palco: papel, tinta, amarelo e vermelho chapados, letras condensadas gigantes e listas com réguas no lugar de cartões. Funciona no celular a partir de 360 px, respeita a preferência de movimento reduzido e não depende de internet: fontes e ícones são servidos pelo próprio sistema.

Trabalho de G2 da disciplina de Engenharia de Software, desenvolvido com **OpenSpec** (especificar antes de programar).

## Telas

| Início | Resultado do sorteio | Histórico e estatísticas |
|---|---|---|
| ![Início no celular](docs/screenshots/inicio-celular.webp) | ![Resultado no celular](docs/screenshots/resultado-celular.webp) | ![Histórico no celular](docs/screenshots/historico-celular.webp) |

Mais capturas, no celular e no desktop, em [`docs/screenshots/`](docs/screenshots/).

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

Cria dados de exemplo para a demonstração: 18 artistas, 20 músicas (rock, rock brasileiro, metal, samba, sertanejo e MPB; os 4 humores; dificuldades de 1 a 5; 5 favoritas e 1 inativa) e as playlists "Roda de violão" e "Churrasco". Todas as músicas têm a faixa do Spotify e quatro têm vídeo do YouTube que toca no player ("Tempo Perdido", "Sonífera Ilha", "Trem das Onze" e "Evidências"); as demais ficam com uma busca do YouTube no "Outro link", porque os vídeos oficiais bloqueiam a incorporação. Os links foram conferidos no navegador e estão documentados em [`docs/links-verificados.md`](docs/links-verificados.md).

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

## Comandos úteis

Conferir se links do YouTube e do Spotify tocam no player embutido (precisa de internet e do Google Chrome; não faz parte dos testes automáticos):

```bash
python tools/verificar_links.py "https://youtu.be/<ID>" "https://open.spotify.com/track/<ID>"
python tools/verificar_links.py --arquivo links.txt   # um link por linha
```

Para cada link, a ferramenta abre o player como o app abre e mostra `OK` ou `FALHA` com o texto que aparece no player (título e canal ou artista), para conferir se é a música certa. Vídeos que bloqueiam incorporação aparecem como `FALHA`. Foi com ela que os links do seed foram verificados (ver [`docs/links-verificados.md`](docs/links-verificados.md)).

## Zerar o banco

Pare o servidor e apague o arquivo `instance/shuffle.db`. Ele é recriado vazio na próxima execução; rode `python seed.py` se quiser os dados de exemplo de novo. O mesmo vale se o `schema.sql` mudar: não há migrações. A exceção são as colunas de link por serviço (`youtube` e `spotify`): um banco criado antes delas as recebe sozinho, vazias, na próxima vez que o app inicia, sem perder músicas. Recriar o banco pelo seed também funciona e já traz os links verificados.

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
  historico.py     Toquei / Avaliar e tela de histórico
  estatisticas.py  consultas das estatísticas
  templates/       telas (Jinja)
  static/          CSS (design system), JS e fontes (static/fonts)
tests/             testes (unittest)
seed.py            carga inicial
openspec/          especificação (specs, proposta, design e tarefas)
```

## Especificação (OpenSpec)

Os requisitos, as regras de negócio RN01 a RN08 e os cenários de cada funcionalidade estão em [`openspec/specs/`](openspec/specs/). As mudanças já entregues estão arquivadas em [`openspec/changes/archive/`](openspec/changes/archive/): `add-mvp` (banco, CRUD, sorteio e histórico) e `add-estatisticas-e-visual` (estatísticas e atalhos). A mudança `refaz-identidade-visual` troca o nome para "Shuffle" e o visual para o design system "Lambe-lambe", com as regras anti-slop do seu `design.md`, e a `add-player-embutido` acrescenta o player do YouTube e do Spotify na tela de resultado.

```bash
openspec validate --specs --strict
```

## Limitações conhecidas

- Feito para uso local por uma pessoa: não há login nem proteção CSRF. Não publique o servidor na internet sem adicionar isso e definir a variável de ambiente `SECRET_KEY`.
- A anti-repetição vale para o histórico inteiro, independentemente dos filtros usados no sorteio.
- **Player embutido na apresentação:** com o seed, "Evidências", "Tempo Perdido", "Sonífera Ilha" e "Trem das Onze" mostram os dois players (YouTube e Spotify); as outras músicas têm só o Spotify. Para outros vídeos, edite a música e cole um link de vídeo (`youtube.com/watch?v=…`, `youtu.be/…`, `youtube.com/shorts/…`, `music.youtube.com/watch?v=…`) no campo YouTube ou de faixa (`open.spotify.com/track/…`, `open.spotify.com/intl-pt/track/…`) no campo Spotify.
- O player só carrega depois do clique e precisa de internet nesse momento; a tela de resultado em si abre sem internet. Vários vídeos oficiais de música bloqueiam a incorporação e o Spotify toca só uma prévia de 30 s para quem não está logado no navegador: nesses casos, use "Abrir no YouTube" ou "Abrir no Spotify". O status de incorporação muda com o tempo; confira com `python tools/verificar_links.py` antes de apresentar.
- Modo "Esquecidas", setlist, modo festa, CSV e desafio ficaram para trabalhos futuros (ver o `proposal.md` das mudanças em `openspec/changes/`).

## Créditos

- Fontes [Big Shoulders Display](https://github.com/xotypeco/big_shoulders), [Archivo](https://github.com/Omnibus-Type/Archivo) e [IBM Plex Mono](https://github.com/IBM/plex), sob a SIL Open Font License 1.1, distribuídas pelos pacotes do [Fontsource](https://fontsource.org) (licenças em `shuffle_meu/static/fonts/`).
- Ícones do [Lucide](https://lucide.dev), licença ISC.
