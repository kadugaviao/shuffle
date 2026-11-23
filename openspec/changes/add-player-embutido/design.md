# Design: add-player-embutido

## Context

Motivação em `proposal.md`; comportamento na delta de `sorteio`. Estado atual que molda a abordagem:

- A rota `GET /sorteios/<id>` (`sorteio.py`, `resultado()`) já lê `m.link` e passa `s` ao template. Em `sorteio/resultado.html`, o link aparece como `<a class="botao" … target="_blank" rel="noopener noreferrer">Abrir link</a>` dentro do `.revelavel`, que fica escondido durante a roleta.
- O cadastro só garante que o link começa com `http://` ou `https://` (requisito "Link seguro" de `musicas`); qualquer texto depois disso é aceito. Por isso o link não pode ir cru para um `src` de iframe.
- Os links do seed são buscas (`youtube.com/results?search_query=…`), que não têm player: a demonstração com o seed continua só com "Abrir link".
- Não há Content-Security-Policy no projeto; o JS (`static/app.js`) é melhoria progressiva em funções independentes; botões que só funcionam com JS já usam o padrão `hidden` revelado pelo JS (botão de fechar aviso).
- Design system "Lambe-lambe" e seção Anti-slop (arquivados em `changes/archive/2026-11-22-refaz-identidade-visual/design.md`) valem para o bloco do player.

## Goals / Non-Goals

**Goals:**
- Tocar vídeo do YouTube ou faixa do Spotify na tela de resultado, sob demanda.
- Zero requisição a terceiros ao abrir a tela; segurança garantida no servidor, não no navegador.
- Mudança pequena: uma função pura, um bloco no template, uma função no JS, algumas regras de CSS.

**Non-Goals:**
- Player sem JavaScript (sem JS fica o "Abrir link", que já cumpre a função).
- Outros serviços, álbuns e playlists do Spotify.
- Content-Security-Policy para o site todo.
- Mudar o cadastro de músicas ou o seed.

## Decisions

### D1. Extração do ID: função pura em `sorteio.py`

`player(link) -> dict | None` devolve `{"servico": "YouTube" | "Spotify", "src": <url do embed>}` ou `None`. Só a biblioteca padrão (`urllib.parse.urlsplit`, `parse_qs`, `re`):

1. `urlsplit(link)`; o esquema precisa ser `http` ou `https`. O host vem de `.hostname` (minúsculo, sem porta e sem `usuario@`), então `https://youtube.com@exemplo.net/…` dá `exemplo.net` e é recusado.
2. Comparação do host por **igualdade** com uma lista fechada, nunca por "termina com" ou "contém":
   - YouTube: `youtube.com`, `www.youtube.com`, `m.youtube.com` com caminho `/watch` (ID no parâmetro `v`) ou `/shorts/<ID>`; `music.youtube.com` com `/watch` (mesmo ID e mesmo embed do YouTube); `youtu.be` com caminho `/<ID>`. Barra final opcional; parâmetros extras (`t=`, `si=`, `list=`) são ignorados.
   - Spotify: `open.spotify.com` com caminho `/track/<ID>` ou `/intl-<idioma>/track/<ID>`, em que `<idioma>` é um código de idioma ISO 639-1 (2 letras minúsculas) com região opcional (`-` + 2 letras), como `intl-pt`, `intl-es` ou `intl-pt-br`: `re.fullmatch(r"/(?:intl-[a-z]{2}(?:-[a-z]{2})?/)?track/([A-Za-z0-9]{22})/?", caminho)` (o caminho é comparado como veio: o Spotify só gera minúsculas nele). Parâmetros como `si=` são ignorados.
3. O ID passa por `re.fullmatch`: YouTube `[A-Za-z0-9_-]{11}`, Spotify `[A-Za-z0-9]{22}`. Qualquer outra coisa (aspas, `<`, espaço, tamanho diferente) dá `None`.
4. O `src` é montado só com constantes e o ID validado: `https://www.youtube-nocookie.com/embed/<ID>` e `https://open.spotify.com/embed/track/<ID>`. O link do usuário nunca é interpolado.

A rota passa `player=player(s["link"]) if s["link"] else None` ao template. O autoescape do Jinja continua ativo como segunda barreira.

*Alternativas:* filtro Jinja (rejeitada: a regra de segurança fica escondida no template e é pior de testar); validar no cadastro e guardar o ID (rejeitada: muda schema e o formulário, fora do escopo; o link pode ter sido gravado antes).

### D2. Carregar só no clique: player dentro de `<template>`

