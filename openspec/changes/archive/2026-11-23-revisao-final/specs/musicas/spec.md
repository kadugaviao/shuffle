# Spec Delta: musicas

## MODIFIED Requirements

### Requirement: Listar repertório com busca e filtros
O sistema DEVE (MUST) listar as músicas em ordem alfabética de título, mostrando título, artista, gênero, humor, dificuldade, favorita e ativa. A busca DEVE (MUST) achar trechos do título ou do nome do artista sem diferenciar maiúsculas de minúsculas. Os filtros DEVEM (MUST) ser gênero, humor e só favoritas, combinados entre si.

#### Scenario: Busca por artista
- **GIVEN** existem "Tempo Perdido" e "Índios" de "Legião Urbana" e "Oceano" de "Djavan"
- **WHEN** o usuário busca "legião"
- **THEN** a lista mostra só "Índios" e "Tempo Perdido"

#### Scenario: Filtros combinados
- **GIVEN** "Tempo Perdido" é rock e favorita, e "Índios" é rock e não favorita
- **WHEN** o usuário filtra gênero "rock" e marca "só favoritas"
- **THEN** a lista mostra só "Tempo Perdido"

#### Scenario: Nada encontrado
- **GIVEN** nenhuma música corresponde à busca "xyz"
- **WHEN** o usuário busca "xyz"
- **THEN** o sistema exibe "Nenhuma música encontrada." em vez de uma lista vazia

#### Scenario: Repertório vazio
- **GIVEN** não há nenhuma música cadastrada
- **WHEN** o usuário abre o Repertório sem busca nem filtros
- **THEN** o sistema exibe "Caderno em branco" e o botão "Nova música"
- **AND** não mostra a busca nem os filtros
