# Design: add-estatisticas-e-visual

## Context

O MVP (`add-mvp`, arquivado) entregou as telas em Jinja com um CSS simples, mensagens via `flash()` no topo da página e 79 testes, vários deles conferindo trechos de HTML (ex.: `<option value="3" selected>`, campos ocultos do "Pular", o `<select name="nota">`). A motivação desta mudança está em `proposal.md`; o comportamento esperado, nas specs desta mudança. Restrições que moldam o design: apresentação em 24/11 (cerca de 2 dias), Flask + Jinja + CSS/JS puros, nenhuma dependência nova, apresentação possivelmente sem internet e nenhuma mudança de schema.

## Goals / Non-Goals

**Goals:**
- Fechar a tela 7 com estatísticas calculadas por SQL sobre as tabelas existentes.
- Um design system escrito ("Midnight Stage") que o trio e a IA sigam nas próximas mudanças sem reinventar tokens.
- Melhoria progressiva: tudo funciona com HTML + formulários; o JavaScript só acrescenta animação e evita recarregar a página.
- Manter a suíte de testes verde a cada grupo de tarefas.

**Non-Goals:**
- Modo claro, temas, internacionalização.
- Sistema de componentes reutilizável fora deste projeto ou build de CSS (sem Sass, PostCSS, bundler).
- Gráficos com biblioteca; as barras são `div`s com largura em CSS.

## Decisions

### D1. Estatísticas: módulo `estatisticas.py` com consultas SQL

Uma função `calcular(db) -> dict` chamada pela rota `GET /historico`, que passa o resultado ao template. As estatísticas ficam acima da lista de sorteios, na mesma página (a tela 7 do plano é uma só: "Histórico e estatísticas"); o item do menu continua "Histórico".

```sql
-- resumo
SELECT (SELECT COUNT(*) FROM musica), (SELECT COUNT(*) FROM sorteio),
       (SELECT COUNT(*) FROM sorteio WHERE tocada = 1), (SELECT AVG(nota) FROM sorteio WHERE nota IS NOT NULL);
-- top 5 mais tocadas
SELECT m.id, m.titulo, a.nome AS artista, COUNT(*) AS vezes
  FROM sorteio s JOIN musica m ON m.id = s.musica_id JOIN artista a ON a.id = m.artista_id
 WHERE s.tocada = 1 GROUP BY m.id ORDER BY vezes DESC, m.titulo COLLATE PT LIMIT 5;
-- nunca sorteadas (só ativas)
SELECT m.id, m.titulo, a.nome AS artista FROM musica m JOIN artista a ON a.id = m.artista_id
 WHERE m.ativa = 1 AND NOT EXISTS (SELECT 1 FROM sorteio s WHERE s.musica_id = m.id) ORDER BY m.titulo COLLATE PT;
-- média de notas por música
SELECT m.id, m.titulo, a.nome AS artista, AVG(s.nota) AS media, COUNT(s.nota) AS avaliacoes
  FROM sorteio s JOIN musica m ON m.id = s.musica_id JOIN artista a ON a.id = m.artista_id
 WHERE s.nota IS NOT NULL GROUP BY m.id ORDER BY media DESC, avaliacoes DESC, m.titulo COLLATE PT;
```
- **Por gênero** é agrupado em Python: `SELECT genero FROM musica`, chave `casefold()` (vazio vira "Sem gênero"), rótulo = grafia mais frequente do grupo (empate: a primeira em ordem alfabética), ordenado por quantidade e depois pelo rótulo. Fazer isso em SQL exigiria subconsultas para a "grafia mais usada"; em Python são poucas linhas.
- **Exibição de gêneros** (em todas as telas, não só nas estatísticas): filtro Jinja `genero` põe a primeira letra em maiúscula ("pop" vira "Pop") e mantém siglas já em caixa alta ("MPB"). Só na exibição: o banco, os valores dos filtros e o campo do formulário continuam com o texto digitado.
- **Arredondamento:** a ordem usa a média exata; a exibição usa um filtro Jinja `decimal1` com `Decimal(...).quantize(Decimal("0.1"), ROUND_HALF_UP)` e vírgula ("4,25" vira "4,3"). O `round()` do Python arredonda para o par e mostraria "4,2".
- **Barras:** largura proporcional ao maior valor da seção, passada como `style="--p: 75%"`.
- Listas longas ("nunca sorteadas" e "médias") mostram 10 itens e o resto dentro de um `<details>` "Ver todas (N)".
- *Alternativa:* uma tela `/estatisticas` separada. Rejeitada para não criar uma sexta aba no menu do celular e porque o plano define uma tela só.

