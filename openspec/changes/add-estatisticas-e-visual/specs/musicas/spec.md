# Spec Delta: musicas

## ADDED Requirements

### Requirement: Atalhos de favorita e ativa no repertório
Cada música do Repertório DEVE (MUST) ter atalhos para marcar ou desmarcar favorita e para ativar ou desativar, sem abrir o formulário de edição. Depois do atalho, a lista DEVE (MUST) continuar com a mesma busca, os mesmos filtros e a mesma posição. O atalho DEVE (MUST) gravar o estado escolhido (não apenas inverter), para que um clique repetido não desfaça a ação.

#### Scenario: Marcar favorita
- **GIVEN** "Tempo Perdido" não é favorita e o Repertório está filtrado por gênero "rock"
- **WHEN** o usuário aciona o atalho de favorita de "Tempo Perdido"
- **THEN** "Tempo Perdido" passa a ser favorita
- **AND** o Repertório continua filtrado por gênero "rock"

#### Scenario: Desativar
- **GIVEN** "Índios" está ativa
- **WHEN** o usuário aciona o atalho de ativa de "Índios"
- **THEN** "Índios" fica inativa e deixa de participar do sorteio (RN04)

#### Scenario: Clique repetido
- **GIVEN** o usuário marcou "Tempo Perdido" como favorita pelo atalho
- **WHEN** a mesma requisição de marcar favorita chega de novo
- **THEN** "Tempo Perdido" continua favorita

#### Scenario: Música inexistente
- **GIVEN** não existe música com o id informado
- **WHEN** chega uma requisição de atalho para esse id
- **THEN** o sistema responde "não encontrado" sem alterar nada
