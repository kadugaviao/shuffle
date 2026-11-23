# Design: revisao-final

## Context

Motivação e itens em `proposal.md`; achados com IDs, reprodução e severidade em `docs/revisao-final.md`; comportamento nas deltas de `sorteio`, `musicas`, `playlists` e `interface`. Estado atual que molda a abordagem:

- `sorteio/resultado.html`:
  - A folha `.resultado` tem `max-width: 52rem` e uma coluna só, na ordem: capa + data, título + carimbo, artista, linha de 4 botões de ouvir e abrir, bloco `[data-player]`, Toquei/Pular, estrelas.
  - O player é clonado de um `<template data-player-modelo="youtube|spotify">` por `iniciarPlayer()` em `app.js`.
  - A roleta posiciona o `.rolo` com `padding-top: calc(24px + 96px + 16px)`, que supõe capa de 96 px acima do título.
- O degrau de título vem do template:
  - `titulo-longo` quando o título passa de 24 caracteres ou tem palavra de mais de 8 letras;
  - o CSS aplica 44/72 px em vez de 72/120 px.
- `templates/_macros.html`: `aria(nome, erros)` só põe `aria-invalid`/`aria-describedby` com erro; `campo()` renderiza rótulo, controle e erro.
- Os avisos são renderizados no HTML com `role="status"`/`role="alert"`, e `app.js` só cuida do fechar e do sumir em 5 s.
- `playlists.remover()` apaga e sempre avisa "Música removida da playlist.".
- As contagens usam "música(s)" em 4 templates. A mensagem "Este artista tem N música(s)…" é citada na spec de artistas e não muda.
- Testes que conferem HTML exato e serão ajustados:
  - "música(s)";
  - `<ul class="lista-cartoes">`;
  - "Ouvir aqui</button>", `data-ouvir="youtube" hidden`, "Ouvir no YouTube</button>";
  - "Abrir no YouTube".

## Goals / Non-Goals

**Goals:**
- Resultado sem vazio lateral, com hierarquia clara (Toquei/Pular primeiro) e player que não empurra as ações.
- Corrigir todos os itens Alta e Média e os Baixa de esforço P do relatório, cada bug com teste que falha antes.
- README e screenshots prontos para a entrega, conferidos numa cópia limpa.

**Non-Goals:**
- Mudar a direção visual, o schema, as rotas ou as regras de negócio.
- Os itens listados como trabalho futuro em `proposal.md`.

## Decisions

### D1. Resultado em duas colunas

- `.resultado` perde o `max-width`: ocupa o contêiner de 72rem, como o Início.
- O template divide a folha em duas partes:
  - `<div class="resultado-principal">`: topo (capa, data, carimbo), título, artista, ações (Toquei/Pular), avaliação;
  - `<section class="resultado-ouvir" aria-label="Ouvir e abrir">`: "Ouvir aqui", seletor, player e links "Abrir no…".
- A partir de 960 px, `display: grid; grid-template-columns: minmax(0, 1fr) 26rem; gap: var(--espaco-7)`. A coluna da direita tem `border-left: var(--regua)` e `padding-left: var(--espaco-6)`: régua, não cartão dentro da folha.
- Abaixo de 960 px, uma coluna, com o bloco de ouvir depois das ações e separado por régua no topo. A ordem do HTML é a mesma da leitura (ações antes de ouvir), então o teclado segue a ordem visual.
- Sem nenhum link, a seção de ouvir não é renderizada e a coluna principal ocupa a folha inteira.

*Alternativa:* manter uma coluna e só centralizar a folha. Rejeitada: o design pede composição alinhada à esquerda e sem lado sobrando.

### D2. "Ouvir aqui" com seletor e links "Abrir no…"

- **Com dois players:** rótulo "Ouvir aqui" (Archivo condensado 16, `id="rotulo-ouvir"`) e `<div class="segmentado segmentado-2" role="group" aria-labelledby="rotulo-ouvir">` com dois `<button type="button" data-ouvir="youtube" aria-pressed="false">YouTube</button>`.
  - O `.segmentado` atual é usado com chips de radio e fonte mono. A variação `.segmentado-2` usa 2 colunas, Archivo condensado e botões.
  - Nenhum vem pressionado: o player só carrega no clique.