### D2. Atalhos de favorita e ativa

Rotas `POST /musicas/<id>/favorita` e `POST /musicas/<id>/ativa` com o campo `valor` (0 ou 1): gravam o estado pedido, não invertem (clique repetido ou página antiga não desfazem a ação). Id inexistente: 404; `valor` diferente de 0/1: 400.
- O formulário de cada atalho leva a query string atual na `action` (`/musicas/5/favorita?genero=rock`); sem JavaScript a rota redireciona para `url_for("musicas.lista", **request.args)` + `#musica-5`, voltando com os mesmos filtros e à mesma posição. Usar `request.args` em vez de um `next` livre evita redirecionamento aberto.
- Com JavaScript, `app.js` intercepta o envio, faz `fetch` do mesmo POST e, se `res.ok`, troca o estado no lugar (sem recarregar) com a micro-animação; se falhar, envia o formulário normalmente.
- Marcação: favorita é `<button aria-pressed>` com ícone de coração; ativa é `<button role="switch" aria-checked>`. Cada um tem `aria-label` com o título da música.

### D3. Avaliação com 5 estrelas

O formulário de avaliação só é renderizado quando `tocada = 1`. São 5 `<button name="nota" value="1..5">` com `aria-label="Dar nota N de 5"` e `aria-pressed` na nota atual; a rota `POST /sorteios/<id>/avaliar` não muda e continua validando a RN07.
- Acender em sequência no hover/foco sem `:has()`: `.estrelas:hover .estrela, .estrelas:focus-within .estrela` acende todas, e `.estrela:hover ~ .estrela, .estrela:focus-visible ~ .estrela` apaga as seguintes. Funciona em qualquer navegador atual.
- Depois de "Toquei" as estrelas entram com um pop escalonado (mola, 40 ms entre elas).

### D4. Revelação estilo roleta

- `POST /sortear` grava `session["revelar"] = id_do_sorteio` antes do redirect; `GET /sorteios/<id>` faz `session.pop("revelar", None) == id`. Assim só a primeira visualização depois de sortear anima: recarregar ou abrir pelo histórico não repete, sem mexer na URL.
- Quando revela, o template põe no cartão `data-roleta='[...]'` com até 12 títulos de músicas ativas (`ORDER BY RANDOM() LIMIT 12`), mais o título sorteado no fim.
- `base.html` tem um script inline mínimo no `<head>`, `document.documentElement.classList.add("js")`, para o CSS esconder o resultado **antes** da primeira pintura (`.js [data-roleta] .revelavel { visibility: hidden }`) e não piscar a resposta.
- `app.js` troca o título de um "rolo" com intervalos crescentes (cerca de 14 passos, de 40 ms até 220 ms, total de ~1,2 s, abaixo do teto de 1,5 s da spec) e, no fim, mostra o resultado real com glow e pop; a região do resultado tem `aria-live="polite"` e só o título final é anunciado.
- **Rede de segurança:** se o JS falhar, uma animação CSS `aparecer 0s 2s forwards` torna o resultado visível depois de 2 s. Sem JS a classe `js` não existe e nada é escondido. Com `prefers-reduced-motion`, o CSS não esconde e o JS não roda.

### D5. Erros junto ao campo

