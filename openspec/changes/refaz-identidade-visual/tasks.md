# Tasks: refaz-identidade-visual

Referências: comportamento em `specs/*/spec.md`, decisões em `design.md` (D1–D13) e nas seções "Design system 'Lambe-lambe'" e "Anti-slop". Testes com `python -m unittest` a partir da raiz. Ao fim de cada grupo a suíte inteira DEVE estar verde e o grupo é commitado como `feat(visual): grupo N - <nome>` (o grupo 1 como `chore(nome): ...`). Conferência visual de cada grupo a 360 px e a 1440 px, com o seed carregado.

## 1. Renomeação para "Shuffle"

- [x] 1.1 Commitar os artefatos desta mudança antes de qualquer código (`docs: specs refaz-identidade-visual`); verificar com `git log -1 --stat` que só arquivos de `openspec/changes/refaz-identidade-visual/` entraram
- [x] 1.2 Em `base.html`, trocar o `<title>` para `{% block titulo %}{% endblock %} | Shuffle` e o texto da marca para "Shuffle" (a caixa alta vem do CSS, D5); criar em `tests/test_interface.py` o teste de nome (título termina com "| Shuffle", marca presente, "Shuffle Meu" ausente em Início, resultado, Repertório, formulário de música, Artistas, Playlists e Histórico); verificar que o teste passa e falha se a marca voltar a "Shuffle Meu"
- [x] 1.3 Trocar o nome em README, `docs/plan.md` (título, apresentação, tabela de passos e a descrição da tela 6 sem emoji nos botões), `openspec/config.yaml` (`context`) e nos comentários de `seed.py`, `schema.sql`, `app.js` e `style.css`, tirando o 🎵 dos títulos; verificar com `git grep -n "Shuffle Meu" -- . ':!openspec/changes/archive' ':!openspec/changes/refaz-identidade-visual'` sem resultado e com `git grep -n shuffle_meu` mostrando o pacote, o comando e os imports intactos (D1)
- [x] 1.4 Rodar a suíte e `flask --app shuffle_meu run` seguindo o README; verificar que tudo passa e a aba do navegador mostra "Início | Shuffle"; commitar o grupo

## 2. Tokens, fontes e base

- [x] 2.1 Baixar com `npm pack` numa pasta temporária `@fontsource-variable/big-shoulders-display`, `@fontsource-variable/archivo` e `@fontsource/ibm-plex-mono` 5.3.0 e copiar para `static/fonts/` só os arquivos de D3 (latin e latin-ext) e a licença de cada família (`OFL-big-shoulders-display.txt`, `OFL-archivo.txt`, `OFL-ibm-plex-mono.txt`); apagar Geist, Geist Mono, Instrument Serif e as licenças deles; verificar que `git status` não mostra `package.json` nem `node_modules` e que cada arquivo responde 200 em `/static/fonts/...`
- [x] 2.2 Reescrever `static/style.css` do zero (D2) com: tokens do design system em `:root`, `@font-face` (`font-display: swap`, `font-stretch: 62% 125%` no Archivo), base (papel, escala tipográfica em degraus de D6, `:focus-visible`), contêiner de 72rem, componentes genéricos (botões primário/secundário/perigo/ícone, input, select, chip, etiqueta, régua, linha de lista, folha com fita, toast, estado vazio) e o bloco `prefers-reduced-motion`; sem `body::before`/`::after`; verificar abrindo cada tela a 360 px que tudo está legível e sem rolagem horizontal, mesmo antes do grupo da tela
- [x] 2.3 Em `base.html`: tirar o `<svg>` com `gradiente-svg`, trocar `theme-color` para `#161616` e o preload para Big Shoulders e Archivo (latin); verificar no painel Rede que as três famílias carregam do próprio servidor e que nenhuma requisição sai para outro domínio
- [x] 2.4 Reescrever `tests/test_contraste.py` para os tokens novos e os pares de D4 (4,5:1: tinta e tinta-2 sobre papel e papel-2, tinta sobre amarelo, papel e amarelo sobre tinta, `--vermelho-texto` sobre papel e papel-2; 3:1, só texto grande: papel sobre vermelho, vermelho e sucesso sobre papel); verificar que passa e que falha se `--tinta-2` virar `#8A8A86`
- [x] 2.5 Criar em `tests/test_design.py` o teste anti-slop do CSS (D11): sem `gradient(`, `backdrop-filter`, `blur(`, `#000` como cor, `cubic-bezier` com y fora de [0, 1], `border-radius` acima de 4 px, `font-family` fora das três famílias + fallbacks, uma `box-shadow` só; e o teste de que `static/fonts/` só tem as três famílias; verificar que passa e que falha ao acrescentar `border-radius: 12px` ou `linear-gradient(...)` numa regra
- [x] 2.6 Atualizar os créditos de fontes no README (Big Shoulders Display, Archivo, IBM Plex Mono, OFL 1.1, via Fontsource); verificar os links e o caminho das licenças; suíte verde; commitar o grupo

