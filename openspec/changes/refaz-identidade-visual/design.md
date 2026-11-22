# Design: refaz-identidade-visual

## Context

O motivo está em `proposal.md`; o comportamento esperado, nas specs desta mudança (`interface` e `sorteio`). Estado atual que molda a abordagem:

- `static/style.css` (~730 linhas) implementa o "Midnight Stage": tema escuro, `backdrop-filter`, `radial-gradient` animado no `body::before`, ruído SVG no `body::after`, `--mola` com overshoot, `--glow`, raios 12/20/999 px.
- `base.html` tem um `<linearGradient id="gradiente-svg">` usado pelas estrelas e `theme-color #0A0A0F`. `app.js` tem o "pop" com mola (`data-pop`) e a roleta por troca de texto com intervalos crescentes.
- Fontes em `static/fonts/`: Geist, Geist Mono e Instrument Serif (woff2 do Fontsource, sem `package.json`).
- 23 arquivos de teste. Os funcionais conferem banco e mensagens; alguns conferem trechos de HTML (`"Toquei ✅"`, `style="--h: 312"`, `class="musica-cartao inativa"`, `<h1 class="titulo-sorteado">`, `class="estrelas entrando"`). `test_contraste.py` lê os tokens hexadecimais do `:root` e mede o contraste.
- O nome "Shuffle Meu" aparece em `base.html` (marca e `<title>`), README, `docs/plan.md`, `openspec/config.yaml`, e em comentários de `seed.py`, `schema.sql`, `app.js` e `style.css`. Nenhuma spec principal cita o nome e nenhum teste o confere hoje.
- Contrastes medidos com a fórmula de `test_contraste.py` para os tokens pedidos: tinta/papel 16,15; tinta/papel-2 14,75; tinta-2/papel 6,18; tinta-2/papel-2 5,64; tinta/amarelo 12,82; papel/vermelho **3,85**; vermelho/papel **3,85**; sucesso/papel **4,46**; vermelho/tinta 4,19; amarelo/tinta 12,82.
- Restrições: apresentação em 24/11, Flask + Jinja + CSS/JS puros, nada de dependência nova, funcionamento offline.

## Goals / Non-Goals

**Goals:**
- Trocar a identidade inteira sem mudar rota, campo de formulário, consulta ou regra de negócio.
- Um design system escrito ("Lambe-lambe") que valha para mudanças futuras, com uma lista anti-slop conferida por teste, para a regressão não voltar sem ninguém perceber.
- Suíte verde ao fim de cada grupo de tarefas, com commit por grupo.

**Non-Goals:**
- Modo escuro ou alternância de tema (o app passa de só-escuro para só-claro).
- Renomear o pacote, o banco ou pastas (D1).
- Reescrever mensagens citadas nas specs (D12).
- Build de CSS, framework ou biblioteca JS.

## Decisions

### D1. Nome "Shuffle" só onde é visível ou documental

Muda: marca da navegação, `<title>` (`{% block titulo %} | Shuffle`), README, `docs/plan.md`, `openspec/config.yaml`, comentários e docstrings que citam o nome (`seed.py`, `schema.sql`, `app.js`, `style.css`) e um teste novo que confere título e marca. O emoji 🎵 sai dos títulos do README e do plano, junto com o nome.

**Não muda** o pacote `shuffle_meu`, o comando `flask --app shuffle_meu run`, `instance/shuffle.db` e nomes de pastas. Renomear o pacote mexe em imports de todos os módulos e testes, no comando que o trio já ensaiou e no README a dois dias da apresentação, sem nenhum ganho visível. As mudanças arquivadas ficam como estão, porque são o registro do que foi feito com o nome da época.

*Alternativa:* renomear tudo para `shuffle`. Rejeitada pelo risco e porque o usuário final nunca vê o nome do pacote.

### D2. CSS reescrito do zero, marcação preservada

`style.css` é reescrito em vez de editado: quase toda regra atual depende de token que deixa de existir (`--superficie`, `--gradiente`, `--glow`, `--mola`). A marcação dos templates muda só onde a estrutura da tela muda (repertório vira lista numerada, carimbo novo, capa por classe). **Nomes de classe e ganchos existentes ficam** (`musica-cartao`, `lista-cartoes`, `aba`, `toast-*`, `data-roleta`, `numero`, `metrica-valor`), mesmo que "cartão" não descreva mais o visual: são ganchos de teste e de JS, e renomear agora só gera diff.