- `validar_musica()` passa a devolver `(dados, erros)` com `erros` como `dict` `{campo: mensagem}`; `_validar()` de artistas faz o mesmo (`{"nome": ...}`). A duplicata da RN02 vai para `titulo`, artista inexistente para `artista_id`, nome repetido de artista para `nome`.
- As playlists deixam de redirecionar no erro: o `POST /playlists` e o `POST /playlists/<id>/editar` inválidos renderizam a própria tela com o erro no campo e os dados digitados.
- Um macro Jinja `campo()` em `templates/_macros.html` gera label, controle, `aria-invalid="true"`, `aria-describedby` e o `<p class="erro-campo" id="erro-<campo>">`; todos os formulários usam esse macro.
- Erros que não são de campo (RN05, RN07, exclusão de artista com músicas) continuam como `flash(..., "erro")` e viram toasts persistentes.

### D6. Toasts

`base.html` renderiza as mensagens de `flash` numa região fixa (`<section class="toasts" aria-label="Avisos">`), cada uma com `role="status"` (sucesso) ou `role="alert"` (erro/aviso) e um botão de fechar que começa `hidden` e o JS revela. Categoria padrão (`message`) = sucesso, some em 5 s, pausando com hover ou foco; `erro` e `aviso` ficam até fechar. Sem JS, as mensagens ficam visíveis e estáticas. Posição: canto superior direito no desktop, acima da barra de navegação no celular.

### D7. Navegação com aba atual

A seção atual vem de `request.blueprint` (`sorteio` → Início, `musicas` → Repertório, `artistas`, `playlists`, `historico`), então formulários, detalhe de playlist e resultado destacam a seção certa sem configuração por rota. O item atual recebe `aria-current="page"`. Abaixo de 720 px o mesmo `<nav>` vira barra inferior fixa (ícone em cima, nome embaixo), e o `main` ganha `padding-bottom: calc(72px + env(safe-area-inset-bottom))` para a barra não cobrir o fim da página.

### D8. Fontes e ícones locais

- Fontes em woff2 tiradas dos pacotes npm do Fontsource (licença OFL 1.1): `@fontsource-variable/geist` e `@fontsource-variable/geist-mono` (variáveis, um arquivo cobre 400–600) e `@fontsource/instrument-serif` (itálico 400). Só os subconjuntos `latin` e `latin-ext` (acentos do português), baixados com `npm pack` numa pasta temporária: **nada vai para o `package.json`**, porque não há Node no projeto. Ficam em `static/fonts/` com o `OFL.txt`. `font-display: swap` e `<link rel="preload">` para a Geist.
- Pilhas de fallback: Geist → `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`; Instrument Serif → `Georgia, "Times New Roman", serif`; Geist Mono → `ui-monospace, "SF Mono", Menlo, Consolas, monospace`.
- Ícones: SVG inline com os traçados do Lucide (licença ISC, crédito no README), num macro `icone(nome)` em `templates/_icones.html`; `stroke-width="1.5"`, `aria-hidden="true"` quando acompanham texto.
- *Alternativa:* Google Fonts por `<link>`. Rejeitada porque a apresentação pode ser offline.

### D9. Fundo, vidro e desempenho

- O fundo é uma camada `body::before` fixa com 2 a 3 `radial-gradient` (violeta e rosa, baixa opacidade) animada só com `transform` em ciclos de 40 a 60 s; sem `filter: blur`, que custa caro em celular (o gradiente radial já é difuso). A textura de ruído é um SVG `feTurbulence` em data URI, em `body::after`, com opacidade 0,03. As duas camadas usam `pointer-events: none`.
- `backdrop-filter: blur()` só nas camadas fixas (navegação e toasts). Os cartões usam a superfície translúcida + borda + brilho interno, o que dá o efeito de vidro sem desfocar 25 elementos de uma vez. Onde não há suporte (`@supports not (backdrop-filter: blur(1px))`), a navegação usa `rgba(10,10,15,0.92)`.
- O glow pulsante do "Sortear" anima a `opacity` de um pseudo-elemento, não o `box-shadow` (que repinta a cada quadro).

### D10. Capa gerada

Filtro Jinja `matiz(texto)` = `zlib.crc32(texto.encode()) % 360` (determinístico entre execuções, ao contrário de `hash()`) e filtro `iniciais(nome)` (até 2 letras das palavras do nome do artista). CSS: `linear-gradient(135deg, hsl(var(--h) 70% 45%), hsl(calc(var(--h) + 40) 75% 28%))`. A capa é decorativa (`aria-hidden="true"`), porque o nome do artista aparece em texto ao lado.

