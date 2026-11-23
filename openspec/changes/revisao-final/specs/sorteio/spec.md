# Spec Delta: sorteio

## MODIFIED Requirements

### Requirement: Sorteio com filtros
O sistema DEVE (MUST) permitir filtrar o sorteio por gênero, humor, dificuldade máxima, artista e playlist. Os filtros informados DEVEM (MUST) ser combinados entre si (todos precisam ser atendidos); filtro em branco NÃO DEVE (MUST NOT) restringir. O filtro por gênero NÃO DEVE (MUST NOT) diferenciar maiúsculas de minúsculas.

#### Scenario: Filtro por humor e dificuldade
- **GIVEN** "Oceano" é calma com dificuldade 4 e "Tempo Perdido" é calma com dificuldade 2
- **WHEN** o usuário sorteia com humor "calma" e dificuldade máxima 3
- **THEN** o resultado é "Tempo Perdido"

#### Scenario: Filtro por playlist
- **GIVEN** a playlist "Roda de violão" contém só "Tempo Perdido"
- **WHEN** o usuário sorteia com a playlist "Roda de violão"
- **THEN** o resultado é "Tempo Perdido"

#### Scenario: Filtro por artista
- **GIVEN** "Djavan" tem uma única música ativa, "Oceano"
- **WHEN** o usuário sorteia com o artista "Djavan"
- **THEN** o resultado é "Oceano"

#### Scenario: Filtro por gênero
- **GIVEN** "Tempo Perdido" tem gênero "rock" e "Oceano" tem gênero "MPB", ambas ativas
- **WHEN** o usuário sorteia com o gênero "ROCK"
- **THEN** o resultado é "Tempo Perdido"

### Requirement: Player embutido no resultado
A tela de resultado DEVE (MUST) mostrar um link para cada link preenchido: "Abrir no YouTube", "Abrir no Spotify" e "Abrir link". Com link do YouTube ou do Spotify, DEVE (MUST) oferecer "Ouvir aqui", que embute o player oficial na tela; com os dois, "Ouvir aqui" DEVE (MUST) vir com um seletor de duas opções, "YouTube" e "Spotify". O player aberto DEVE (MUST) poder ser fechado, e os links de abrir DEVEM (MUST) continuar disponíveis com ou sem player.

#### Scenario: Vídeo do YouTube
- **GIVEN** a música sorteada tem o link do YouTube "https://www.youtube.com/watch?v=jNQXAC9IVRw" e nenhum outro
- **WHEN** o usuário abre o resultado e clica em "Ouvir aqui"
- **THEN** o player do YouTube aparece na tela, dentro de um bloco com borda de tinta, e o vídeo começa a tocar
- **AND** o link "Abrir no YouTube" continua visível

#### Scenario: Faixa do Spotify
- **GIVEN** a música sorteada tem o link do Spotify "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC" e nenhum outro
- **WHEN** o usuário abre o resultado e clica em "Ouvir aqui"
- **THEN** o player do Spotify aparece na tela
- **AND** o link "Abrir no Spotify" continua visível

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
- **THEN** a tela mostra só o link "Abrir link", sem "Ouvir aqui"

#### Scenario: YouTube e Spotify
- **GIVEN** a música sorteada tem link do YouTube, link do Spotify e outro link
- **WHEN** o usuário abre o resultado
- **THEN** a tela mostra "Ouvir aqui" com as opções "YouTube" e "Spotify", nenhuma selecionada, e os links "Abrir no YouTube", "Abrir no Spotify" e "Abrir link"
- **AND** ao escolher "Spotify" aparece o player do Spotify, e ao escolher depois "YouTube" o player do YouTube toma o lugar dele

#### Scenario: Fechar o player
- **GIVEN** o player do YouTube está aberto no resultado
- **WHEN** o usuário clica em "Fechar player"
- **THEN** o player sai da tela e "Ouvir aqui" volta a ficar disponível

#### Scenario: Ações principais sempre à vista
- **GIVEN** um navegador com 360 px de largura e uma música sorteada com link do YouTube
- **WHEN** o usuário abre o player
- **THEN** os botões "Toquei" e "Pular" continuam acima do player, sem serem empurrados por ele

### Requirement: Player só carrega quando pedido
Abrir a tela de resultado NÃO DEVE (MUST NOT) carregar nenhum conteúdo de YouTube ou Spotify. O player só DEVE (MUST) ser carregado depois que o usuário clicar em "Ouvir aqui" ou escolher "YouTube" ou "Spotify" no seletor, para a tela abrir sem internet e sem rastreamento de terceiros.

#### Scenario: Abrir o resultado
- **GIVEN** a música sorteada tem link do YouTube e link do Spotify
- **WHEN** o usuário abre a tela de resultado e não escolhe nenhum serviço para ouvir
- **THEN** o navegador não faz nenhuma requisição a YouTube ou Spotify

#### Scenario: Sem internet
- **GIVEN** o computador está sem internet e a música sorteada tem um link de faixa do Spotify
- **WHEN** o usuário abre a tela de resultado
- **THEN** a tela aparece completa, com "Ouvir aqui" e o link "Abrir no Spotify"

### Requirement: Validação estrita do link do player
O sistema DEVE (MUST) extrair o ID do vídeo ou da faixa no servidor, a partir só dos campos YouTube e Spotify, aceitando os domínios e caminhos listados e IDs com os caracteres válidos de cada serviço (11 de letras, números, "-" e "_" no YouTube; 22 letras e números no Spotify), também ao exibir links gravados antes da validação. O endereço do player DEVE (MUST) ser montado a partir do ID, nunca com a URL gravada.

#### Scenario: Domínio parecido
- **GIVEN** a música tem no outro link "https://youtube.com.exemplo.net/watch?v=jNQXAC9IVRw"
- **WHEN** o usuário abre o resultado
- **THEN** a tela não oferece "Ouvir aqui"
- **AND** mostra só o link "Abrir link"

#### Scenario: ID com caracteres inválidos
- **GIVEN** o campo YouTube da música foi gravado direto no banco com "https://youtu.be/abc\"onload=x"
- **WHEN** o usuário abre o resultado
- **THEN** a tela não oferece "Ouvir aqui"
- **AND** nenhum trecho do link aparece dentro do endereço de um player

#### Scenario: Vídeo no outro link
- **GIVEN** a música só tem no outro link o vídeo "https://www.youtube.com/watch?v=jNQXAC9IVRw"
- **WHEN** o usuário abre o resultado
- **THEN** a tela mostra só o link "Abrir link", sem "Ouvir aqui", porque o player usa só os campos YouTube e Spotify