## 3. Navegação e avisos

- [x] 3.1 Navegação de D2/Componentes: faixa de tinta com "SHUFFLE" em Big Shoulders amarelo e links em Archivo condensado, régua vermelha de 4 px na aba atual; abaixo de 720 px, faixa só com a marca e barra inferior fixa com ícone + rótulo de 14 px; foco amarelo dentro da faixa; verificar com os testes de `aria-current` (cenário "Seção atual") e, a 360 px, que os 5 rótulos cabem sem cortar e a barra não cobre o fim da página (cenário "Menu no celular")
- [x] 3.2 Toasts como faixa de tinta com texto papel e ícone na cor do estado; em `app.js`, entrada de 160 ms e saída de 120 ms; verificar com os testes de toasts de `test_interface.py` e, no navegador, os cenários "Confirmação some sozinha" e "Alerta fica até fechar"
- [x] 3.3 Suíte verde; commitar o grupo

## 4. Tela inicial

- [x] 4.1 Reescrever `inicio.html` como composição de cartaz: título "Bora tocar o quê?" (72/120 px, quebrando em 2–3 linhas à esquerda), botão "Sortear" vermelho largo, régua de 2 px, filtros em chips retangulares (selecionado amarelo), selects e o campo de rodadas; bloco "Última sorteada" como folha com fita na coluna de 20rem a partir de 960 px, com o mesmo texto de hoje e o bloco de espera com a frase nova de D12; verificar com os testes de `test_sorteio.py` e `test_historico.py` da tela inicial (ajustando só a frase que mudou) e, a 1440 px, que as duas colunas ficam alinhadas no topo sem vazio de um lado só
- [x] 4.2 "Sortear" com sombra `--impressao` e estado pressionado (desloca 2 px, sem sombra, 120 ms); remover `data-pop` de todos os templates e a função de pop de `app.js`; verificar com `git grep -n data-pop` vazio, teclado (Enter e Espaço sorteiam) e movimento reduzido sem deslocamento
- [x] 4.3 Macro `vazio()` sem ícone ilustrativo (título em Big Shoulders 28 px, frase, botão primário), atualizando todas as chamadas; início sem músicas com "Cadastre sua primeira música" e a frase nova; verificar com o teste "Primeiro acesso" e com `git grep -n "vazio("` mostrando só chamadas na assinatura nova
- [x] 4.4 Trocar `MSG_NENHUMA` em `sorteio.py` para "Nada com esse filtro. Tira algum?" e acrescentar em `test_sorteio.py` uma asserção do texto literal (não só da constante); verificar que os cenários "Filtro sem resultado (RN05)" e "Repertório vazio (RN05)" passam e que `git grep -n afrouxar -- shuffle_meu tests` fica vazio
- [x] 4.5 Suíte verde; commitar o grupo

## 5. Resultado do sorteio