### D11. Chips e controles

Filtros de escolha única (humor, dificuldade máxima, gênero) viram `input type="radio"` visualmente escondidos com `<label>` em pílula, com "Todos" como `value=""`; "Só favoritas" vira um checkbox em pílula. São controles nativos: funcionam sem JS, pelo teclado e enviam o mesmo formulário de antes, então as rotas não mudam. Artista e playlist continuam `select` (podem ter muitas opções), estilizados como vidro. No formulário de música, humor vira chips e dificuldade vira um seletor segmentado 1–5 (radios).

### D12. JavaScript

Um único `static/app.js`, sem dependências, em funções independentes: confirmação de exclusão (já existe), toasts, atalhos do repertório, roleta, pop dos botões. Cada função começa checando se o seu elemento existe na página e respeita `matchMedia("(prefers-reduced-motion: reduce)")`.

### D13. Testes

- Cada grupo de tarefas atualiza os testes que conferiam o HTML antigo daquela tela, em vez de deixar para o fim.
- Novos testes: estatísticas (unidade sobre `calcular()` com dados controlados, cobrindo empate, arredondamento e gênero), atalhos (estado explícito, 404, 400, filtros preservados), estrelas só após tocar, `revelar` na sessão, `aria-current`, tela inicial vazia, erros por campo.
- `tests/test_contraste.py` lê os tokens de cor do `:root` em `style.css` e calcula o contraste WCAG das combinações de texto usadas, falhando abaixo de 4,5:1 (3:1 para texto grande). Assim o requisito de contraste vira teste automático, e não só conferência visual.

## Design system "Midnight Stage"

Fonte da verdade visual para esta e as próximas mudanças. Valores definidos pelo trio; os marcados com * foram derivados aqui para cumprir o contraste AA ou completar a escala.

### Conceito e princípios

Palco de show à noite: interface escura, cartões de vidro fosco flutuando sobre luz difusa, um único gradiente vibrante como destaque.
- **A ousadia fica num lugar só:** o momento memorável é o botão "Sortear" e a revelação da música. O resto da interface é silencioso.
- **O gradiente é raro:** só aparece no botão "Sortear", no CTA do estado vazio, no ponto da aba atual, nas barras das estatísticas, no anel de foco, nas estrelas acesas e no glow da música sorteada. Nunca como fundo de seção ou decoração.
- **Texto em caixa normal** (sentence case): sem rótulos em caixa alta, sem "eyebrows" acima de títulos, sem setas "→" em botões, sem metadados unidos por " · " (dados viram chips ou linhas separadas).
- **Monoespaçada só para números** (contagens, notas, métricas), nunca para rótulos.

### Tokens (`:root` em `style.css`)

| Token | Valor | Uso |
|---|---|---|
| `--fundo` | `#0A0A0F` | fundo da página |
| `--superficie` | `rgba(255,255,255,0.04)` | cartões, inputs |
| `--superficie-alta`* | `rgba(255,255,255,0.07)` | hover de cartão, chip selecionado |
| `--borda` | `rgba(255,255,255,0.08)` | bordas |
| `--borda-hover` | `rgba(255,255,255,0.16)` | bordas no hover/foco |
| `--texto` | `#F5F5F7` | texto principal (18,1:1 no fundo) |
| `--texto-2` | `#A1A1AA` | texto secundário (7,7:1) |
| `--texto-apagado` | `#52525B` | **só** controles desabilitados e decoração (2,6:1, não passa AA) |
| `--texto-sobre-gradiente`* | `#0A0A0F` | todo texto sobre o gradiente (mínimo 4,7:1 nas três cores) |
| `--gradiente` | `linear-gradient(135deg, #8B5CF6 0%, #EC4899 50%, #F59E0B 100%)` | destaque |
| `--sucesso` / `--aviso` / `--perigo` | `#22C55E` / `#F59E0B` / `#EF4444` | estados (todos ≥ 4,8:1 na superfície) |
| `--raio-controle` / `--raio-cartao` / `--raio-pilula` | `12px` / `20px` / `999px` | raios |
| `--sombra-cartao` | `0 8px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06)` | cartões |
| `--glow` | `0 0 32px rgba(236,72,153,0.45), 0 0 64px rgba(139,92,246,0.30)` | elemento em destaque |
| `--mola` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | interações (150–250 ms) |
| `--entrada` | `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out) | entradas |
| `--espaco-1..7`* | `4, 8, 12, 16, 24, 32, 48px` | espaçamento (base 4) |

**Por que texto escuro sobre o gradiente:** branco sobre a ponta âmbar (`#F59E0B`) dá 2,15:1, e sobre o rosa 3,53:1; ambos reprovam no AA para texto normal. `#0A0A0F` dá 4,66:1 no violeta, 5,60:1 no rosa e 9,20:1 no âmbar.

