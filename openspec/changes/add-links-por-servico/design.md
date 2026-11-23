# Design: add-links-por-servico

## Context

Motivação em `proposal.md`; comportamento nas deltas de `musicas` e `sorteio`. Estado atual que molda a abordagem:

- `musica.link` (TEXT, `CHECK` de `http://`/`https://`) é o único link. `validar_musica()` em `musicas.py` só confere o esquema. O formulário (`musicas/form.html`) usa o macro `campo()`, que já põe o erro junto ao campo.
- `player(link)` vive em `sorteio.py` (mudança `add-player-embutido`, arquivada): host comparado por igualdade, `re.fullmatch` do ID, `src` montado só com o ID. `sorteio.py` importa de `musicas.py` (`generos`, `rotulo_genero`), então `musicas.py` não pode importar de `sorteio.py` sem ciclo.
- O schema roda a cada início (`init_db()` executa `schema.sql`, todo em `CREATE TABLE IF NOT EXISTS`). Não há migrações: uma coluna nova num `CREATE TABLE` não chega a bancos que já existem.
- `seed.py` grava em `link` uma busca do YouTube por música, com `INSERT OR IGNORE` pelas chaves naturais, e promete não sobrescrever o que o usuário editou (`test_nao_sobrescreve_edicao_do_usuario`).
- O resultado (`sorteio/resultado.html`) tem um botão "Ouvir aqui", um `<template data-player-modelo>` com o iframe e um bloco `[data-player]`; `app.js` (`iniciarPlayer`) clona o template no clique.
- Já existe um script de verificação via Chrome DevTools Protocol, da investigação do "This video is unavailable" (`add-player-embutido`, D3): ele abre o embed numa página em `127.0.0.1` e lê o texto dentro do iframe de outra origem.

## Goals / Non-Goals

**Goals:**
- Um campo por serviço, validado no servidor com as mesmas regras do player, sem perder dados de bancos existentes.
- Resultado com um botão por link e escolha de player quando houver os dois.
- Seed com links reais, oficiais e verificados, documentados com data.

**Non-Goals:**
- Outros serviços, álbuns e playlists, player para o "Outro link".
- Normalizar os links gravados (ficam como o usuário colou).
- Busca automática de links pelo app em tempo de execução.
- Ferramenta de migração genérica.

## Decisions

### D1. `links.py`: extração por serviço num módulo neutro

`player()` e suas constantes saem de `sorteio.py` para `shuffle_meu/links.py`, com duas funções públicas:

- `youtube_id(link) -> str | None`: esquema `http`/`https`, host em `youtube.com`, `www.youtube.com`, `m.youtube.com`, `music.youtube.com` (`/watch?v=`) ou `youtu.be` (`/<ID>`), e `/shorts/<ID>` nos três primeiros. O ID passa por `[A-Za-z0-9_-]{11}`.
- `spotify_id(link) -> str | None`: host `open.spotify.com`, caminho `/track/<ID>` ou `/intl-xx[-yy]/track/<ID>`, ID `[A-Za-z0-9]{22}`.
- `players(youtube, spotify) -> list[dict]`: na ordem YouTube, Spotify, só os válidos, cada um `{"chave": "youtube"|"spotify", "servico": "YouTube"|"Spotify", "src": ...}`, com `src` montado só com constantes e o ID, como hoje.

`musicas.py` (validação) e `sorteio.py` (resultado) importam de `links.py`; o teste `TestPlayer` passa a importar de lá, com os mesmos casos.

*Alternativa:* deixar em `sorteio.py` e importar dentro da função em `musicas.py` (rejeitada: import tardio para fugir de ciclo é frágil e esconde a dependência).

### D2. Banco: colunas novas e acréscimo idempotente

- `schema.sql`: `youtube TEXT CHECK (youtube LIKE 'http://%' OR youtube LIKE 'https://%')` e o mesmo para `spotify`, logo depois de `link`. Bancos novos já nascem com elas.
- `db.init_db()`, depois do `executescript`: lê `PRAGMA table_info(musica)` e, para cada coluna que faltar, roda `ALTER TABLE musica ADD COLUMN <coluna> TEXT CHECK (...)`, com a mesma definição do `schema.sql` (constante única em `db.py`, usada nos dois lugares por interpolação controlada, sem entrada do usuário). Idempotente: na segunda inicialização não há nada a acrescentar. As músicas existentes ficam com as colunas `NULL`.
- **Recriar o banco pelo seed é aceitável** (não há dados reais): apagar `instance/shuffle.db` e rodar `python seed.py` dá o banco com os links novos. O acréscimo idempotente existe para que um banco antigo, como o da máquina da apresentação, não quebre com `no such column: youtube` antes de ser recriado.
- O `CHECK` no banco é só a rede de segurança do esquema; a regra estrita (domínio, caminho, ID) fica em Python (D3), como já acontece com `link`.

