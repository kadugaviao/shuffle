# Spec Delta: playlists

## MODIFIED Requirements

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
