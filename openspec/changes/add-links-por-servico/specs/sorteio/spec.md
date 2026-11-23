# Spec Delta: sorteio

## MODIFIED Requirements

### Requirement: Player embutido no resultado
A tela de resultado DEVE (MUST) mostrar um botão para cada link preenchido: "Abrir no YouTube", "Abrir no Spotify" e "Abrir link". Com link do YouTube ou do Spotify, DEVE (MUST) oferecer "Ouvir aqui", que embute o player oficial na tela usando o YouTube se houver, senão o Spotify; com os dois, DEVE (MUST) oferecer "Ouvir no YouTube" e "Ouvir no Spotify". Os botões de abrir DEVEM (MUST) continuar disponíveis com ou sem player.

#### Scenario: Vídeo do YouTube
- **GIVEN** a música sorteada tem o link do YouTube "https://www.youtube.com/watch?v=jNQXAC9IVRw" e nenhum outro
- **WHEN** o usuário abre o resultado e clica em "Ouvir aqui"
- **THEN** o player do YouTube aparece na tela, dentro de um bloco com borda de tinta, e o vídeo começa a tocar
- **AND** o botão "Abrir no YouTube" continua visível

#### Scenario: Faixa do Spotify
- **GIVEN** a música sorteada tem o link do Spotify "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC" e nenhum outro
- **WHEN** o usuário abre o resultado e clica em "Ouvir aqui"
- **THEN** o player do Spotify aparece na tela
- **AND** o botão "Abrir no Spotify" continua visível

#### Scenario: Faixa do Spotify com idioma no link
- **GIVEN** a música sorteada tem o link do Spotify "https://open.spotify.com/intl-pt/track/4uLU6hMCjMI75M1A2tKUQC?si=abc"
- **WHEN** o usuário abre o resultado e clica em "Ouvir aqui"
- **THEN** o player do Spotify aparece na tela, com a mesma faixa do link sem idioma

#### Scenario: Link do YouTube Music
- **GIVEN** a música sorteada tem o link do YouTube "https://music.youtube.com/watch?v=jNQXAC9IVRw"
- **WHEN** o usuário abre o resultado e clica em "Ouvir aqui"
- **THEN** o player do YouTube aparece na tela com o mesmo vídeo

#### Scenario: Link sem player
- **GIVEN** a música sorteada só tem o outro link, com uma busca do YouTube ou uma cifra
- **WHEN** o usuário abre o resultado
- **THEN** a tela mostra só o botão "Abrir link", sem nenhum botão de ouvir

#### Scenario: YouTube e Spotify
- **GIVEN** a música sorteada tem link do YouTube, link do Spotify e outro link
- **WHEN** o usuário abre o resultado
- **THEN** a tela mostra "Ouvir no YouTube", "Ouvir no Spotify", "Abrir no YouTube", "Abrir no Spotify" e "Abrir link"
- **AND** ao clicar em "Ouvir no Spotify" aparece o player do Spotify, e ao clicar depois em "Ouvir no YouTube" o player do YouTube toma o lugar dele

### Requirement: Player só carrega quando pedido
Abrir a tela de resultado NÃO DEVE (MUST NOT) carregar nenhum conteúdo de YouTube ou Spotify. O player só DEVE (MUST) ser carregado depois que o usuário clicar em um botão de ouvir ("Ouvir aqui", "Ouvir no YouTube" ou "Ouvir no Spotify"), para a tela abrir sem internet e sem rastreamento de terceiros.

#### Scenario: Abrir o resultado
- **GIVEN** a música sorteada tem link do YouTube e link do Spotify
- **WHEN** o usuário abre a tela de resultado e não clica em nenhum botão de ouvir
- **THEN** o navegador não faz nenhuma requisição a YouTube ou Spotify

#### Scenario: Sem internet
- **GIVEN** o computador está sem internet e a música sorteada tem um link de faixa do Spotify
- **WHEN** o usuário abre a tela de resultado
- **THEN** a tela aparece completa, com os botões "Ouvir aqui" e "Abrir no Spotify"

### Requirement: Validação estrita do link do player
O sistema DEVE (MUST) extrair o ID do vídeo ou da faixa no servidor, a partir só dos campos YouTube e Spotify, aceitando os domínios e caminhos listados e IDs com os caracteres válidos de cada serviço (11 de letras, números, "-" e "_" no YouTube; 22 letras e números no Spotify), também ao exibir links gravados antes da validação. O endereço do player DEVE (MUST) ser montado a partir do ID, nunca com a URL gravada.

#### Scenario: Domínio parecido
- **GIVEN** a música tem no outro link "https://youtube.com.exemplo.net/watch?v=jNQXAC9IVRw"
- **WHEN** o usuário abre o resultado
- **THEN** a tela não oferece nenhum botão de ouvir
- **AND** mostra só o "Abrir link"

#### Scenario: ID com caracteres inválidos
- **GIVEN** o campo YouTube da música foi gravado direto no banco com "https://youtu.be/abc\"onload=x"
- **WHEN** o usuário abre o resultado
- **THEN** a tela não oferece "Ouvir aqui"
- **AND** nenhum trecho do link aparece dentro do endereço de um player

#### Scenario: Vídeo no outro link
- **GIVEN** a música só tem no outro link o vídeo "https://www.youtube.com/watch?v=jNQXAC9IVRw"
- **WHEN** o usuário abre o resultado
- **THEN** a tela mostra só o "Abrir link", sem botão de ouvir, porque o player usa só os campos YouTube e Spotify