*Alternativa:* exigir recriar o banco (rejeitada pelo usuário: quebraria quem já tem um banco).

### D3. Validação e formulário

- `validar_musica()` lê `youtube`, `spotify` e `link` (Outro link). Erros por campo:
  - `youtube` preenchido e `youtube_id()` `None`: "Cole o link de um vídeo do YouTube (youtube.com/watch?v=… ou youtu.be/…)."
  - `spotify` preenchido e `spotify_id()` `None`: "Cole o link de uma faixa do Spotify (open.spotify.com/track/…)."
  - `link`: a mensagem atual ("O link deve começar com http:// ou https://.").
- Grava o texto como veio (sem espaços nas pontas). `INSERT` e `UPDATE` de `musicas.py` passam a incluir as duas colunas.
- `musicas/form.html`: três campos com o macro `campo()`, nesta ordem, no lugar do campo único: "YouTube (opcional: link do vídeo)", "Spotify (opcional: link da faixa)" e "Outro link (opcional: cifra, letra…)". Os três são `type="url"`, com `autocomplete="off"` e placeholders `https://youtu.be/…`, `https://open.spotify.com/track/…` e `https://…`.

### D4. Resultado: botões por link e escolha de player

- A rota passa `players=players(s["youtube"], s["spotify"])` (D1) e os três links.
- Linha de botões, nesta ordem:
  1. Os botões de ouvir (`hidden`, revelados pelo JS): "Ouvir aqui" quando há um player; "Ouvir no YouTube" e "Ouvir no Spotify" quando há dois.
  2. "Abrir no YouTube", "Abrir no Spotify" e "Abrir link", cada um só se o campo estiver preenchido, todos com `target="_blank" rel="noopener noreferrer"` e o aviso oculto "(abre em nova aba)".
- Um `<template data-player-modelo="<chave>">` por player (inerte, como hoje), com o iframe e os mesmos atributos travados por `test_atributos_do_iframe`; a classe de tamanho (`player-youtube` 16:9, `player-spotify` 152 px) vai no próprio iframe.
- `app.js`, `iniciarPlayer()`: revela os botões de ouvir; no clique, `bloco.replaceChildren(clone do template da chave)`, esconde o botão clicado, volta a mostrar o outro (se houver) e foca o iframe. Trocar de player descarta o iframe anterior, então só um toca por vez.
- O "Outro link" nunca vira player, mesmo que seja um vídeo (cenário "Vídeo no outro link").

### D5. Seed: links verificados, sem sobrescrever edições

- `seed.py` ganha `LINKS = {título: (youtube | None, spotify | None)}`, separado de `MUSICAS` para manter a tabela de músicas legível. Cada valor vem de `docs/links-verificados.md` (D6).
- Música nova: o `INSERT` grava `youtube` e `spotify` de `LINKS`; o `link` recebe a busca do YouTube só quando `youtube` é `None`.
- Banco que já tem as músicas do seed (o `INSERT OR IGNORE` não altera linhas existentes):
  - `UPDATE … SET youtube = ? WHERE youtube IS NULL` e o mesmo para `spotify`, pelas chaves naturais (título + artista). Assim, um link que o usuário colou não é sobrescrito.
  - O `link` só é limpo quando o seed preencheu o `youtube` **e** o `link` ainda é exatamente a busca que o próprio seed gerou. Um link editado pelo usuário nunca é apagado.
- O seed continua idempotente e o teste de não sobrescrever ganha um caso para os links.

### D6. Como os links do seed são encontrados e verificados

Durante a implementação, nunca no app:

1. **Candidatos** por pesquisa na web, por música, nesta ordem para o YouTube, passando ao próximo só quando o anterior não incorporar ou não existir:
   1. o vídeo oficial (canal do artista, VEVO, gravadora ou "Artista - Topic" automático);
   2. outro vídeo do canal oficial do artista (ao vivo, acústico, lyric video);
   3. uma versão ao vivo ou acústica de canal confiável (emissora, festival, programa ou gravadora com canal verificado).

   No Spotify, a faixa do álbum original do artista; remasterização serve. Nenhum ID é escrito de memória ou "chutado": cada um vem de uma página encontrada na pesquisa.
