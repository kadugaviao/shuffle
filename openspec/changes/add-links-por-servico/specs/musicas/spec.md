# Spec Delta: musicas

## ADDED Requirements

### Requirement: Links do YouTube e do Spotify
Os campos YouTube e Spotify DEVEM (MUST) ser opcionais. Quando informado, o campo YouTube só DEVE (MUST) aceitar link de vídeo (youtube.com/watch?v=, music.youtube.com/watch?v=, youtu.be/, youtube.com/shorts/) e o campo Spotify só link de faixa (open.spotify.com/track/ ou open.spotify.com/intl-xx/track/), com as mesmas regras estritas de domínio e de ID do player. O erro DEVE (MUST) aparecer junto ao campo, preservando os dados digitados.

#### Scenario: Os três links
- **GIVEN** o formulário de música
- **WHEN** o usuário informa o YouTube "https://youtu.be/jNQXAC9IVRw", o Spotify "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC" e o outro link "https://www.cifraclub.com.br/legiao-urbana/tempo-perdido/"
- **THEN** a música é gravada com os três links

#### Scenario: Busca no campo YouTube
- **GIVEN** o formulário de música
- **WHEN** o usuário informa no campo YouTube "https://www.youtube.com/results?search_query=tempo+perdido"
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe junto ao campo YouTube "Cole o link de um vídeo do YouTube (youtube.com/watch?v=… ou youtu.be/…)."
- **AND** os demais campos continuam com o que foi digitado

#### Scenario: Álbum no campo Spotify
- **GIVEN** o formulário de música
- **WHEN** o usuário informa no campo Spotify "https://open.spotify.com/album/4uLU6hMCjMI75M1A2tKUQC"
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe junto ao campo Spotify "Cole o link de uma faixa do Spotify (open.spotify.com/track/…)."

#### Scenario: Link do serviço trocado
- **GIVEN** o formulário de música
- **WHEN** o usuário cola um link de faixa do Spotify no campo YouTube
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música e exibe o erro junto ao campo YouTube

#### Scenario: Banco criado antes dos campos novos
- **GIVEN** um banco criado por uma versão anterior, sem as colunas de YouTube e Spotify, com músicas cadastradas
- **WHEN** o sistema é iniciado
- **THEN** as colunas passam a existir vazias e nenhuma música é perdida

## MODIFIED Requirements

### Requirement: Cadastrar música (RN01)
O sistema DEVE (MUST) permitir cadastrar uma música com título e artista obrigatórios (RN01) e gênero, humor, dificuldade, link do YouTube, link do Spotify e outro link. Toda música nova DEVE (MUST) começar com favorita = falso e ativa = verdadeiro. Espaços no início e no fim do título DEVEM (MUST) ser descartados.

#### Scenario: Cadastro válido
- **GIVEN** existe o artista "Legião Urbana"
- **WHEN** o usuário cadastra "Tempo Perdido" de "Legião Urbana", gênero "rock", humor "calma", dificuldade 2
- **THEN** a música aparece no repertório como ativa e não favorita
- **AND** o sistema exibe "Música cadastrada."

#### Scenario: Título vazio (RN01)
- **GIVEN** o formulário de música
- **WHEN** o usuário envia o formulário com o título vazio ou só com espaços
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe "Informe o título da música." mantendo os dados digitados

#### Scenario: Sem artista (RN01)
- **GIVEN** o formulário de música
- **WHEN** o usuário envia o formulário sem escolher um artista
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe "Escolha o artista da música."

### Requirement: Link seguro
O outro link (cifra, letra, busca) DEVE (MUST) ser opcional e, quando informado, começar com "http://" ou "https://". O sistema NÃO DEVE (MUST NOT) aceitar outros esquemas de link.

#### Scenario: Link válido
- **GIVEN** o formulário de música
- **WHEN** o usuário informa no outro link "https://www.cifraclub.com.br/legiao-urbana/tempo-perdido/"
- **THEN** a música é gravada e o link aparece clicável no resultado, abrindo em nova aba

#### Scenario: Esquema proibido
- **GIVEN** o formulário de música
- **WHEN** o usuário informa no outro link "javascript:alert(1)"
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe "O link deve começar com http:// ou https://."