- [x] 5.1 Macro `capa()` com classe `capa-{{ (nome|matiz) % 3 }}` (D8) no lugar de `style="--h"`; atualizar `test_capa_e_dificuldade`; verificar que Djavan dá `capa-0` e que as três cores aparecem no repertório do seed
- [x] 5.2 Reescrever `sorteio/resultado.html` como folha à esquerda: capa grande, data em Plex Mono, título com classe `titulo-longo` acima de 24 caracteres ou com palavra de mais de 9 letras, carimbo `<p class="carimbo" aria-hidden="true">` ("Toca essa!" ou "Tocada"), `status-tocada` visualmente oculto, "Toquei" e "Pular" sem emoji com ícones `check` e `pular`, rótulo "Quanto valeu?" / "Sua nota: N" e link "Mudar os filtros"; atualizar os testes que procuram "Toquei ✅" e "Pular ⏭️" e criar testes do carimbo por estado e da classe `titulo-longo`; verificar que passam (cenários "Tela de resultado" e "Sorteio já tocado")
- [x] 5.3 Roleta vertical e entrada do carimbo em `app.js` + CSS (D7): lista de títulos numa janela de uma linha, um `translateY` de 1.200 ms com `--rolar`, carimbo 1,2 → 1 em 160 ms; manter `aria-live`, a classe `js` e a rede de segurança de 2 s; verificar com os testes de `data-roleta` (só a primeira visualização revela) e no navegador: tempo total ≤ 1,5 s medido no painel Performance, sem passar do ponto, sem JS tudo aparece, movimento reduzido mostra o resultado e o carimbo parados (cenários de "Revelação animada do resultado" e "Resultado sem roleta")
- [x] 5.4 Estrelas com traço de tinta e preenchimento amarelo (sem `url(#gradiente-svg)`), entrada de 160 ms todas juntas depois de "Toquei"; verificar com os testes de estrelas de `test_historico.py` e o cenário "Avaliar pelo teclado" (Tab até a quarta, Enter, nota 4)
- [x] 5.5 Acrescentar ao teste anti-slop a checagem de emoji nos templates; verificar que passa e falha se "✅" voltar a `resultado.html`
- [x] 5.6 Suíte verde; conferir a 360 px com um título longo do seed; commitar o grupo

## 6. Repertório

- [x] 6.1 Reescrever `musicas/lista.html` como setlist: `<ol>` com régua de 2 px no topo, cada `<li class="musica-cartao">` com número em Plex Mono, capa de 48 px, título em Archivo 700, artista em `--tinta-2`, etiquetas de gênero e humor em caixa alta de 14 px, dificuldade em 5 quadradinhos, linhas alternando papel/papel-2; abaixo de 720 px a linha quebra em três; verificar com os testes de `test_musicas.py` (inclusive `musica-cartao inativa`) e a 360 px sem rolagem horizontal
- [x] 6.2 Atalhos de D9: interruptor retangular chapado (trilho 40×24, raio 0, ligado amarelo com quadrado de tinta à direita) com rótulo visível "Ativa" / "Fora do sorteio" trocado pelo JS junto com o `aria-checked`; coração preenchido em vermelho quando favorita; verificar com `test_cartao_tem_atalhos_acessiveis` (acrescentando o rótulo conforme o estado), os cenários de "Atalhos de favorita e ativa no repertório" com e sem JS e o foco visível em cada atalho
- [x] 6.3 Filtros do repertório no estilo novo e frase do estado vazio "Nada com esse filtro. Tira algum?" (o título "Nenhuma música encontrada." fica); verificar com o teste "Nada encontrado" e a 360 px
- [x] 6.4 Suíte verde; commitar o grupo

## 7. Formulários

- [x] 7.1 `musicas/form.html`: inputs com borda 2 px de tinta, rótulos em Archivo condensado, humor em chips, dificuldade em seletor segmentado de 5 quadrados com números em Plex Mono, erro em `--vermelho-texto` junto ao campo com borda vermelha; verificar com os testes de erro por campo de `test_musicas.py` (cenário "Título vazio") e pelo teclado
- [x] 7.2 `artistas/form.html` e botões dos formulários (primário vermelho em Archivo 700 20 px, secundário, excluir em `--vermelho-texto`); verificar com os testes de `test_artistas.py` e medindo no DevTools que o texto do botão primário tem 20 px e peso 700 (cenário "Botão vermelho")
- [x] 7.3 Suíte verde; conferir os formulários a 360 px; commitar o grupo

