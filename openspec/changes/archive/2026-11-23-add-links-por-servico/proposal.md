# Proposal: add-links-por-servico

## Why

Cada música tem um único campo `link`. Quem cadastra o link do Spotify perde o do YouTube e vice-versa, e a busca do YouTube que o seed grava não toca no player embutido (`add-player-embutido`). Com um campo por serviço, a mesma música pode ter vídeo, faixa e cifra, e a demonstração passa a mostrar o player com os dados de exemplo, sem precisar editar música na hora.

## What Changes

- **Banco:** a tabela `musica` ganha as colunas `youtube` e `spotify` (TEXT, opcionais). A coluna `link` continua e passa a ser o **"Outro link"** (cifra, letra, busca). Bancos já existentes recebem as colunas sozinhos na inicialização (acréscimo idempotente, sem perder dados); recriar o banco pelo seed continua valendo.
- **Validação no servidor:** o campo YouTube só aceita links de vídeo reconhecidos e o campo Spotify só aceita links de faixa, com as mesmas regras estritas do player. "Outro link" continua aceitando qualquer `http://` ou `https://`.
- **Formulário de música:** três campos (YouTube, Spotify, Outro link), cada um com o erro junto ao campo e os dados digitados preservados.
- **Resultado do sorteio:** um botão para cada campo preenchido: "Abrir no YouTube", "Abrir no Spotify" e "Abrir link". O player embutido usa o YouTube se houver, senão o Spotify ("Ouvir aqui"); com os dois, a tela oferece "Ouvir no YouTube" e "Ouvir no Spotify". Continuam valendo as regras do player: só carrega no clique, nada externo ao abrir a tela, visual Lambe-lambe.
- **Seed:** cada música recebe um link do YouTube **que permite incorporação** e um link de faixa do Spotify, todos **verificados de verdade no Chrome**. Ordem de busca no YouTube: vídeo oficial; se bloquear, outro vídeo do canal oficial do artista (ao vivo, acústico, lyric video); depois uma versão ao vivo ou acústica de canal confiável. Sem nenhum que incorpore, o `youtube` fica vazio e a busca continua no "Outro link". Nenhum ID é inventado. A verificação fica registrada em `docs/links-verificados.md`, com o tipo de vídeo, o motivo quando ficar sem YouTube e a data.
- **Músicas do seed trocadas** (pedido do trio durante a implementação): 18 músicas em 6 gêneros (rock, rock brasileiro, metal, samba, sertanejo e MPB), mais 2 calmas de bandas já presentes ("Nothing Else Matters", do Metallica, e "Patience", do Guns N' Roses, esta inativa) para o filtro de humor "calma" não ficar com uma música só. Continuam 2 playlists, com músicas da lista nova.
- **Ferramenta de verificação** versionada em `tools/verificar_links.py`, com instruções no README. Ela não roda na suíte de testes, porque precisa de internet e do Chrome.
- Specs (`musicas` e `sorteio`), testes e README atualizados.

**Continua igual:** regras de negócio RN01 a RN08, demais campos e telas, e o player em si (domínios, `<template>` inerte, atributos do iframe).

### Fora do escopo
Outros serviços (Deezer, SoundCloud, YouTube Music como campo próprio), álbuns e playlists do Spotify, player para o "Outro link", busca automática de links pelo app e normalização dos links gravados.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `musicas`: o cadastro passa a ter links de YouTube e Spotify validados por serviço, além do "Outro link"; o requisito "Link seguro" passa a valer para o "Outro link".
- `sorteio`: a tela de resultado mostra um botão por link preenchido e o player escolhe entre YouTube e Spotify a partir dos campos próprios.

## Impact

- Código: novo `shuffle_meu/links.py` (extração e validação de vídeo do YouTube e faixa do Spotify, saindo de `sorteio.py` para ser usado também por `musicas.py` sem import circular); `schema.sql` e `db.py` (colunas novas e acréscimo idempotente); `musicas.py` (validação e gravação dos campos); `templates/musicas/form.html`; `sorteio.py` e `templates/sorteio/resultado.html` (botões e players); `static/app.js` (escolher entre os players); `static/style.css`; `seed.py`.
- Banco: duas colunas novas em `musica`; nenhum dado existente é apagado.
- Testes: validação por serviço, acréscimo das colunas num banco antigo, formulário, tela de resultado com 0, 1 ou 2 players, seed (todo link do seed é válido e consta como verificado no `docs/links-verificados.md`).
- Ferramenta: `tools/verificar_links.py` (novo, só biblioteca padrão; pilota o Chrome pelo DevTools Protocol).
- Documentação: `docs/links-verificados.md` (novo), README (seção "Comandos úteis") e screenshots do resultado.
- Dependências: nenhuma. A busca dos links do seed usa pesquisa na web e o Chrome do ambiente, só durante a implementação.
