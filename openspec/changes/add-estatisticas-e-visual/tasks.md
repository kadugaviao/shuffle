# Tasks: add-estatisticas-e-visual

Referências: comportamento em `specs/*/spec.md`, decisões em `design.md` (D1–D13) e na seção "Design system". Testes com `python -m unittest` a partir da raiz. Ao fim de cada grupo a suíte inteira DEVE estar verde e o grupo é commitado como `feat(visual): grupo N - <nome>`. Prioridade: grupos 1 a 4 completos e funcionando antes de seguir para o 5.

## 1. Design system: tokens, fontes, ícones e componentes base

- [x] 1.1 Baixar os woff2 (subconjuntos `latin` e `latin-ext`) de `@fontsource-variable/geist`, `@fontsource-variable/geist-mono` e `@fontsource/instrument-serif` 5.3.0 com `npm pack` numa pasta temporária e copiar para `shuffle_meu/static/fonts/` junto com o `OFL.txt`; verificar que `git status` não mostra `package.json` nem `node_modules` e que cada arquivo é servido com status 200 por `/static/fonts/...`
- [x] 1.2 Reescrever o topo de `static/style.css` com os `@font-face` (`font-display: swap`), os tokens do design system em `:root` e a base (reset, tipografia, escala de espaços, foco visível); verificar que a tela inicial carrega as três fontes no painel Rede do navegador
- [x] 1.3 Criar `tests/test_contraste.py`, que lê os tokens de cor do `:root` e confere 4,5:1 para `--texto`, `--texto-2`, `--perigo`, `--sucesso`, `--aviso` sobre `--fundo` e sobre a superfície efetiva, e para `--texto-sobre-gradiente` sobre as três cores do gradiente; verificar que o teste passa e que ele falha se `--texto-2` for trocado por `#52525B`
- [x] 1.4 Criar `templates/_icones.html` com o macro `icone(nome)` (traçados do Lucide, traço 1.5, `aria-hidden`) para: dado, música, microfone, lista, histórico, coração, estrela, check, pular, fechar, mais, lápis, lixeira, busca, link externo, alerta; verificar renderizando cada ícone numa página de teste temporária (removida depois) e com teste que confere o `<svg` gerado
- [x] 1.5 Criar `templates/_macros.html` com os macros `campo()` (label, controle, `aria-invalid`, `aria-describedby`, erro), `chips()` (radios em pílula com "Todos"), `capa()` e `dificuldade()`; e os filtros Jinja `matiz`, `iniciais` e `decimal1` em `__init__.py`; verificar com testes unitários dos filtros (`matiz` estável entre execuções, `iniciais("Chitãozinho & Xororó")`, `decimal1(4.25) == "4,3"`)
- [x] 1.6 CSS dos componentes base (botão primário com gradiente e pop, secundário, perigo, chip, input/select de vidro com anel de foco no gradiente, cartão, erro de campo, interruptor, coração, estrelas, toast, estado vazio), com o bloco `prefers-reduced-motion`; verificar numa página de teste temporária (removida depois) a 360 px e no desktop

## 2. Base e navegação

- [x] 2.1 Reescrever `base.html`: classe `js` inline no `<head>`, preload da Geist, navegação de vidro fixa com ícones e pílulas, `aria-current="page"` pela seção (`request.blueprint`), barra inferior abaixo de 720 px com `padding-bottom` de segurança; verificar com testes de `aria-current` em `/`, `/musicas/nova`, `/playlists/1` e `/sorteios/<id>` (cenário "Seção atual") e a 360 px que a barra fica embaixo e não cobre o fim da página (cenário "Menu no celular")
- [x] 2.2 Fundo de palco (`body::before` com manchas radiais animadas por `transform`, `body::after` com ruído SVG a 3%), parado com `prefers-reduced-motion`; verificar a 360 px que não há rolagem horizontal e, emulando movimento reduzido no DevTools, que o fundo fica parado
- [x] 2.3 Toasts em `base.html` + `app.js` (sucesso some em 5 s, pausa com hover/foco; erro e aviso ficam até fechar; botão de fechar revelado pelo JS; `role="status"`/`role="alert"`); verificar com teste de que a mensagem e o `role` saem no HTML e, no navegador, os cenários "Confirmação some sozinha" e "Alerta fica até fechar"

## 3. Início e sorteio

- [x] 3.1 Redesenhar `inicio.html`: botão "Sortear" (gradiente animado, glow, pop), filtros de humor, dificuldade máxima e gênero em chips, artista e playlist em `select` de vidro, N como campo numérico, "Última sorteada" em cartão; atualizar os testes do MVP que conferiam `<option ... selected>` para os radios marcados (`checked`); verificar `python -m unittest` verde e que os filtros voltam marcados depois da mensagem da RN05
- [x] 3.2 Estado vazio na tela inicial (ícone grande, "Cadastre sua primeira música", CTA no gradiente para `/musicas/nova`) quando não há nenhuma música; verificar com testes dos cenários "Primeiro acesso" e "Só músicas inativas"

## 4. Resultado do sorteio