Organização do novo arquivo: tokens (`:root`) → `@font-face` → base → layout → componentes (na ordem da tabela de componentes) → telas → `@media (prefers-reduced-motion)`. Seletores de classe simples, sem aninhar seletores de tipo com classe, para não haver regras de espaçamento que se anulam.

### D3. Fontes locais do Fontsource

Baixadas com `npm pack` numa pasta temporária (nada de `package.json`), só subconjuntos `latin` e `latin-ext`, versionadas em `static/fonts/` com a licença de cada família:

| Família | Pacote (5.3.0) | Arquivos | Eixos |
|---|---|---|---|
| Big Shoulders Display | `@fontsource-variable/big-shoulders-display` | `big-shoulders-display-latin[-ext]-wght-normal.woff2` | peso 100–900 |
| Archivo | `@fontsource-variable/archivo` | `archivo-latin[-ext]-standard-normal.woff2` (~90 KB) | peso 100–900, largura 62–125 % |
| IBM Plex Mono | `@fontsource/ibm-plex-mono` | `ibm-plex-mono-latin[-ext]-{400,500}-normal.woff2` | estático 400 e 500 |

- O arquivo "standard" do Archivo traz o eixo de largura (`font-stretch: 62% 125%` no `@font-face`); a largura condensada é `font-stretch: 75%`, sem um segundo arquivo.
- `font-display: swap`; `<link rel="preload">` para Big Shoulders e Archivo (latin).
- Fallbacks: Big Shoulders → `"Arial Narrow", "Roboto Condensed", Impact, sans-serif`; Archivo → `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`; Plex Mono → `ui-monospace, Menlo, Consolas, monospace`.
- Saem os arquivos de Geist, Geist Mono e Instrument Serif e as licenças deles. O README troca os créditos.

### D4. Regras de contraste para as cores de impressão

O vermelho `#E4371E` dá 3,85:1 com papel nos dois sentidos, e o sucesso `#1E7F4F` dá 4,46:1 com papel. Os dois passam só em texto grande. Em vez de trocar os valores escolhidos pelo trio, o design fixa **onde** cada um pode ser texto:

- **Fundo vermelho com texto papel** só em texto grande: o "Sortear" (Big Shoulders 900, 44/72 px) e os botões primários, que sempre usam Archivo 700 a 20 px (negrito acima de 18,66 px conta como grande).
- **Vermelho como cor de texto pequeno** (erro de campo, link de excluir) usa o token derivado `--vermelho-texto: #B82E17`* (5,45:1 no papel, 4,97:1 no papel-2). Carimbo e números grandes usam o vermelho original.
- **Sucesso** só aparece como texto grande (carimbo "TOCADA", 44 px) ou ícone. Não há texto verde pequeno.
- **Amarelo** só como fundo (chip selecionado, estrela acesa, capa) ou como texto sobre tinta (marca "SHUFFLE" na faixa).
- `test_contraste.py` passa a conferir esses pares, separando o limite de 4,5:1 (texto normal) do de 3:1 (pares que o design só permite em texto grande).

*Alternativa:* escurecer o vermelho de impressão para `#C4301A` (4,95:1) em tudo. Rejeitada porque apaga o vermelho de cartaz que é a identidade; fica registrada como plano B (ver dúvidas).

### D5. Caixa alta só por CSS

Títulos de tela, o hero, a música sorteada, a marca e o carimbo ficam em caixa normal no HTML ("Bora tocar o quê?", "Tempo Perdido", "Shuffle") e viram caixa alta com `text-transform: uppercase`. Leitores de tela leem a palavra normalmente, e os testes que conferem textos (`<h1 class="titulo-sorteado">Tempo Perdido</h1>`) continuam válidos.

### D6. Escala tipográfica em degraus, sem `clamp()`

