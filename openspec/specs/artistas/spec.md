# artistas Specification

## Purpose

Manter o cadastro dos artistas do repertório (CRUD completo), que é obrigatório para cadastrar músicas.

## Requirements

### Requirement: Cadastrar artista
O sistema DEVE (MUST) permitir cadastrar um artista com nome (obrigatório) e país (opcional). Espaços no início e no fim do nome DEVEM (MUST) ser descartados.

#### Scenario: Cadastro válido
- **GIVEN** não existe artista chamado "Legião Urbana"
- **WHEN** o usuário cadastra o artista "Legião Urbana" com país "Brasil"
- **THEN** o artista aparece na lista de artistas
- **AND** o sistema exibe a mensagem "Artista cadastrado."

#### Scenario: Nome vazio
- **GIVEN** o formulário de artista
- **WHEN** o usuário envia o formulário com o nome vazio ou só com espaços
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar o artista
- **AND** exibe "Informe o nome do artista." mantendo os dados digitados

### Requirement: Nome de artista único
O sistema NÃO DEVE (MUST NOT) permitir dois artistas com o mesmo nome, sem diferenciar maiúsculas de minúsculas.

#### Scenario: Nome repetido
- **GIVEN** existe o artista "Legião Urbana"
- **WHEN** o usuário cadastra ou edita outro artista com o nome "legião urbana"
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a alteração
- **AND** exibe "Já existe um artista com esse nome."

### Requirement: Listar artistas
O sistema DEVE (MUST) listar os artistas em ordem alfabética, mostrando nome, país e a quantidade de músicas de cada um.

#### Scenario: Lista com contagem
- **GIVEN** o artista "Legião Urbana" tem 2 músicas e "Djavan" tem 1
- **WHEN** o usuário abre a tela de artistas
- **THEN** a lista mostra "Djavan" antes de "Legião Urbana"
- **AND** mostra 1 música para "Djavan" e 2 para "Legião Urbana"

#### Scenario: Nenhum artista
- **GIVEN** não há artistas cadastrados
- **WHEN** o usuário abre a tela de artistas
- **THEN** o sistema exibe "Nenhum artista cadastrado ainda." e o botão para cadastrar

### Requirement: Editar artista
O sistema DEVE (MUST) permitir editar o nome e o país de um artista, aplicando as mesmas validações do cadastro.

#### Scenario: Edição válida
- **GIVEN** existe o artista "Legiao Urbana"
- **WHEN** o usuário altera o nome para "Legião Urbana"
- **THEN** o novo nome aparece na lista de artistas e nas músicas desse artista

### Requirement: Excluir artista
O sistema DEVE (MUST) excluir um artista sem músicas após confirmação do usuário. O sistema NÃO DEVE (MUST NOT) excluir um artista que ainda tem músicas.

#### Scenario: Artista sem músicas
- **GIVEN** o artista "Djavan" não tem músicas
- **WHEN** o usuário clica em excluir e confirma
- **THEN** o artista some da lista

#### Scenario: Artista com músicas
- **GIVEN** o artista "Legião Urbana" tem 2 músicas
- **WHEN** o usuário tenta excluí-lo
- **THEN** o sistema NÃO DEVE (MUST NOT) excluir o artista nem as músicas
- **AND** exibe "Este artista tem 2 música(s). Exclua as músicas antes de excluir o artista."

#### Scenario: Confirmação cancelada
- **GIVEN** o artista "Djavan" não tem músicas
- **WHEN** o usuário clica em excluir e cancela a confirmação
- **THEN** o artista continua cadastrado