- [x] 4.1 Redesenhar `sorteio/resultado.html`: cartão central com capa grande, título em Instrument Serif, artista, link, "Toquei ✅" e "Pular ⏭️"; manter os campos ocultos do Pular; verificar com o teste "Tela de resultado" atualizado (sem o botão "Avaliar" antes de tocar)
- [x] 4.2 Estrelas: renderizar as 5 só quando `tocada = 1`, `aria-pressed` na nota atual, hover/foco acendendo em sequência e pop escalonado (D3); atualizar os testes de avaliação; verificar com testes "Avaliar música tocada (RN07)", "Estrelas escondidas antes de tocar", "Avaliar sem ter tocado (RN07)" e "Nota fora da faixa", e pelo teclado no navegador (cenário "Avaliar pelo teclado")
- [x] 4.3 Revelação estilo roleta (D4): `session["revelar"]` em `POST /sortear`, `data-roleta` com até 12 títulos só na primeira visualização, animação de ~1,2 s em `app.js`, rede de segurança CSS de 2 s e nada com movimento reduzido; verificar com testes de que `data-roleta` aparece só na primeira visualização (cenários "Revelação depois de sortear" e "Recarregar não repete"), com JS desativado que o resultado aparece (cenário "Navegador sem JavaScript") e, emulando movimento reduzido, que aparece direto (cenário "Resultado sem roleta")

## 5. Repertório

- [x] 5.1 Rotas `POST /musicas/<id>/favorita` e `POST /musicas/<id>/ativa` com `valor` 0/1 explícito, 404 para id inexistente, 400 para valor inválido e redirect para a lista com `request.args` + `#musica-<id>` (D2); verificar com testes "Marcar favorita", "Desativar", "Clique repetido" e "Música inexistente"
- [x] 5.2 Redesenhar `musicas/lista.html` em grade de cartões (capa gerada, título, artista, chips de gênero/humor, barrinhas de dificuldade com `aria-label`, coração `aria-pressed`, interruptor `role="switch"`, editar/excluir), busca e filtros em chips; atualizar os testes de listagem; verificar com os testes do MVP de busca e filtros verdes
- [x] 5.3 `app.js`: atalhos via `fetch` trocando o estado no lugar, com micro-animação e envio normal como fallback; verificar no navegador que favoritar não recarrega a página e, com JS desativado, que volta com os mesmos filtros e na mesma posição

## 6. Formulários

- [x] 6.1 `validar_musica()` e `_validar()` de artistas devolvendo erros por campo (`dict`), incluindo RN02 em `titulo`, artista inexistente em `artista_id` e nome repetido em `nome`; atualizar `tests/test_musicas.py` e `tests/test_artistas.py`; verificar a suíte verde
- [x] 6.2 Redesenhar `musicas/form.html` e `artistas/form.html` com o macro `campo()` (humor em chips, dificuldade segmentada 1–5, erros abaixo do campo com `aria-invalid`); verificar com teste do cenário "Título vazio" (mensagem logo após o campo Título, `aria-invalid="true"`, dificuldade preservada)

## 7. Artistas e playlists

- [x] 7.1 Redesenhar `artistas/lista.html` (cartões com capa gerada, contagem em Geist Mono, excluir como botão de perigo, estado vazio ilustrado); verificar com os testes de artistas verdes
- [x] 7.2 Redesenhar `playlists/lista.html` e `playlists/detalhe.html`; criar e editar inválidos renderizam a própria tela com erro no campo em vez de redirecionar (D5); verificar com testes de nome vazio na criação e na edição (erro junto ao campo, nada gravado) e os demais testes de playlists verdes

## 8. Histórico e estatísticas

- [ ] 8.1 Criar `estatisticas.py` com `calcular(db)` (resumo, top 5, nunca sorteadas, médias, gêneros agrupados em Python, D1); verificar com `tests/test_estatisticas.py` cobrindo todos os cenários da spec `estatisticas` (empate no top 5, só ativas nas nunca sorteadas, "4,7" no resumo, ordem das médias, "rock 4" com grafias misturadas, estados vazios)
- [ ] 8.2 Redesenhar `historico.html` com as estatísticas no topo (4 cartões de métrica, ranking com barras no gradiente, nunca sorteadas e médias com "Ver todas (N)" acima de 10, gêneros em barras) e a lista de sorteios abaixo; atualizar os testes de histórico; verificar com testes de que as mensagens de estado vazio aparecem sem sorteios e que a página responde 200 com o seed carregado

## 9. Conferência visual, documentação e integração

- [ ] 9.1 Conferência a 360 px e em 1440 px de largura, com o seed carregado e alguns sorteios tocados e avaliados: sem rolagem horizontal em nenhuma tela (cenário "Telas a 360 px"), foco visível percorrendo cada tela com Tab, emulação de movimento reduzido; salvar screenshots em `docs/screenshots/` (início, resultado, repertório, formulário, histórico com estatísticas; celular e desktop) e verificar que os 10 arquivos existem
- [ ] 9.2 Verificar o funcionamento sem internet: desligar a rede (ou bloquear requisições externas no DevTools), recarregar todas as telas e conferir no painel Rede que nenhuma requisição sai de `localhost` e que as fontes aparecem (cenário "Apresentação offline")
- [ ] 9.3 Atualizar o README (seção de estatísticas, créditos de fontes OFL e ícones Lucide ISC, screenshots); verificar seguindo o README do zero numa cópia limpa
- [ ] 9.4 Integração final: `python -m unittest`, `openspec validate add-estatisticas-e-visual --strict` e `openspec validate --specs --strict` sem erros, e o fluxo de ponta a ponta no navegador (sortear com chips, revelação, Toquei, 4 estrelas, favoritar pelo atalho, conferir estatísticas)

## Workflow follow-up

- Revisão do trio sobre as telas e as estatísticas em relação às specs.
- Arquivar a mudança com `openspec archive add-estatisticas-e-visual` (cria `openspec/specs/estatisticas` e `openspec/specs/interface`, move "Interface responsiva" de `sorteio` para `interface`) e conferir `openspec validate --specs --strict`.