Os tamanhos são só os da escala (14, 16, 20, 28, 44, 72, 120 px), trocados por degrau no ponto de quebra de 720 px. `clamp()` com `vw` gera tamanhos intermediários arbitrários, que é o que a escala quer evitar. Títulos de música longos descem um degrau com uma classe dada pelo template (`titulo-longo` quando o título passa de 24 caracteres), mais `overflow-wrap: anywhere` e `text-wrap: balance` para palavras longas a 360 px.

### D7. Revelação: roleta vertical e carimbo

Mantém o mecanismo atual (`session["revelar"]`, `data-roleta` com até 12 títulos + o sorteado, classe `js` no `<head>`, rede de segurança CSS de 2 s, `aria-live` só com o título final). Muda só o visual:

- O `.rolo` vira uma janela da altura de uma linha do título, com `overflow: hidden`, contendo a lista de títulos empilhados na mesma fonte e tamanho do título final (`white-space: nowrap`, reticências se não couber).
- Um único `transform: translateY()` leva a lista até o último item em **1.200 ms** com `cubic-bezier(0.5, 1, 0.89, 1)` (ease-out quadrático: a velocidade cai em ritmo constante até zero, sem passar do ponto). Uma transição em vez de `setTimeout` encadeados: o navegador anima na GPU e o fim é um `transitionend` só.
- No fim, o rolo some, o resultado aparece e o carimbo entra: escala 1,2 → 1 e opacidade 0 → 1 em **160 ms** ease-out. Total ≈ 1,36 s, dentro do teto de 1,5 s da spec.
- O carimbo é um `<p class="carimbo" aria-hidden="true">` sempre presente no HTML (sem JS e com movimento reduzido ele já aparece parado): "Toca essa!" quando `tocada = 0`, "Tocada" quando `tocada = 1`. O texto acessível do estado continua no `<p class="status-tocada">`, que passa a ser visualmente oculto.
- Sai o `data-pop` e a função de pop com mola.

### D8. Capa chapada em 3 cores

O filtro `matiz` continua igual (`crc32 % 360`, coberto por teste). A capa usa `matiz % 3` no template: classe `capa-0` amarelo com iniciais em tinta, `capa-1` vermelho com iniciais em papel (iniciais em Big Shoulders 900 a 28 px ou mais, texto grande: 3,85:1 passa), `capa-2` tinta com iniciais em amarelo. Sem mudança em Python; o `style="--h: ..."` sai.

### D9. Atalhos de favorita e ativa

Mesmas rotas, mesmos formulários e o mesmo JS de atalho. Favorita: `<button aria-pressed>` com coração em traço; ligado = coração preenchido em vermelho (muda forma e cor). Ativa: continua `<button role="switch" aria-checked>` com `aria-label="Ativa: <título>"`, desenhado como **interruptor retangular chapado**: trilho 40×24 com borda 2 px de tinta e raio 0, quadrado interno de tinta à esquerda (fora do sorteio, trilho papel) ou à direita (ativa, trilho amarelo); o quadrado desliza em 120 ms. Ao lado, rótulo visível em Archivo condensado 14 px: "Ativa" ou "Fora do sorteio", trocado pelo mesmo JS que já troca o `aria-checked`. Ícones de play/pausa foram descartados porque confundem com tocar a música.

### D10. Movimento

- Durações 120 a 180 ms, `ease-out` (palavra-chave do CSS), só onde mostra mudança de estado: pressionar o "Sortear" (desloca 2 px e perde a sombra, 120 ms), alternar favorita e ativa (120 ms), entrada de aviso (160 ms, saída 120 ms), estrelas aparecendo depois de "Toquei" (160 ms, todas juntas, sem cascata) e o carimbo (160 ms).
- Hover não anima: troca de cor ou sublinhado instantâneo.
- A roleta (D7) é a única animação longa.
- `prefers-reduced-motion: reduce` zera transições e animações, não roda a roleta e mostra o carimbo parado.

### D11. Testes que seguram a identidade

- `test_contraste.py`: lê os novos tokens do `:root` e confere os pares de D4 (4,5:1 para os de texto normal, 3:1 para os só-grandes).
- Teste anti-slop novo (em `test_design.py`): no `style.css`, nenhum `gradient(`, `backdrop-filter`, `blur(`, `#000` como cor, `cubic-bezier` com y fora de [0, 1], `border-radius` acima de 4 px, `font-family` fora das três famílias + fallbacks, e uma `box-shadow` só (a do "Sortear"). Nos templates, nenhum caractere de emoji. Em `static/fonts/`, só as três famílias.
- Teste de nome (em `test_interface.py`): `<title>` termina com "| Shuffle", a marca existe e "Shuffle Meu" não aparece em nenhuma tela.
- Testes acoplados ao HTML antigo são atualizados no grupo da tela correspondente (emoji dos botões, capa, cartão de música).