- **Com um player:** um botão só, `<button type="button" data-ouvir="spotify">` com ícone de fone e texto "Ouvir aqui".
- **Com e sem JS:** o bloco de ouvir começa `hidden` e o `app.js` revela, como hoje. Sem JS ficam só os links.
- **Clique:**
  - o `app.js` clona o template do serviço para `[data-player]`, marca `aria-pressed="true"` no escolhido (amarelo e marca quadrada, como o chip) e `false` no outro;
  - mostra o botão **"Fechar player"** (secundário, ícone `fechar`) e escreve "Player do YouTube aberto." numa região `aria-live="polite"` do bloco;
  - o foco fica no botão escolhido, não vai para dentro do iframe (A4).
- **Fechar:** esvazia o bloco, volta todos para `aria-pressed="false"`, esconde o fechar, anuncia "Player fechado." e devolve o foco ao seletor.
- **Links "Abrir no…":** `<a class="link-abrir">` em Archivo 600 14 px, sublinhados, com o ícone `link` (sem o caractere ↗ e sem " · ", proibidos pelo Anti-slop), área de toque de 44 px e "(abre em nova aba)" oculto, todos numa linha `.links-abrir` com `flex-wrap`.
- **Spec:** os rótulos "Ouvir no YouTube" e "Ouvir no Spotify" saem (delta de `sorteio`).

### D3. Topo, carimbo, data e título

- **Carimbo:** sai de `.resultado-titulo` e vai para `.resultado-topo`, à direita da capa e da data. Fica sempre no mesmo lugar, independentemente do tamanho do título (D5 do relatório). Abaixo de 720 px o carimbo usa `--t-28` (900, ainda texto grande): a 44 px ele mede 216 px e não cabe ao lado da capa a 360 px.
- **Data:** uma linha só, em Plex Mono 14, abaixo da capa (`white-space: nowrap`).
- **Degraus de título:**
  - `titulo-longo` (mais de 24 caracteres) desce um degrau em qualquer largura;
  - `titulo-palavra-longa` (palavra de mais de 8 letras) desce só abaixo de 720 px, onde a palavra não cabe a 72 px. No desktop "Evidências" volta a 120 px (B2).
  - O teste do degrau ganha um caso por classe.
- **Roleta:** o `.rolo` fica dentro de `.resultado-principal`. O `app.js` posiciona a janela com `rolo.style.top = titulo.offsetTop + "px"` no início da animação, em vez do `96px` fixo (D10). A janela usa o mesmo degrau do título.

### D4. Ajustes em outras telas

- **Início no celular (D6):** `<p class="ultima-compacta meta">` logo abaixo do "Sortear", com o mesmo texto "Última sorteada: título — artista". Visível abaixo de 960 px; a folha da coluna direita aparece só a partir de 960 px. A spec de histórico continua atendida em qualquer largura.
- **Hover do "Sortear" (D7):** `text-decoration: underline 4px; text-underline-offset: 8px`, instantâneo, como os outros primários.
- **Dificuldade no repertório (D8):** sai de `.etiquetas` e vai para a linha do artista, em `.musica-info`. Na linha das ações não cabe: a 360 px ela já ocupa 303 de 312 px. Assim a dificuldade fica sempre no mesmo lugar, sem depender da largura das etiquetas.
- **Aba atual (D9):** além da régua vermelha, o rótulo fica em `--amarelo` (amarelo sobre tinta: 12,8:1).
- **Plural (D12):** filtro Jinja `n|plural("música", "músicas")` em `__init__.py`, que devolve a palavra certa para o número; o número continua em `<span class="numero">`. Usado nas 4 contagens; a mensagem de exclusão de artista não muda.
- **Histórico vazio (D13):** o CTA "Que tal sortear agora?" usa o ícone `dado`. O macro `vazio()` ganha o parâmetro `icone_cta` (padrão `mais`).
- **Repertório vazio (D15):** com zero músicas e sem busca ou filtro, o template renderiza só o cabeçalho e `vazio("Caderno em branco", "Anota a primeira que você sabe tocar.", …, "Nova música")`, sem o formulário de busca e filtros. O caso "busca sem resultado" continua "Nenhuma música encontrada.".
- **Base 4 (D10):** chip com `padding: 0 var(--espaco-3)`, etiqueta com `padding: 0 var(--espaco-2)`, marca do chip com 4 px de afastamento e `.linha-lado` com `padding-left` derivado de `calc(48px + var(--espaco-4))`. O teste anti-slop não muda.

