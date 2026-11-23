# Proposal: refaz-identidade-visual

## Why

O design system "Midnight Stage" (mudança `add-estatisticas-e-visual`) ficou com cara de interface gerada por IA: gradiente violeta-rosa, vidro fosco, glow, manchas de luz no fundo, easing com mola, cartões arredondados em tudo e tema escuro de dashboard. Nada disso vem do contexto do app, que é o caderno de repertório de quem toca em roda de violão. Antes da apresentação de 24/11, o trio quer uma identidade com autor, tirada desse contexto, e um nome mais curto: "Shuffle".

## What Changes

**Nome**
- O app passa a se chamar **Shuffle** (antes "Shuffle Meu") em tudo que é visível ou documental: marca na navegação ("SHUFFLE"), `<title>` das páginas, textos da interface, README, `docs/plan.md`, `openspec/config.yaml`, specs, `design.md` e testes.
- **Não** mudam: o pacote Python `shuffle_meu`, o comando `flask --app shuffle_meu run`, o arquivo do banco (`instance/shuffle.db`) e os nomes de pastas. As mudanças arquivadas também não são reescritas (são histórico).

**Identidade visual "Lambe-lambe"** (substitui o "Midnight Stage" por inteiro)
- Referência: cartaz lambe-lambe de show colado no muro (tipos de madeira, cores chapadas, letras condensadas gigantes) e a folha de setlist presa com fita no chão do palco.
- Tema claro em papel-jornal frio (`#F3F2EE`), tinta `#161616`, duas cores de impressão (amarelo `#FFD60A` e vermelho `#E4371E`), réguas no lugar de cartões, raio 0 nos blocos e 4 px só em controles.
- Fontes locais (Fontsource, OFL): Big Shoulders Display (títulos e música sorteada), Archivo (texto e interface, largura condensada em rótulos e chips) e IBM Plex Mono (números). Saem Geist, Geist Mono e Instrument Serif.
- Telas redesenhadas: navegação, início (composição de cartaz assimétrica), resultado do sorteio (roleta vertical e carimbo "TOCA ESSA!"), repertório em lista de setlist numerada, formulários, artistas, playlists, histórico e estatísticas.
- **Regras anti-slop** escritas no `design.md` e conferidas por teste: sem gradiente, vidro, `backdrop-filter`, glow, ruído, sombra difusa, easing com mola, animação em cascata, emoji como ícone e preto puro em texto.
- Emoji saem dos botões ("Toquei ✅" vira "Toquei" com ícone de traço; "Pular ⏭️" vira "Pular").
- Microtexto em português informal e específico onde o texto não é fixado pelas specs (ver `design.md`). A única mensagem citada em spec que muda é a da RN05, que passa a ser "Nada com esse filtro. Tira algum?" (a regra em si não muda).

**Continua igual:** stack (Flask + Jinja + CSS/JS puros), rotas, banco, regras de negócio RN01 a RN08, as demais mensagens citadas nas specs, responsividade a 360 px, contraste AA, movimento reduzido, teclado e funcionamento sem internet.

### Fora do escopo
Modo escuro, temas, renomear o pacote Python, mudar o schema, mudar outras mensagens citadas nas specs e qualquer funcionalidade nova.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `interface`: novos requisitos para o nome "Shuffle", a identidade visual "Lambe-lambe" e as proibições anti-slop verificáveis; o requisito de contraste deixa de citar o gradiente e passa a cobrir as cores de impressão; o de movimento reduzido passa a listar as animações que existem agora (roleta, carimbo, deslocamento do "Sortear").
- `sorteio`: a revelação animada passa a ser uma roleta vertical com desaceleração sem repique, terminando no carimbo "TOCA ESSA!"; a mensagem da RN05 passa a ser "Nada com esse filtro. Tira algum?".

## Impact

- Código: `static/style.css` reescrito; todos os templates (marcação de telas, sem mudar rotas nem campos de formulário); `static/app.js` (roleta vertical, carimbo; sai o "pop" com mola); `templates/_macros.html` (capa chapada em 3 cores).
- Python: nenhuma mudança de comportamento; o texto da constante da RN05 em `sorteio.py` e comentários e docstrings com o nome antigo (`seed.py`, `schema.sql`).
- Estáticos: `static/fonts/` troca os arquivos e as licenças OFL.
- Testes: `test_contraste.py` e `test_design.py` reescritos para os tokens novos e as regras anti-slop; testes que conferem trechos de HTML alterados (emoji dos botões, capa, título da tela) atualizados junto com cada tela. Os testes funcionais continuam passando.
- Documentação: README (nome, descrição do design, créditos das fontes), `docs/plan.md`, `openspec/config.yaml` e screenshots novos em WebP em `docs/screenshots/`, substituindo os PNG.
- Dependências: nenhuma nova no projeto. O Pillow (já instalado na máquina) só é usado para converter os screenshots para WebP e não entra no `requirements.txt`.