### D12. Microtexto

Os textos citados nas specs ficam **iguais** (são o contrato que os testes conferem): "Sortear", "Toquei", "Pular", "Cadastre sua primeira música", "Nenhuma música encontrada.", "Nenhum sorteio ainda. Que tal sortear agora?", "Última sorteada: …", as de validação e as confirmações. A exceção é a mensagem da RN05, que muda junto com a spec de `sorteio` (delta desta mudança) e com um teste que confere o texto literal. O tom informal entra nos textos livres:

| Onde | Hoje | Passa a ser |
|---|---|---|
| Mensagem da RN05 (spec) | Nenhuma música encontrada com esses filtros. Tente afrouxar os filtros. | Nada com esse filtro. Tira algum? |
| Atalho de ativa (rótulo) | Ativa | Ativa / Fora do sorteio |
| Título da tela inicial | O que tocar agora? | Bora tocar o quê? |
| Início sem músicas (frase) | O sorteio começa quando o repertório tem pelo menos uma música. | Sem música no caderno, não tem sorteio. |
| Bloco de espera (frase) | Depois do primeiro sorteio, ela fica guardada neste cartão. | Sorteia a primeira e ela fica anotada aqui. |
| Rótulo das estrelas | Que nota você dá? / Sua nota | Quanto valeu? / Sua nota: N |
| Link abaixo do resultado | Voltar aos filtros | Mudar os filtros |
| Repertório sem resultado (frase) | Tente outra busca ou limpe os filtros. | Tira um filtro ou busca outro nome. |
| Carimbo do resultado | (não existe) | Toca essa! / Tocada |

### D13. Screenshots em WebP

Capturas com o Chrome headless já instalado (`google-chrome --headless --screenshot --window-size=...`, `--virtual-time-budget` para a roleta terminar) e conversão com o Pillow da máquina (`Image.save(..., "WEBP", quality=85)`), fora do `requirements.txt`. Os mesmos 10 enquadramentos de antes (início, resultado, repertório, formulário, histórico; celular 360 px e desktop 1440 px), com o seed carregado. Os PNG saem do repositório e o README passa a apontar para os `.webp`.

## Design system "Lambe-lambe"

Fonte da verdade visual desta e das próximas mudanças. Substitui o "Midnight Stage" por inteiro. Valores com * foram derivados aqui para cumprir o contraste AA; os demais foram definidos pelo trio.

### Conceito e princípios

Cartaz lambe-lambe de show colado no muro e a folha de setlist presa com fita no chão do palco. O app é o caderno de repertório de quem toca em roda de violão.

- **A tipografia é a imagem.** Não há ilustração nem foto: o peso visual vem das letras condensadas gigantes em Big Shoulders. Cada tela tem um título grande e o resto em Archivo, quieto.
- **Duas cores de impressão, usadas como tinta, não como enfeite.** Vermelho = ação primária, carimbo e perigo. Amarelo = seleção e destaque de fundo. O resto é papel e tinta.
- **Réguas no lugar de cartões.** Seções separadas por régua de 2 px, linhas de lista por régua de 1 px. Blocos com borda só onde o conteúdo é de fato uma folha (o resultado e o bloco "última sorteada").
- **A ousadia fica num lugar só:** o resultado do sorteio (roleta + carimbo). Nenhuma outra tela anima sem ação do usuário.
- **Composição de cartaz, alinhada à esquerda.** Nada centralizado por padrão; o vazio é usado como respiro, nunca deixando um lado da tela sobrando.

### Tokens (`:root` em `style.css`)

