# Tasks: add-player-embutido

Referências: comportamento na delta `specs/sorteio/spec.md`, decisões em `design.md` (D1–D5). Testes com `python -m unittest` a partir da raiz. Ao fim de cada grupo a suíte inteira DEVE estar verde e o grupo é commitado como `feat(player): grupo N - <nome>`.

## 1. Extração do ID no servidor

- [x] 1.1 Commitar os artefatos desta mudança antes de qualquer código (`docs: specs add-player-embutido`); verificar com `git log -1 --stat` que só arquivos de `openspec/changes/add-player-embutido/` entraram
- [ ] 1.2 Escrever primeiro os testes unitários de `player()` em `tests/test_sorteio.py` com os casos aceitos e recusados de D5; verificar que falham por `player` não existir
- [ ] 1.3 Implementar `player(link)` em `sorteio.py` conforme D1 (esquema, host por igualdade numa lista fechada, caminho, `re.fullmatch` do ID, `src` montado só com constantes + ID); verificar que os testes de 1.2 passam e que a suíte inteira continua verde; commitar o grupo

## 2. Player na tela de resultado

- [ ] 2.1 Na rota `resultado()`, passar `player` ao template; em `sorteio/resultado.html`, quando houver player, acrescentar o botão "Ouvir aqui" (`type="button"`, `hidden`, ícone de fone) ao lado do "Abrir link", o bloco `.player` vazio e o `<template>` com o iframe de D3; verificar com testes da tela: com link de vídeo, `src` só dentro do `<template>` e "Abrir link" presente (cenários "Vídeo do YouTube" e "Faixa do Spotify"); com o link do seed, sem `<template>` nem "Ouvir aqui" (cenário "Link sem player"); com os links maliciosos dos cenários "Domínio parecido" e "ID com caracteres inválidos", sem "Ouvir aqui" e sem trecho do link em `src=`
- [ ] 2.2 Acrescentar o ícone `fone` (Lucide `headphones`) em `_icones.html` e à lista `ICONES` de `tests/test_design.py`; verificar com `test_todos_os_icones`
- [ ] 2.3 Em `app.js`, função `iniciarPlayer()`: revelar o botão, clonar o `<template>` para o bloco `.player` no clique, esconder o botão e focar o iframe; verificar no navegador que abrir o resultado não gera nenhuma requisição a YouTube ou Spotify no painel Rede (cenário "Abrir o resultado") e que o clique carrega o player; sem JS, só "Abrir link" aparece
- [ ] 2.4 CSS do bloco `.player` conforme D4 (borda de tinta 2 px, raio 0, 16:9 no YouTube, 152 px no Spotify); verificar que o teste anti-slop continua passando e conferir a 360 px e a 1440 px sem rolagem horizontal, com um link de vídeo e um de faixa colocados numa música de teste do banco de conferência (não no seed)
- [ ] 2.5 Conferir o cenário "Sem internet" com a rede desligada (a tela abre completa, com "Ouvir aqui" e "Abrir link") e o foco visível no botão e no iframe pelo teclado; suíte verde; commitar o grupo

## 3. Documentação e integração

- [ ] 3.1 Atualizar o README: o resultado toca vídeos do YouTube (inclusive YouTube Music) e faixas do Spotify ali mesmo, sob demanda; demais links abrem em nova aba; e, numa seção de apresentação/limitações, que para ver o player é preciso editar uma música e colar um link real de vídeo ou faixa (o seed só tem buscas); verificar que o texto confere com o comportamento
- [ ] 3.2 Rodar a suíte, `openspec validate add-player-embutido --strict` e `openspec validate --all --strict`; verificar que tudo passa e que `git grep -n "youtube-nocookie\|embed/track" -- seed.py` não acha nada (seed sem IDs inventados); commitar o grupo

## Workflow follow-up

- Arquivar com `/opsx:archive add-player-embutido` depois da revisão do trio, sincronizando a spec de `sorteio`.