### D5. Playlist: remover música que não está nela (B1)

`remover()` lê `cursor.rowcount` do `DELETE`. Se for 0, avisa `flash("Essa música não está na playlist.", "erro")`; senão, mantém a mensagem atual. Continua redirecionando para o detalhe. O teste chama o POST para uma música fora da playlist e espera o aviso de erro e a ausência da confirmação.

### D6. Limites de tamanho no servidor (SEG1)

- Cada validação ganha um dicionário com os limites e as mensagens, ao lado das regras atuais:
  - **`musicas.py`:** título 200, gênero 60, link/youtube/spotify 500;
  - **`artistas.py`:** nome 120, país 80;
  - **`playlists.py`:** nome 120, descrição 200.
- **Mensagem:** "O título pode ter no máximo 200 caracteres.", com o artigo certo para cada campo.
- Os mesmos números ficam nos `maxlength` dos templates (os campos de link ganham `maxlength="500"`).
- Sem helper compartilhado: são 3 dicionários de poucas linhas, no estilo de validação de cada módulo.

### D7. Acessibilidade dos formulários (A1–A3)

- **Interruptor (A1):** `aria-label="{{ rótulo visível }}: {{ título }}"` ("Ativa: Tempo Perdido" ou "Fora do sorteio: Tempo Perdido"). O `app.js` atualiza o `aria-label` junto com o rótulo. O teste atual de "Ativa: Tempo Perdido" continua valendo para música ativa, e ganha o caso inativo.
- **Obrigatórios e foco (A2):**
  - `aria(nome, erros, obrigatorio=false, dica=none)` acrescenta `aria-required="true"` e junta os ids de dica e erro em `aria-describedby`.
  - Título e Artista (música), Nome (artista e playlist) passam `obrigatorio=true`.
  - O `app.js` foca `document.querySelector('[aria-invalid="true"]')` ao carregar.
- **Dica dos links (A3):** `campo()` ganha o parâmetro `dica`, renderizado como `<p class="dica meta" id="dica-<campo>">` abaixo do controle. As dicas são:
  - YouTube: "Link de um vídeo: youtube.com/watch?v=… ou youtu.be/…";
  - Spotify: "Link de uma faixa: open.spotify.com/track/…";
  - Outro link: "Cifra, letra ou busca; começa com https://".

### D8. Avisos anunciados (A5) e listas (A6)

- **Avisos (A5):**
  - `base.html` ganha, fora da seção de avisos, uma região sempre presente `<p class="visualmente-oculto" aria-live="assertive" data-anunciar></p>`.
  - `iniciarToasts()` copia o texto de cada aviso para essa região 100 ms depois do carregamento. A região já existe vazia, então o leitor de tela anuncia a mudança.
  - Os avisos continuam no HTML com os mesmos `role`, para quem está sem JS e para os testes atuais.
- **Listas (A6):** `role="list"` em `.setlist`, `.lista-cartoes`, `.lista-simples` e `.barras`; os testes que procuram `<ul class="lista-cartoes">` passam a procurar o novo HTML.

### D9. README, screenshots e docs (DOC1–DOC4, SEG2)