| Token | Valor | Uso |
|---|---|---|
| `--papel` | `#F3F2EE` | fundo da página, texto sobre vermelho e tinta |
| `--papel-2` | `#E9E8E3` | linhas alternadas de listas, fita adesiva |
| `--tinta` | `#161616` | texto, réguas, bordas, faixa de navegação, toasts |
| `--tinta-2` | `#5A5A57` | texto secundário (6,18:1 no papel, 5,64:1 no papel-2, 4,90:1 no amarelo) |
| `--amarelo` | `#FFD60A` | fundo de destaque (chip selecionado, estrela acesa, capa); texto só sobre tinta |
| `--vermelho` | `#E4371E` | ação primária, carimbo, perigo; texto sobre ele só grande (3,85:1) |
| `--vermelho-texto`* | `#B82E17` | texto vermelho pequeno: erro de campo, link de excluir (5,45:1) |
| `--sucesso` | `#1E7F4F` | carimbo "Tocada" e ícone de sucesso (só grande ou ícone, 4,46:1) |
| `--foco` | `3px solid var(--tinta)`, `outline-offset: 2px` | foco de teclado; sobre tinta (faixa, toasts), `--amarelo` |
| `--raio-controle` | `4px` | inputs, selects e botões |
| — | `0` | blocos, réguas, chips, capas, barras, toasts |
| `--regua` / `--regua-fina` | `2px solid var(--tinta)` / `1px solid var(--tinta)` | seções / linhas de lista |
| `--impressao` | `2px 2px 0 var(--tinta)` | única sombra: botão "Sortear" |
| `--rapido` / `--medio` | `120ms` / `160ms` | durações (sempre com `ease-out`) |
| `--rolar` | `1200ms cubic-bezier(0.5, 1, 0.89, 1)` | só a roleta |
| `--espaco-1..8` | `4, 8, 12, 16, 24, 32, 48, 64px` | espaçamento (base 4) |

`color-scheme: light`; `<meta name="theme-color" content="#161616">` (cor da faixa).

### Tipografia

Escala única: **14 / 16 / 20 / 28 / 44 / 72 / 120 px**. Quando há dois valores, o primeiro vale abaixo de 720 px e o segundo a partir dele.

| Papel | Fonte | Tamanho | Detalhes |
|---|---|---|---|
| Hero da tela inicial | Big Shoulders Display 900 | 72 / 120 | caixa alta, altura de linha 0,9, tracking −0,01em, quebra em 2–3 linhas |
| Música sorteada | Big Shoulders Display 900 | 72 / 120 (longa: 44 / 72) | caixa alta, altura de linha 0,9, tracking −0,01em |
| Título de tela (h1) | Big Shoulders Display 900 | 44 / 72 | caixa alta, altura de linha 0,95 |
| Título de seção (h2) | Big Shoulders Display 800 | 28 | caixa alta |
| Marca "SHUFFLE" | Big Shoulders Display 900 | 28 | amarelo sobre a faixa de tinta |
| Botão "Sortear" | Big Shoulders Display 900 | 44 / 72 | caixa alta, papel sobre vermelho |
| Carimbo | Big Shoulders Display 900 | 44 | caixa alta, borda 4 px na mesma cor, girado −6° |
| Botão primário | Archivo 700, condensado | 20 | papel sobre vermelho (texto grande) |
| Botão secundário, links | Archivo 600 | 16 | |
| Texto | Archivo 400 | 16 | altura de linha 1,5; linhas de até ~70 caracteres |
| Título na lista | Archivo 700 | 20 | |
| Rótulos de campo, chips, navegação | Archivo 600, condensado (`font-stretch: 75%`) | 16 | caixa normal |
| Etiquetas (gênero, humor, inativa, tocada) | Archivo 700, condensado | 14 | caixa alta, tracking +0,04em, sem fundo, borda 1 px |
| Secundário / meta | Archivo 400 | 14 | `--tinta-2` |
| Rótulo da barra inferior | Archivo 600, condensado | 14 | sempre com ícone |
| Métricas | IBM Plex Mono 500, `tabular-nums` | 44 / 72 | |
| Números em listas, dificuldade, contadores, datas | IBM Plex Mono 400, `tabular-nums` | 14–16 | |

Caixa alta só por `text-transform` (D5). Caixa alta só no display (≥ 28 px) e nas etiquetas de 14 px; rótulos, botões comuns e navegação ficam em caixa normal.

### Layout