### Tipografia

| Papel | Fonte | Tamanho / peso |
|---|---|---|
| Título de página (h1) | Instrument Serif itálico | `clamp(2rem, 6vw, 2.75rem)`, altura de linha 1,1 |
| Música sorteada | Instrument Serif itálico | `clamp(2.5rem, 9vw, 4.5rem)`, altura de linha 1,05 |
| Título de seção (h2) | Geist 600 | 1.25rem |
| Texto | Geist 400 | 1rem (16 px), altura de linha 1,5; linhas de até ~70 caracteres |
| Secundário / chips | Geist 500 | 0.875rem (mínimo para leitura) |
| Rótulo da barra inferior (celular) | Geist 500 | 0.75rem: única exceção ao mínimo, sempre acompanhado de ícone |
| Números de métrica | Geist Mono 500, `tabular-nums` | 2.5rem |
| Números em lista | Geist Mono 400, `tabular-nums` | 0.875–1rem |

### Layout

- Largura máxima do conteúdo: 64rem, alinhado à esquerda dentro do contêiner centralizado, ocupando a mesma largura da navegação (nenhuma tela deixa um vazio de um lado só); o resultado do sorteio é a única tela centralizada.
- Início: a partir de 960 px, duas colunas (sorteio e filtros à esquerda, cartão da última sorteada à direita, 20rem). Sem sorteios, a coluna da direita mostra um cartão de espera no mesmo estilo; abaixo de 960 px ele não aparece.
- Repertório: grade `repeat(auto-fill, minmax(16rem, 1fr))` no desktop, uma coluna no celular.
- Ponto de quebra único: 720 px (barra de navegação muda de cima para baixo).
- Camadas (`z-index`): fundo −1, conteúdo 0, navegação 10, toasts 20.

```
Desktop                                     Celular (360 px)
┌──────────────────────────────────────┐    ┌──────────────────┐
│ Shuffle Meu  (Início)•Repertório ... │    │ Shuffle Meu      │
├──────────────────────────────────────┤    ├──────────────────┤
│  Sortear (gradiente, largo)          │    │ Sortear          │
│  humor: [Todos][Calma][Animada]...   │    │ [Todos][Calma].. │
│  dificuldade: [1][2][3][4][5]        │    │ [1][2][3][4][5]  │
│  artista ▾   playlist ▾   N [5]      │    │ artista ▾        │
│  Última sorteada: ...                │    ├──────────────────┤
└──────────────────────────────────────┘    │ ⌂  ♫  🎤  ≡  ⟲   │  ← barra inferior
                                            └──────────────────┘
```

### Componentes