- **README na estrutura pedida:**
  1. título e frase;
  2. equipe;
  3. requisitos: "testado com Python 3.12.3 e git 2.43.0"; Google Chrome só para a ferramenta de links; Node.js 20+ e a CLI do OpenSpec só para o `openspec validate`;
  4. como rodar, só blocos de comando: `git clone`, `cd`, `python3 -m venv .venv`, ativar, `pip install -r requirements.txt`, `python seed.py`, `flask --app shuffle_meu run` e o endereço;
  5. comandos úteis: testes, recriar o banco, `openspec validate --strict`, `python tools/verificar_links.py` com o que precisa;
  6. problemas comuns no formato "erro → comando" (venv não ativado, `--app`, porta ocupada com `--port 5001`, "This video is unavailable");
  7. OpenSpec: fluxo em 3 linhas, onde ficam specs e mudanças arquivadas, comandos do Claude Code;
  8. stack em tabela e árvore de pastas;
  9. screenshots e limitações, incluindo `SECRET_KEY` e CSRF.
- **Screenshots:**
  - Um script fora do repositório usa o Chrome headless pelo DevTools Protocol, como em `tools/verificar_links.py`. Ele mede o `scrollHeight` da página e captura a página inteira, então a barra fixa fica no fim e não cobre conteúdo.
  - **Celular:** 390 px a 2× (início, resultado, histórico). **Desktop:** 1440 px a 1× (início, resultado).
  - Mesma largura dentro de cada grupo, convertidos para WebP.
  - O resultado usa "Evidências" (dois players). A aba atual fica visível no início do celular pela barra inferior no fim da página.
  - O README mostra os 3 do celular numa tabela e os 2 do desktop em outra, com `width` igual por grupo. Os 10 arquivos atuais saem: ficam só os 5 usados.
- **Outros:** `requirements.txt` com `Flask==3.1.3`. `docs/plan.md` com os critérios de pronto marcados, exceto o ensaio. Cópia limpa: `git clone` do commit final num diretório temporário, seguindo o README comando a comando.

### D10. Testes

Cada correção ganha teste escrito antes e conferido falhando:

| Item | Teste |
|---|---|
| S1 | Sorteio filtrado por "ROCK" só traz a música de rock. |
| B1 | Remover música fora da playlist avisa erro. |
| B2 | Palavra longa usa a classe só de celular; mais de 24 caracteres usa `titulo-longo`. |
| SEG1 | Título de 201 caracteres e nome de 121 recusados, com erro no campo. |
| D15 | Repertório vazio mostra "Caderno em branco" e não mostra o formulário de busca. |
| D12 | "1 música" e "2 músicas". |
| A1 | `aria-label` do interruptor inativo começa com "Fora do sorteio". |
| A2 | `aria-required` nos obrigatórios. |
| A3 | `aria-describedby` junta dica e erro. |
| D2 / spec | Seletor com dois `aria-pressed="false"`, botão simples com um serviço, links "Abrir no…" fora de botões, "Fechar player" presente e escondido, nenhum iframe fora de `<template>`, `test_atributos_do_iframe` mantido. |

Os comportamentos de JS (seletor, fechar player, foco no erro, região live, roleta posicionada pelo título) são conferidos no Chrome pelo DevTools Protocol, como nas mudanças anteriores.

## Risks / Trade-offs

- [Mudanças na tela mais usada na véspera] → grupos pequenos com commit e suíte verde em cada um; o resultado é o primeiro grupo, e dá para parar depois dele com o essencial pronto.
- [Roleta posicionada por `offsetTop` pode errar se o layout mudar durante a animação] → a posição é lida no início da animação, com a folha já renderizada; conferir a 360 e 1440 px.
- [`aria-live="assertive"` duplicado com o `role="alert"` em leitores que já anunciavam] → aviso lido duas vezes no pior caso, menos ruim que nenhuma vez.
- [Foco automático no primeiro erro pode surpreender quem enxerga] → só acontece depois de um envio com erro, quando o campo errado é o próximo passo natural.
- [README e screenshots dependem do estado final] → são o último grupo, depois de todas as mudanças visuais.

## Migration Plan

Sem migração de dados (schema igual). Implantação: atualizar o código e reiniciar. Rollback: reverter os commits da mudança.