- Contêiner com largura máxima de 72rem, alinhado à esquerda, margem lateral de 16 px no celular e 32 px a partir de 720 px.
- Pontos de quebra: **720 px** (navegação de baixo para cima, degrau da escala) e **960 px** (duas colunas no início).
- Camadas (`z-index`): conteúdo 0, navegação 10, toasts 20. Não há mais camada de fundo.
- `main` com `padding-bottom: calc(72px + env(safe-area-inset-bottom))` abaixo de 720 px para a barra inferior não cobrir o fim.

```
Início, a partir de 960 px
┌──────────────────────────────────────────────────────────────────────┐
│ SHUFFLE   Início   Repertório   Artistas   Playlists   Histórico     │ faixa de tinta
│           ▀▀▀▀▀▀ régua vermelha na aba atual                         │
└──────────────────────────────────────────────────────────────────────┘
  BORA                                         ▱┌────────────────────┐▱  fita
  TOCAR O                                       │ Última sorteada:   │
  QUÊ?                    (120 px, à esquerda)  │ [TP] Tempo Perdido │
  ┌───────────────────────────────┐             │ — Legião Urbana    │
  │  SORTEAR                      │▌ impressão  │ 22/11 21:04        │
  └───────────────────────────────┘             └────────────────────┘
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  (coluna de 20rem, topo
  Humor     [Todos][Animada][Calma][Triste]...   alinhado com o hero)
  Dificuldade máxima  [Qualquer][1][2][3][4][5]
  Gênero    [Todos][Rock][MPB]...
  Artista [▾]   Playlist [▾]   Não repetir as últimas [ 5 ] rodadas

Início, 360 px                      Resultado, 360 px
┌──────────────────────┐            ┌──────────────────────┐
│ SHUFFLE              │ faixa      │ SHUFFLE              │
├──────────────────────┤            ├──────────────────────┤
│ BORA                 │ 72 px      │▱┌──────────────────┐▱│
│ TOCAR O              │            │ │[TP] 22/11 21:04  │ │
│ QUÊ?                 │            │ │ TEMPO   ╱TOCA   ╱│ │
│ ┌──────────────────┐ │            │ │ PERDIDO╱ ESSA! ╱ │ │
│ │ SORTEAR          │▌│ largura    │ │ Legião Urbana    │ │
│ └──────────────────┘ │ total      │ │ [Abrir link]     │ │
│ ━━━━━━━━━━━━━━━━━━━━ │            │ │ [✓ Toquei][Pular]│ │
│ Humor                │            │ └──────────────────┘ │
│ [Todos][Animada]...  │            │ Mudar os filtros     │
├──────────────────────┤            ├──────────────────────┤
│ ⌂    ♫    ◉    ≡   ⟲ │ barra      │ ⌂    ♫    ◉    ≡   ⟲ │
│ Início Rep. ...      │ inferior   │ ...                  │
└──────────────────────┘            └──────────────────────┘

Repertório, desktop
  REPERTÓRIO                                              [+ Nova música]
  Buscar [________________]  Humor [..]  Gênero [..]  [Só favoritas] [Filtrar]
  25 músicas
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  01 [TP] Tempo Perdido           ROCK  ANIMADA  ■■□□□   [♡] [▮□ Ativa] [✎] [lixo]
          Legião Urbana
  ────────────────────────────────────────────────────────────────────────  papel-2
  02 [DJ] Oceano                  MPB   CALMA    ■■■■□   [♥] [▮□ Ativa] [✎] [lixo]
          Djavan
  ────────────────────────────────────────────────────────────────────────
```

Abaixo de 960 px o bloco "última sorteada" não aparece (como hoje). No celular, cada linha do repertório quebra em três: número + capa + título/artista; etiquetas + dificuldade; atalhos alinhados à direita.

### Componentes