2. **Verificação no Chrome** com `tools/verificar_links.py` (D8):
   - YouTube: carregar `https://www.youtube-nocookie.com/embed/<ID>` com os mesmos atributos do app, a partir de uma página em `127.0.0.1`. Passa só se o texto do iframe trouxer o título da música e o nome do canal oficial, sem "This video is unavailable", "Error" nem "Video unavailable".
   - Spotify: carregar `https://open.spotify.com/embed/track/<ID>`. Passa só se o texto trouxer o título e o artista.
3. Música sem vídeo oficial que incorpore: `youtube` vazio, e a busca fica no "Outro link". Sem faixa encontrada e confirmada: `spotify` vazio.
4. `docs/links-verificados.md` registra, por música: título, artista, link do YouTube, canal, tipo de vídeo (oficial, ao vivo, acústico, lyric, cover), "incorpora?" (sim; ou vazio com o motivo, como "todos os candidatos bloqueiam incorporação" ou "sem vídeo em canal oficial ou confiável"), link do Spotify e a data da verificação.

### D8. `tools/verificar_links.py`

- Só biblioteca padrão. Abre o Chrome headless com `--remote-debugging-pipe`: o protocolo DevTools passa por dois pipes (descritores 3 e 4, mensagens JSON terminadas em `\0`), sem WebSocket nem dependência nova.
- Recebe links pela linha de comando (ou um arquivo, um por linha) e, para cada um, usa `links.youtube_id`/`spotify_id` para montar o embed. Abre o embed dentro de uma página local mínima, servida pelo próprio script em `127.0.0.1` com os mesmos atributos do iframe do app, e lê o texto dentro do iframe (`Target.setAutoAttach` + `Runtime.evaluate` na sessão do iframe).
- Imprime uma linha por link: `OK` ou `FALHA`, o serviço, o ID e o texto lido (título e canal ou artista), para conferir com a música esperada. Código de saída diferente de zero se algum falhar.
- Não roda na suíte (`tests/` não o importa): depende de internet e do Chrome. O README, na seção "Comandos úteis", mostra o uso: `python tools/verificar_links.py https://youtu.be/<ID> https://open.spotify.com/track/<ID>`.

### D7. Testes

- `links.py`: os casos de `TestPlayer`, separados por `youtube_id` e `spotify_id`, mais `players()` com 0, 1 e 2 serviços e a ordem YouTube, Spotify.
- Banco: banco novo tem as colunas; um banco criado com o schema antigo (sem as colunas) recebe as duas na inicialização, sem perder linhas, e a segunda inicialização não falha.
- Formulário: os cenários da delta de `musicas` (os três links, busca no campo YouTube, álbum no Spotify, serviço trocado) com os dados preservados e o erro no campo certo.
- Resultado: os cenários da delta de `sorteio` com 0, 1 e 2 players (rótulos "Ouvir aqui" / "Ouvir no …", um `<template>` por player, nenhum iframe fora de `<template>`, botões de abrir por campo, outro link nunca vira player) e `test_atributos_do_iframe` para os dois.
- Seed: todo `youtube` do seed passa em `youtube_id`, todo `spotify` em `spotify_id`, música sem `youtube` tem a busca no `link`, e todo link do seed aparece no `docs/links-verificados.md` com "sim". É a trava contra ID inventado.

## Risks / Trade-offs

- [Muitos vídeos oficiais de música bloqueiam incorporação] → a música fica com `youtube` vazio e a busca no "Outro link"; a tabela registra o motivo. A demonstração usa as músicas que incorporam.
- [O status de incorporação muda com o tempo ou por país] → a data da verificação fica no `docs/links-verificados.md`; antes da apresentação, rodar o resultado de uma música do seed.
- [O "Artista - Topic" e a faixa do Spotify podem ser remasterização ou outra versão] → aceitável para ouvir antes de tocar; o critério é título e artista oficiais.
- [Vídeos ao vivo ou de canais confiáveis não são a gravação de estúdio] → o tipo fica registrado na tabela; servem para lembrar a música antes de tocar.
- [Encontrar e verificar 25 × 2 links custa tempo] → é um grupo de tarefas próprio, que pode ser feito por último sem bloquear o resto (o seed sem links continua funcionando).
- [`ALTER TABLE ADD COLUMN` com `CHECK` não revalida linhas antigas] → as colunas nascem vazias, então não há linha antiga a validar.
- [Rollback deixa as colunas no banco] → colunas vazias e ignoradas pelo código antigo; recriar o banco resolve.

## Migration Plan

Na primeira inicialização com o código novo, `init_db()` acrescenta `youtube` e `spotify` a bancos antigos (D2). Para ter os links verificados num banco existente, basta rodar `python seed.py` (D5); ou apagar `instance/shuffle.db` e rodar o seed. Rollback: reverter os commits; as colunas extras ficam vazias e não atrapalham.
