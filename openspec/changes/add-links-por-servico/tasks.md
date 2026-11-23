# Tasks: add-links-por-servico

Referências: comportamento nas deltas `specs/musicas/spec.md` e `specs/sorteio/spec.md`, decisões em `design.md` (D1–D7). Testes com `python -m unittest` a partir da raiz. Ao fim de cada grupo a suíte inteira DEVE estar verde e o grupo é commitado como `feat(links): grupo N - <nome>`.

## 1. Extração por serviço (`links.py`)

- [x] 1.1 Commitar os artefatos desta mudança antes de qualquer código (`docs: specs add-links-por-servico`); verificar com `git log -1 --stat` que só arquivos de `openspec/changes/add-links-por-servico/` entraram
- [x] 1.2 Escrever os testes de `youtube_id`, `spotify_id` e `players()` (D7) em `tests/test_links.py`, levando para lá os casos de `TestPlayer`; verificar que falham por `shuffle_meu.links` não existir
- [x] 1.3 Criar `shuffle_meu/links.py` (D1) e fazer `sorteio.py` usá-lo no lugar de `player()`; verificar que os testes de 1.2 passam e que a suíte inteira continua verde (inclusive `test_atributos_do_iframe`); commitar o grupo

## 2. Banco

- [x] 2.1 Acrescentar `youtube` e `spotify` ao `CREATE TABLE musica` em `schema.sql` e o acréscimo idempotente em `db.init_db()` (D2); verificar com testes: banco novo tem as colunas; banco criado com o schema antigo, com uma música, recebe as colunas vazias sem perder a música (cenário "Banco criado antes dos campos novos"); a segunda inicialização não falha; `CHECK` recusa `javascript:` nas colunas novas
- [x] 2.2 Registrar no README (seção "Zerar o banco") que bancos antigos recebem as colunas sozinhos e que recriar pelo seed também vale; suíte verde; commitar o grupo

## 3. Formulário de música

- [x] 3.1 `validar_musica()`, `INSERT` e `UPDATE` com `youtube`, `spotify` e `link` e as mensagens de D3; verificar com os testes dos cenários "Os três links", "Busca no campo YouTube", "Álbum no campo Spotify" e "Link do serviço trocado" (erro no campo certo, dados preservados, nada gravado), e com os testes atuais de "Link seguro" no outro link
- [x] 3.2 `musicas/form.html` com os três campos via `campo()` (D3); verificar no navegador a 360 px e a 1440 px, com e sem erro, e que editar uma música mostra os três links gravados; suíte verde; commitar o grupo

## 4. Resultado do sorteio

- [ ] 4.1 Rota e `sorteio/resultado.html` com os botões por link e um `<template>` por player (D4); verificar com testes: 0, 1 e 2 players (rótulos "Ouvir aqui" / "Ouvir no YouTube" / "Ouvir no Spotify"), botões "Abrir no YouTube", "Abrir no Spotify" e "Abrir link" só para campos preenchidos, nenhum iframe fora de `<template>`, cenários "Vídeo no outro link" e "ID com caracteres inválidos" (valor gravado direto no banco), e `test_atributos_do_iframe` para os dois serviços
- [ ] 4.2 `app.js` (`iniciarPlayer` com troca de player) e CSS; verificar no Chrome via DevTools Protocol com uma música de teste do banco de conferência que tenha os dois links: abrir o resultado gera zero requisições a YouTube ou Spotify; "Ouvir no Spotify" carrega o Spotify; "Ouvir no YouTube" depois troca pelo YouTube e o botão do Spotify volta; foco no player; a 360 px sem rolagem horizontal; suíte verde; commitar o grupo

## 5. Seed com links verificados

- [ ] 5.1 Criar `tools/verificar_links.py` (D8) e a seção "Comandos úteis" do README com o uso; verificar rodando-o com um vídeo que incorpora (`https://youtu.be/jNQXAC9IVRw`), um que bloqueia (`https://youtu.be/dQw4w9WgXcQ`) e a faixa `https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC`, esperando OK, FALHA e OK, e conferindo que nenhum teste em `tests/` o importa
- [ ] 5.2 Levantar, para cada uma das 25 músicas do seed, os candidatos de D6 por pesquisa na web, na ordem oficial → outro vídeo do canal oficial (ao vivo, acústico, lyric) → ao vivo/acústico de canal confiável, e a faixa no Spotify, anotando a página de origem de cada candidato; verificar que nenhum ID foi escrito sem ter vindo de uma página encontrada
- [ ] 5.3 Verificar cada candidato com `tools/verificar_links.py`: YouTube passa só com título e canal esperados no texto do iframe e sem mensagem de erro; Spotify só com título e artista; quando falhar, passar ao próximo candidato da ordem de D6
- [ ] 5.4 Escrever `docs/links-verificados.md` (música, artista, link do YouTube, canal, tipo de vídeo, incorpora?, motivo quando vazio, link do Spotify, data) com o resultado de 5.3, sem nenhuma linha "sim" que não tenha passado na verificação
- [ ] 5.5 `seed.py` com `LINKS` e o preenchimento de bancos existentes (D5); verificar com testes: links do seed válidos e presentes como "sim" no `docs/links-verificados.md`; música sem `youtube` com a busca no `link`; segunda execução idempotente; link colado pelo usuário não é sobrescrito; `link` só é limpo quando ainda é a busca gerada pelo seed
- [ ] 5.6 Rodar `python seed.py` num banco novo e num banco antigo de conferência e abrir no Chrome o resultado de uma música com YouTube e de uma com Spotify, confirmando o player tocando sem erro; suíte verde; commitar o grupo

## 6. Documentação e integração

- [ ] 6.1 Atualizar o README: três campos de link; botões por link e escolha de player no resultado; o seed já traz links verificados (com link para `docs/links-verificados.md`); remover das limitações a orientação de colar link real para demonstrar, deixando a observação sobre vídeos que bloqueiam incorporação
- [ ] 6.2 Regenerar os screenshots do resultado (`resultado-celular.webp`, `resultado-desktop.webp`) com uma música do seed que tenha os dois links; verificar abrindo os arquivos
- [ ] 6.3 Rodar a suíte, `openspec validate add-links-por-servico --strict` e `openspec validate --all --strict`; verificar que tudo passa e que nenhum servidor ficou rodando; commitar o grupo

## Workflow follow-up

- Arquivar com `/opsx:archive add-links-por-servico` depois da revisão do trio, sincronizando as specs de `musicas` e `sorteio`.