## 8. Artistas e playlists

- [x] 8.1 `artistas/lista.html` como lista de linhas com régua de 1 px, nome em Archivo 700, país em `--tinta-2` e a contagem de músicas em Plex Mono; verificar com `test_artistas.py` (`<span class="numero">`) e a 360 px
- [x] 8.2 `playlists/lista.html` e `playlists/detalhe.html` no mesmo padrão (mantendo `lista-cartoes` e `editar-playlist`), músicas da playlist como setlist numerada; verificar com `test_playlists.py` e a 360 px
- [x] 8.3 Suíte verde; commitar o grupo

## 9. Histórico e estatísticas

- [x] 9.1 Resumo em 4 números de Plex Mono 44/72 px sobre régua de 2 px, 2×2 no celular e 4 colunas separadas por régua de 1 px a partir de 720 px; verificar com `test_estatisticas.py` (`numero metrica-valor`) e o cenário "Números alinhados"
- [x] 9.2 Top 5 com barras chapadas de tinta (a primeira em vermelho), por gênero em barras de 8 px, nunca sorteadas e médias como listas de linhas com o "Ver todas (N)" de hoje; verificar com os testes de `test_estatisticas.py` e a 360 px sem rolagem horizontal
- [x] 9.3 Lista de sorteios como linhas com data em Plex Mono e etiquetas "Tocada"/nota; estado vazio "Nenhum sorteio ainda." com o botão "Que tal sortear agora?"; verificar com os testes de `test_historico.py` (lista e estado vazio)
- [x] 9.4 Suíte verde; commitar o grupo

## 10. Revisão anti-slop com a ui-craft

- [ ] 10.1 Rodar as ferramentas `check_anti_slop` e `tokens_lint` do ui-craft sobre `style.css` e os templates; corrigir o que violar a seção "Anti-slop" ou os tokens; verificar rodando de novo sem achados críticos e anotando no commit os achados aceitos e o porquê
- [ ] 10.2 Rodar em paralelo os agentes `ui-craft:design-reviewer` e `ui-craft:a11y-auditor` sobre o diff da mudança; corrigir os achados críticos e de alto impacto; verificar repetindo os testes afetados e listando no commit o que ficou para depois
- [ ] 10.3 Conferência de integração, a 360 px e a 1440 px: nenhuma tela com rolagem horizontal (cenário "Telas a 360 px"), foco visível percorrendo cada tela com Tab, movimento reduzido emulado, rede desligada com a aparência igual (cenário "Apresentação offline"), nenhum "Shuffle Meu" visível; verificar marcando cada item numa lista no corpo do commit
- [ ] 10.4 Suíte verde; commitar o grupo

## 11. Screenshots e documentação final

- [ ] 11.1 Gerar os 10 screenshots (início, resultado, repertório, formulário, histórico; celular 360 px e desktop 1440 px) com Chrome headless e converter para WebP com o Pillow (D13), num script na pasta temporária, fora do repositório; apagar os PNG; verificar que `docs/screenshots/` tem exatamente os 10 `.webp` e nenhum `.png`, e abrir cada um conferindo que a roleta terminou
- [ ] 11.2 Atualizar o README: descrição do design system "Lambe-lambe", tabela de screenshots apontando para os `.webp` e a menção às mudanças arquivadas; verificar que cada imagem citada existe (`ls`) e que o README renderiza no GitHub/visualizador de Markdown
- [ ] 11.3 Rodar a suíte, `openspec validate refaz-identidade-visual --strict` e `openspec validate --all --strict`; verificar que tudo passa; commitar o grupo

## Workflow follow-up

- Arquivar a mudança com `/opsx:archive refaz-identidade-visual` depois da revisão do trio, sincronizando as specs de `interface` e `sorteio`.
- Conferir o resultado arquivado: `openspec/specs/interface/spec.md` com os requisitos de nome, identidade e anti-slop.
