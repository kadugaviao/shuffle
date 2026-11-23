# Proposal: revisao-final

## Why

A auditoria de 23/11/2026 (`docs/revisao-final.md`) confirmou que o Shuffle cumpre o trabalho de G2: 5 tabelas, CRUD completo, OpenSpec com specs antes do código e repositório público. Também não encontrou falha de segurança real para uso local. Mas a tela mais importante da demonstração, o resultado do sorteio, quebra regras do próprio design system:
- vazio à direita no desktop;
- 4 botões empilhados competindo com "Toquei" e "Pular";
- o player empurrando as ações para fora da tela.

O README também não segue a estrutura da entrega e não tem os passos de clonar, e os screenshots são inconsistentes. Esta mudança corrige esses pontos antes da apresentação de 24/11, sem mudar a direção visual.

## What Changes

Itens do relatório incluídos: todos os de severidade Alta e Média, e os de severidade Baixa com esforço P (IDs entre parênteses).

**Tela de resultado (D1–D5, D10, D11, B2, A4)**
- A folha ocupa a largura do contêiner. A partir de 960 px tem duas colunas: à esquerda capa, data, título, carimbo, artista, **Toquei / Pular** e estrelas; à direita, o bloco **"Ouvir aqui"**, separado por régua.
- **"Ouvir aqui"**:
  - Com os dois serviços, um seletor segmentado **[YouTube | Spotify]**, sem nenhum selecionado até o clique. Com um serviço, o botão simples "Ouvir aqui".
  - O player abre no bloco, sem empurrar as ações, com o botão **"Fechar player"** e um aviso para leitores de tela.
  - Os links **"Abrir no YouTube"**, **"Abrir no Spotify"** e **"Abrir link"** viram links de texto pequenos com ícone, numa linha só.
- No celular a ordem é: ações primeiro, depois ouvir e abrir.
- O carimbo vai para o topo da folha. A data fica numa linha só.
- O degrau de título longo por palavra de mais de 8 letras vale só no celular.
- A roleta deixa de depender de um valor fixo de altura.

**Outras telas (D6–D9, D12, D13, D15, B1, S3)**
- Início no celular: "Última sorteada" em linha compacta logo abaixo do "Sortear".
- "Sortear" com resposta ao passar o mouse.
- Repertório a 360 px com a dificuldade em posição fixa.
- Aba atual destacada também pela cor do rótulo.
- Plural correto ("1 música", "8 músicas").
- Ícone de sortear no convite do histórico vazio.
- Repertório totalmente vazio: "Caderno em branco", sem filtros.
- Remover de uma playlist uma música que não está nela avisa "Essa música não está na playlist." em vez de confirmar a remoção.

**Formulários e acessibilidade (A1–A3, A5, A6, SEG1)**
- Foco no primeiro campo com erro e `aria-required` nos obrigatórios.
- Dica de formato abaixo dos campos de link.
- Nome acessível do interruptor igual ao rótulo visível ("Fora do sorteio: …").
- Avisos anunciados por uma região live preenchida depois do carregamento.
- `role="list"` nas listas sem marcador.
- Limites de tamanho dos textos validados também no servidor (os mesmos do formulário), com erro junto ao campo.

**Specs e testes (S1, S2)**
- Cenário e teste do sorteio filtrado por gênero.
- Cenário de remover música que não está na playlist.
- Toda correção de bug ganha teste que falha antes e passa depois.

**Documentação (DOC1–DOC4, SEG2)**
- README reescrito na estrutura pedida, com equipe, requisitos com versões, como rodar, comandos úteis, problemas comuns, OpenSpec, stack, pastas, screenshots e limitações. Cada comando testado numa cópia limpa.
- Screenshots refeitos com viewport e enquadramento padronizados.
- `docs/plan.md` com os critérios de pronto marcados.
- `Flask==3.1.3` fixado no `requirements.txt`.

**Continua igual:** banco e schema, regras de negócio RN01 a RN08, rotas, regras do player (só carrega no clique, IDs validados, atributos do iframe), design system "Lambe-lambe" e Anti-slop.

### Fora do escopo (trabalho futuro)

- **Arriscado às vésperas ou muda a direção visual:**
  - CSRF (SEG3);
  - rótulo do "Abrir link" conforme o domínio do conteúdo (D14);
  - recomposição da coluna direita do Início no desktop (D16);
  - estrelas como `radiogroup` (A7);
  - avisos no fluxo da página em vez de flutuantes (A8), porque a spec exige aviso flutuante;
  - testes automáticos de navegador para responsividade, teclado e movimento reduzido (S4).
- **Funcionalidades:**
  - tocar arquivo de áudio local;
  - gravar a própria versão pelo microfone;
  - players de SoundCloud e Deezer.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `sorteio`: filtro por gênero com cenário próprio; o resultado passa a oferecer "Ouvir aqui" com seletor [YouTube | Spotify], links "Abrir no…" e "Fechar player".
- `musicas`: cenário de repertório totalmente vazio ("Caderno em branco").
- `playlists`: remover uma música que não está na playlist avisa em vez de confirmar.
- `interface`: foco no primeiro campo com erro e campos obrigatórios marcados; limite de tamanho dos textos validado no servidor.

## Impact

- **Templates:** `sorteio/resultado.html`, `inicio.html`, `musicas/lista.html`, `musicas/form.html`, `artistas/lista.html`, `artistas/form.html`, `playlists/lista.html`, `playlists/detalhe.html`, `historico.html`, `base.html`, `_macros.html`.
- **Front-end:**
  - `static/style.css`: resultado em duas colunas, seletor, links pequenos, ajustes de base 4;
  - `static/app.js`: seletor de player, fechar player, avisos em região live, rótulo acessível do interruptor.
- **Python:** `playlists.py` (remover), `musicas.py`, `artistas.py` e `playlists.py` (limites de tamanho), um filtro Jinja de plural.
- **Testes:** novos para cada correção; ajustes nos que conferem HTML exato ("música(s)", `<ul class="lista-cartoes">`, botões do player).
- **Docs:** `README.md` reescrito, `docs/screenshots/` refeitos, `docs/plan.md`, `requirements.txt`.
- **Dependências e banco:** nenhuma nova dependência, nenhuma mudança de schema.
