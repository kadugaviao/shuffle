# Spec Delta: sorteio

## ADDED Requirements

### Requirement: Player embutido no resultado
Quando o link da música sorteada for de um vídeo do YouTube (youtube.com/watch?v=, music.youtube.com/watch?v=, youtu.be/, youtube.com/shorts/) ou de uma faixa do Spotify (open.spotify.com/track/ ou open.spotify.com/intl-xx/track/), a tela de resultado DEVE (MUST) oferecer o botão "Ouvir aqui", que embute o player oficial na própria tela. O botão "Abrir link" DEVE (MUST) continuar disponível, com ou sem player.

#### Scenario: Vídeo do YouTube
- **GIVEN** a música sorteada tem o link "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
- **WHEN** o usuário abre o resultado e clica em "Ouvir aqui"
- **THEN** o player do YouTube aparece na tela, dentro de um bloco com borda de tinta, e o vídeo começa a tocar
- **AND** o botão "Abrir link" continua visível

#### Scenario: Faixa do Spotify
- **GIVEN** a música sorteada tem o link "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
- **WHEN** o usuário abre o resultado e clica em "Ouvir aqui"
- **THEN** o player do Spotify aparece na tela

#### Scenario: Faixa do Spotify com idioma no link
- **GIVEN** a música sorteada tem o link "https://open.spotify.com/intl-pt/track/4uLU6hMCjMI75M1A2tKUQC?si=abc"
- **WHEN** o usuário abre o resultado e clica em "Ouvir aqui"
- **THEN** o player do Spotify aparece na tela, com a mesma faixa do link sem idioma

#### Scenario: Link do YouTube Music
- **GIVEN** a música sorteada tem o link "https://music.youtube.com/watch?v=dQw4w9WgXcQ"
- **WHEN** o usuário abre o resultado e clica em "Ouvir aqui"
- **THEN** o player do YouTube aparece na tela com o mesmo vídeo

#### Scenario: Link sem player
- **GIVEN** a música sorteada tem o link de uma busca do YouTube ou de uma cifra
- **WHEN** o usuário abre o resultado
- **THEN** a tela mostra só o botão "Abrir link", sem "Ouvir aqui"

### Requirement: Player só carrega quando pedido
Abrir a tela de resultado NÃO DEVE (MUST NOT) carregar nenhum conteúdo de YouTube ou Spotify. O player só DEVE (MUST) ser carregado depois que o usuário clicar em "Ouvir aqui", para a tela abrir sem internet e sem rastreamento de terceiros.

#### Scenario: Abrir o resultado
- **GIVEN** a música sorteada tem um link de vídeo do YouTube
- **WHEN** o usuário abre a tela de resultado e não clica em "Ouvir aqui"
- **THEN** o navegador não faz nenhuma requisição a YouTube ou Spotify

#### Scenario: Sem internet
- **GIVEN** o computador está sem internet e a música sorteada tem um link de faixa do Spotify
- **WHEN** o usuário abre a tela de resultado
- **THEN** a tela aparece completa, com o botão "Ouvir aqui" e o "Abrir link"

### Requirement: Validação estrita do link do player
O sistema DEVE (MUST) extrair o ID do vídeo ou da faixa no servidor, aceitando só os domínios e caminhos listados e IDs com os caracteres válidos de cada serviço (11 de letras, números, "-" e "_" no YouTube; 22 letras e números no Spotify). O endereço do player DEVE (MUST) ser montado pelo sistema a partir do ID, nunca com a URL digitada.

#### Scenario: Domínio parecido
- **GIVEN** a música tem o link "https://youtube.com.exemplo.net/watch?v=dQw4w9WgXcQ"
- **WHEN** o usuário abre o resultado
- **THEN** a tela não oferece "Ouvir aqui"
- **AND** mostra só o "Abrir link"

#### Scenario: ID com caracteres inválidos
- **GIVEN** a música tem o link "https://youtu.be/abc\"onload=x"
- **WHEN** o usuário abre o resultado
- **THEN** a tela não oferece "Ouvir aqui"
- **AND** nenhum trecho do link aparece dentro do endereço de um player