O iframe vai no HTML dentro de um `<template>`, que o navegador mantém inerte: nada é baixado nem executado até o conteúdo ser clonado para a página. O botão "Ouvir aqui" (`type="button"`, `hidden` no HTML) é revelado pelo `app.js`; ao clicar, o JS clona o template para dentro do bloco do player, esconde o botão e põe o foco no iframe.

- Sem JS: o botão continua `hidden` e a tela mostra só "Abrir link". Nenhum botão morto.
- *Alternativas:* `<iframe loading="lazy">` (rejeitada: carrega assim que entra na tela, sem clique); iframe dentro de `<details>` fechado (rejeitada: o carregamento não é garantido em todos os navegadores); recarregar a página com `?ouvir=1` (rejeitada: perde o estado da tela, complica os filtros na query string e refaz a revelação).

### D3. Atributos do iframe

- `title="Player do <serviço>: <título da música>"` (leitores de tela e WCAG 4.1.2).
- `allow="autoplay; encrypted-media; picture-in-picture; fullscreen"` e `allowfullscreen`. No YouTube o `src` leva `?autoplay=1`: o clique em "Ouvir aqui" já é o pedido para tocar, então não faz sentido pedir um segundo clique no play.
- `referrerpolicy="strict-origin-when-cross-origin"`: o YouTube recusa embed sem referrer; essa política manda só a origem, não o caminho com o id do sorteio.
- Sem `sandbox`: o player do YouTube exige `allow-scripts` + `allow-same-origin`, o que anularia o sandbox; o isolamento já vem de ser outra origem.
- Tamanho: YouTube `aspect-ratio: 16 / 9`, largura total do bloco; Spotify altura fixa de 152 px (o tamanho compacto oficial).

### D4. Visual no Lambe-lambe

- "Ouvir aqui" é um botão secundário com ícone de fone (Lucide `headphones`, traço 1,5, novo em `_icones.html`), ao lado do "Abrir link" numa mesma linha de botões.
- O player aparece logo abaixo dessa linha, num bloco `.player` com `border: var(--regua)` (2 px de tinta), raio 0, fundo papel, iframe sem borda própria e `display: block`. Sem sombra, sem animação de entrada (aparece por ação do usuário e não precisa de movimento para ser notado).
- Largura máxima igual à da folha do resultado; a 360 px ocupa a largura útil da folha.

### D5. Testes

- Unitários de `player()`: os formatos do YouTube (com `www.`, `m.`, `music.`, sem subdomínio, `youtu.be`, `/shorts/`, com `t=` e `si=`), faixa do Spotify com e sem `si=` e com `intl-pt` e `intl-pt-br`, e as recusas de `intl-` malformado (`intl-/`, `intl-portugues/`, `intl-p/`), e recusas: busca do YouTube, `/playlist`, álbum e playlist do Spotify, domínio parecido (`youtube.com.exemplo.net`), `usuario@host`, esquema `javascript:`, ID de 10 e de 12 caracteres, ID com aspas ou `<`, link vazio.
- Da tela de resultado: com link de vídeo, o HTML tem o botão "Ouvir aqui" `hidden`, o `src` montado (`youtube-nocookie.com/embed/<ID>`) **só dentro** do `<template>` e o "Abrir link"; com o link do seed, não tem `<template>` nem "Ouvir aqui"; com link malicioso, nenhum pedaço da URL aparece dentro de `src=`.
- `test_design.py` (anti-slop) continua valendo para o CSS e o template novos.

## Risks / Trade-offs

- [Muitos vídeos oficiais bloqueiam a incorporação e o player mostra erro] → "Abrir link" sempre ao lado (requisito da spec).
- [O Spotify toca só uma prévia de 30 s para quem não está logado no navegador] → limitação do serviço; "Abrir link" leva ao app do Spotify.
- [Clicar em "Ouvir aqui" sem internet mostra a página de erro do navegador dentro do bloco] → a tela em si continua funcionando, e o clique foi uma escolha do usuário; aceitável para a apresentação offline.
- [`youtube-nocookie` ainda grava dados depois que o vídeo toca] → é o modo de privacidade aprimorada oficial; o compromisso é não carregar nada antes do clique.
- [Formatos de link novos dos serviços (ex.: `youtube.com/live/`, `spotify.link`) não são reconhecidos] → caem no "Abrir link", sem quebrar nada; a lista de D1 é fácil de ampliar.
- [O seed só tem buscas, então a demonstração não mostra o player sozinha] → o README orienta a editar uma música e colar um link real de vídeo ou faixa antes de apresentar; o seed não ganha IDs inventados.

## Migration Plan

Sem migração (schema não muda). Implantação = atualizar o código e reiniciar o servidor. Rollback = reverter os commits da mudança.