| Componente | Descrição |
|---|---|
| Navegação (≥ 720 px) | faixa de tinta chapada no topo; "SHUFFLE" em Big Shoulders 900 amarelo à esquerda; links em Archivo condensado 600 papel; aba atual com régua vermelha de 4 px embaixo e `aria-current="page"`; foco em amarelo |
| Navegação (< 720 px) | faixa no topo só com a marca; barra inferior fixa de tinta com 5 itens (ícone 24 px + rótulo 14 px); atual com régua vermelha de 4 px em cima |
| Botão "Sortear" | vermelho, texto papel em Big Shoulders 900 caixa alta, raio 4 px, sombra `--impressao`; pressionado desloca 2 px e perde a sombra (120 ms); largura total no celular |
| Botão primário | vermelho, texto papel Archivo 700 condensado 20 px, raio 4 px, sem sombra |
| Botão secundário | papel, borda 2 px tinta, texto tinta Archivo 600 16 px; hover = fundo papel-2 |
| Botão de perigo | ícone ou texto em `--vermelho-texto`, borda 2 px na mesma cor; confirmação nativa como hoje |
| Botão de ícone | quadrado de 44 px, ícone de traço tinta; pressionado/ligado conforme D9 |
| Interruptor (ativa) | trilho retangular 40×24, borda 2 px tinta, raio 0; ligado = trilho amarelo e quadrado de tinta à direita; rótulo "Ativa" / "Fora do sorteio" ao lado (D9); área de toque de 44 px |
| Chip | retângulo (raio 0), borda 2 px tinta, Archivo 600 condensado 16 px, altura mínima 44 px; selecionado = fundo amarelo e texto 700; radio/checkbox nativo escondido com foco no rótulo |
| Seletor de dificuldade (formulário) | 5 quadrados colados com borda 2 px, números em Plex Mono; selecionado = amarelo |
| Input / select | fundo papel, borda 2 px tinta, raio 4 px, altura 48 px, rótulo acima em Archivo 600 condensado |
| Erro de campo | borda do campo em `--vermelho`, mensagem em `--vermelho-texto` 14 px 700 com ícone de alerta logo abaixo |
| Toast | faixa retangular de tinta, texto papel 16 px, ícone à esquerda na cor do estado (sucesso, vermelho ou amarelo, todos ≥ 3:1 sobre tinta), botão fechar papel; entra com opacidade + 8 px em 160 ms |
| Capa | quadrado chapado (D8) com iniciais em Big Shoulders 900; 48 px na lista, 96 px no resultado |
| Lista setlist | `<ol>` com régua de 2 px no topo, linhas com régua de 1 px e fundo alternando papel/papel-2; número em Plex Mono `--tinta-2`; título Archivo 700 20 px; artista `--tinta-2`; etiquetas de texto; dificuldade; atalhos |
| Dificuldade (lista) | 5 quadradinhos de 10 px com borda 1,5 px tinta; preenchidos em tinta até o nível; `aria-label="Dificuldade N de 5"` |
| Etiqueta | texto 14 px caixa alta, borda 1 px tinta, sem fundo; "Inativa" e linha inativa com título em `--tinta-2` |
| Folha (resultado e "última sorteada") | bloco papel com borda 2 px tinta, raio 0, dois pedaços de fita (retângulos papel-2 com borda 1 px `--tinta-2`, girados ±4°) nos cantos de cima |
| Resultado | folha alinhada à esquerda: capa, data em Plex Mono, título gigante, carimbo sobreposto à direita do título, artista, link, "Toquei" (fundo tinta, texto papel, ícone de check) e "Pular" (secundário, ícone de avanço), estrelas depois de tocar |
| Carimbo | D7; vermelho ("Toca essa!") ou sucesso ("Tocada"), borda 4 px, girado −6°, sem fundo |
| Estrelas | 5 botões de 44 px com estrela em traço 2 px tinta; acesas = preenchimento amarelo com o mesmo contorno; hover/foco acende em sequência como hoje; o número da nota aparece no rótulo ("Sua nota: 4") |
| Métricas | 4 números grandes em Plex Mono sobre régua de 2 px, rótulo 14 px `--tinta-2` abaixo; 2×2 no celular, 4 colunas a partir de 720 px separadas por régua de 1 px (não são cartões) |
| Ranking top 5 | linha de texto (título, artista, número em Plex Mono à direita) + barra chapada de 12 px em tinta com largura `--p`; a primeira em vermelho; sem trilho de fundo |
| Por gênero | barra horizontal de 8 px em tinta, rótulo e contagem na mesma linha |
| Estado vazio | título em Big Shoulders 800 28 px, uma frase, botão primário; sem ícone ilustrativo |
| Ícones | Lucide em SVG inline (como hoje), traço 1,5, `currentColor`; nunca emoji |

