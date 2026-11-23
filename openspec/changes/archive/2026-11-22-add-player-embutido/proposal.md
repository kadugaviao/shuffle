# Proposal: add-player-embutido

## Why

Depois do sorteio, a pessoa quase sempre quer ouvir a música para lembrar o tom ou a levada antes de tocar. Hoje a tela de resultado só oferece "Abrir link", que leva para outra aba e tira a pessoa do app no meio da roda. Quando o link é de um vídeo do YouTube ou de uma faixa do Spotify, dá para tocar ali mesmo, sem sair da tela.

## What Changes

- Na tela de resultado, quando o link da música for de um **vídeo do YouTube** (`youtube.com/watch?v=`, `music.youtube.com/watch?v=`, `youtu.be/`, `youtube.com/shorts/`) ou de uma **faixa do Spotify** (`open.spotify.com/track/` ou `open.spotify.com/intl-xx/track/`), aparece o botão **"Ouvir aqui"**. Ao clicar, o player oficial é embutido na própria tela e começa a tocar (`youtube-nocookie.com/embed/<ID>` ou `open.spotify.com/embed/track/<ID>`).
- **Nada externo carrega ao abrir a tela:** o player só é criado depois do clique. A página continua abrindo sem internet e sem rastreamento de terceiros.
- **"Abrir link" continua sempre**, também quando há player, porque muitos vídeos oficiais bloqueiam a incorporação.
- **O ID é extraído e validado no servidor** (domínio, caminho e caracteres permitidos). O endereço do player é montado pelo sistema a partir do ID, nunca com a URL que o usuário digitou.
- Qualquer outro link (busca do YouTube, cifra, álbum ou playlist do Spotify, domínios parecidos) continua só com "Abrir link".
- Player num bloco com borda de tinta e raio 0, seguindo o design system "Lambe-lambe" e a seção Anti-slop.

**Continua igual:** schema, regras de negócio RN01 a RN08, validação do link no cadastro ("Link seguro"), seed (os links de exemplo continuam sendo buscas do YouTube, então não mostram player) e o funcionamento sem JavaScript, em que fica só o "Abrir link".

### Fora do escopo
Player para outros serviços (Deezer, SoundCloud, álbuns e playlists do Spotify), tocar sem clique, guardar posição do vídeo, mudar o formulário de música e inventar links de vídeo no seed.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `sorteio`: a tela de resultado ganha o player embutido sob demanda para vídeos do YouTube e faixas do Spotify, com validação estrita do link e "Abrir link" sempre disponível.

## Impact

- Código: `sorteio.py` (função pura que extrai o tipo e o ID do link; a rota de resultado passa o player ao template), `templates/sorteio/resultado.html` (botão "Ouvir aqui" e o player num `<template>` inerte), `static/app.js` (insere o player ao clicar), `static/style.css` (bloco do player), `templates/_icones.html` (ícone de fone).
- Banco: nenhuma mudança.
- Testes: testes unitários da extração (links válidos, inválidos e maliciosos) e testes da tela de resultado (botão só quando há player, nenhum iframe fora do `<template>`, "Abrir link" sempre presente).
- Documentação: README (o resultado pode tocar a música ali mesmo; para ver o player na apresentação é preciso editar uma música e colar um link real de vídeo ou faixa, porque o seed só tem buscas).
- Dependências: nenhuma; só `urllib.parse` e `re` da biblioteca padrão.
