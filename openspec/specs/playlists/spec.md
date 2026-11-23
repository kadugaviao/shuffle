# playlists Specification

## Purpose

Agrupar músicas do repertório em playlists (ex.: "Roda de violão", "Churrasco") para organizar e filtrar o sorteio.

## Requirements

### Requirement: Criar playlist
O sistema DEVE (MUST) permitir criar uma playlist com nome obrigatório e descrição opcional.

#### Scenario: Criação válida
- **GIVEN** a tela de playlists
- **WHEN** o usuário cria a playlist "Roda de violão" com descrição "Fáceis de tocar"
- **THEN** a playlist aparece na lista com 0 músicas

#### Scenario: Nome vazio
- **GIVEN** a tela de playlists
- **WHEN** o usuário tenta criar uma playlist com nome vazio ou só com espaços
- **THEN** o sistema NÃO DEVE (MUST NOT) criar a playlist
- **AND** exibe "Informe o nome da playlist."

### Requirement: Listar playlists
O sistema DEVE (MUST) listar as playlists em ordem alfabética com nome, descrição e quantidade de músicas.

#### Scenario: Lista com contagem
- **GIVEN** "Churrasco" tem 4 músicas e "Roda de violão" tem 2
- **WHEN** o usuário abre a tela de playlists
- **THEN** a lista mostra "Churrasco" (4 músicas) antes de "Roda de violão" (2 músicas)

### Requirement: Editar playlist
O sistema DEVE (MUST) permitir renomear uma playlist e alterar sua descrição, com o nome continuando obrigatório.

#### Scenario: Renomear
- **GIVEN** existe a playlist "Churras"
- **WHEN** o usuário a renomeia para "Churrasco"
- **THEN** a lista mostra "Churrasco" com as mesmas músicas de antes

### Requirement: Excluir playlist
O sistema DEVE (MUST) excluir uma playlist após confirmação, removendo os vínculos dela. O sistema NÃO DEVE (MUST NOT) excluir as músicas que estavam na playlist.

#### Scenario: Exclusão mantém as músicas
- **GIVEN** a playlist "Churrasco" tem a música "Oceano"
- **WHEN** o usuário exclui a playlist e confirma
- **THEN** a playlist some da lista
- **AND** "Oceano" continua no repertório

### Requirement: Adicionar música à playlist
O sistema DEVE (MUST) permitir adicionar uma música do repertório a uma playlist. Uma música NÃO DEVE (MUST NOT) aparecer duas vezes na mesma playlist.

#### Scenario: Adicionar
- **GIVEN** a playlist "Roda de violão" sem músicas
- **WHEN** o usuário adiciona "Tempo Perdido"
- **THEN** a tela da playlist lista "Tempo Perdido"

#### Scenario: Adicionar repetida
- **GIVEN** "Tempo Perdido" já está em "Roda de violão"
- **WHEN** o usuário tenta adicioná-la de novo
- **THEN** a playlist continua com uma única ocorrência de "Tempo Perdido"
- **AND** o sistema exibe "Essa música já está na playlist."

#### Scenario: Mesma música em várias playlists
- **GIVEN** "Oceano" está em "Churrasco"
- **WHEN** o usuário adiciona "Oceano" a "Roda de violão"
- **THEN** "Oceano" aparece nas duas playlists

### Requirement: Remover música da playlist
O sistema DEVE (MUST) permitir remover uma música de uma playlist sem excluir a música do repertório. Pedir a remoção de uma música que não está na playlist NÃO DEVE (MUST NOT) confirmar uma remoção; o sistema DEVE (MUST) avisar que a música não está nela.

#### Scenario: Remover
- **GIVEN** "Tempo Perdido" está em "Roda de violão"
- **WHEN** o usuário a remove da playlist
- **THEN** a playlist não lista mais "Tempo Perdido"
- **AND** "Tempo Perdido" continua no repertório e em outras playlists

#### Scenario: Música que não está na playlist
- **GIVEN** "Oceano" não está em "Roda de violão"
- **WHEN** chega um pedido para remover "Oceano" de "Roda de violão"
- **THEN** o sistema exibe "Essa música não está na playlist." como erro
- **AND** não exibe "Música removida da playlist."