### Movimento

Ver D10. Resumo: 120–180 ms, `ease-out`, só quando informa estado; a roleta (1,2 s) e o carimbo (160 ms) são o único momento forte; hover sem animação; nada anima no carregamento da página; `prefers-reduced-motion` desliga tudo.

### Foco e teclado

`:focus-visible` com contorno 3 px tinta e afastamento 2 px em tudo; dentro da faixa de navegação e dos toasts o contorno é amarelo. Chips e estrelas mostram o foco no rótulo visível. A ordem de tabulação segue a ordem visual (o bloco "última sorteada" vem depois dos filtros no HTML).

### Texto da interface

Português do Brasil informal e específico, verbos diretos ("Toquei", "Pular", "Mudar os filtros"). Uma ação mantém o mesmo verbo do botão à confirmação ("Excluir" → "Música excluída."). Estados vazios dizem o que fazer. Erros dizem o que corrigir, sem pedir desculpa. Textos citados nas specs não mudam sem uma mudança de spec (D12).

### Anti-slop

Proibido nesta e nas próximas mudanças. Os itens marcados com ✔ são conferidos por teste automático (D11); os demais, na revisão.

- ✔ Qualquer gradiente (fundo, botão, texto, SVG).
- ✔ Glassmorphism, `backdrop-filter`, `blur()`.
- Glow, manchas de luz, textura de ruído.
- ✔ Sombras, exceto o deslocamento de impressão do "Sortear"; nada de sombra suave difusa.
- ✔ Easing com overshoot, mola ou bounce (`cubic-bezier` com y fora de 0 a 1).
- Animações em cascata no carregamento; animação em todo hover.
- Grades de cartões idênticos; cartão como embrulho de seção.
- ✔ `border-radius` grande (acima de 4 px).
- Raio igual em tudo; bordas coloridas de destaque em cartões.
- ✔ Fontes Inter, Geist, Instrument Serif; fundo creme/marfim com serifa editorial "calma".
- ✔ Preto puro (`#000`) em texto.
- ✔ Emoji como ícone.
- Texto genérico ("Saiba mais", "Clique aqui"); metadados unidos por " · "; seta "→" em botão.

## Risks / Trade-offs

- [Redesign completo a 2 dias da apresentação] → grupos que deixam o sistema funcionando, com testes verdes e commit em cada um; se o tempo acabar, dá para parar depois de qualquer grupo e voltar o resto com `git revert`.
- [CSS reescrito quebra telas ainda não revisadas no meio do caminho] → o grupo de tokens já entrega base, campos, botões e listas genéricas, para as telas ficarem legíveis antes do seu grupo; a conferência a 360 px é feita em cada grupo, não só no fim.
- [Vermelho e sucesso reprovam em texto pequeno] → regras de D4 + token derivado `--vermelho-texto` + teste de contraste que separa os pares só-grandes.
- [Chip selecionado e estrela acesa em amarelo têm pouco contraste de luminância com o papel (1,26:1)] → o amarelo fica sempre dentro de contorno de tinta (12,8:1 com o amarelo), o chip selecionado ganha texto 700 e a nota aparece em número ("Sua nota: 4"); o estado vai para leitores de tela por `checked`/`aria-pressed`.
- [Títulos longos estouram a 120 px ou a 360 px] → classe `titulo-longo`, `overflow-wrap: anywhere`, `text-wrap: balance`; o seed tem títulos de vários tamanhos para conferir.
- [Navegador sem suporte a `font-stretch` em fonte variável] → o texto cai para a largura normal do Archivo, ainda legível; todos os navegadores atuais suportam.
- [Testes acoplados a classes CSS] → classes mantidas (D2); só os trechos de HTML que mudam de verdade são atualizados, no grupo da tela.
- [Pillow sem suporte a WebP] → conferir `PIL.features.check("webp")` antes; se faltar, usar `cwebp` (pacote `webp`) só na máquina de quem gera as capturas.

## Migration Plan

Sem migração de dados (schema não muda). Implantação = atualizar o código e reiniciar o servidor. Rollback = `git revert` dos commits desta mudança, em ordem inversa (cada grupo é um commit).