| Componente | Descrição |
|---|---|
| Fundo de palco | 2–3 manchas radiais violeta/rosa em movimento lento + ruído SVG a 3% |
| Navegação | barra de vidro fixa com links em pílula; atual com `--superficie-alta` e ponto no gradiente; vira barra inferior com ícones abaixo de 720 px |
| Botão "Sortear" | grande, gradiente com `background-position` deslizando em loop lento (~8 s), glow pulsando de leve, pop ao clicar (0,96 → 1,04 → 1 com `--mola`) |
| Botão secundário | vidro (`--superficie`) com borda fina; hover sobe a borda para `--borda-hover` |
| Botão de perigo | só texto `--perigo` até o hover, quando ganha fundo `rgba(239,68,68,0.12)` |
| Chip | pílula com borda; selecionado com `--superficie-alta`, borda `--borda-hover` e texto `--texto` |
| Cartão de música | capa gerada (quadrado 56 px, raio 12), título, artista, chips de gênero/humor, barrinhas de dificuldade (5, preenchidas = nível, `aria-label="Dificuldade 3 de 5"`), atalhos coração e interruptor |
| Interruptor (ativa) | trilho 40×24 (área de toque maior), bolinha com `--mola`; ligado = verde `--sucesso` |
| Coração (favorita) | traço quando desligado, preenchido em `--perigo`/rosa quando ligado, pop de 1,2× |
| Resultado | cartão central com capa grande, título em Instrument Serif, artista, link, "Toquei ✅", "Pular ⏭️" e estrelas após tocar; revelação estilo roleta |
| Estrelas | 5 botões; acesas com o gradiente, hover acende em sequência, pop no clique |
| Cartão de métrica | número grande em Geist Mono + rótulo em `--texto-2` |
| Ranking / barras | nome à esquerda, número em Mono à direita, barra no gradiente com largura `--p` |
| Input / select | vidro, raio 12; foco com anel no gradiente (borda transparente + `background` em duas camadas `padding-box`/`border-box`) |
| Erro de campo | texto `--perigo` abaixo do campo, ícone de alerta, campo com borda `--perigo` |
| Toast | vidro com blur, borda à esquerda na cor do estado, botão de fechar |
| Estado vazio | ícone grande (64 px, traço 1.5) em `--texto-2`, frase curta, CTA no gradiente |

### Movimento

- Interações (hover, clique, alternar): 150–250 ms com `--mola`.
- Entradas (toasts, estrelas, resultado): 200–300 ms com `--entrada`.
- Laços contínuos só em dois lugares: fundo (40–60 s) e botão "Sortear" (~8 s de gradiente + pulsação de ~3 s). Nada mais anima sem ação do usuário.
- Sem animação de entrada em cada cartão nem em cada seção.
- `@media (prefers-reduced-motion: reduce)`: zera durações de animação e transição, para os laços contínuos e desliga a roleta (D4).

### Texto da interface

Verbos diretos e consistentes: o botão "Salvar" gera "Música salva."; "Excluir" gera "Música excluída.". Estados vazios dizem o que fazer ("Cadastre sua primeira música"). Erros dizem o que corrigir, sem pedir desculpas. Emoji só em "Toquei ✅" e "Pular ⏭️", como no plano.

## Risks / Trade-offs

- [Redesign completo a ~2 dias da apresentação] → as tarefas deixam o sistema funcionando ao fim de cada grupo, com testes verdes; vale commitar por grupo para poder voltar atrás. Se o tempo acabar, as telas ainda não redesenhadas continuam funcionais com os estilos antigos.
- [Testes acoplados ao HTML antigo quebram a cada tela] → cada grupo atualiza os seus testes (D13); conferir comportamento (banco, mensagens) e não classes CSS.
- [`backdrop-filter` e gradientes animados pesam em celular fraco] → blur só nas camadas fixas, animação só de `transform`/`opacity` (D9); `prefers-reduced-motion` desliga tudo.
- [Resultado piscar antes da roleta, ou sumir se o JS quebrar] → classe `js` inline no `<head>` + animação CSS de segurança de 2 s (D4).
- [Fontes baixadas de um pacote npm sem `package.json`] → os arquivos woff2 e o `OFL.txt` ficam versionados em `static/fonts/`; o design registra a origem e a versão (5.3.0) para atualizar depois.
- [Cor da capa gerada pode ficar pouco legível] → a capa é decorativa e as iniciais não são a única fonte da informação (o nome do artista está ao lado).
- [Sessão do Flask guarda `revelar`] → é um cookie assinado com `SECRET_KEY`; com a chave fixa de desenvolvimento, só afeta a animação, nada de dado sensível.

## Migration Plan

Sem migração de dados (o schema não muda). Implantação = atualizar o código e reiniciar o servidor. Rollback = voltar o commit.
