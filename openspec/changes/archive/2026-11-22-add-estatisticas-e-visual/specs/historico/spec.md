# Spec Delta: historico

## MODIFIED Requirements

### Requirement: Avaliar sorteio tocado (RN07)
O sistema DEVE (MUST) permitir dar ao sorteio uma nota inteira de 1 a 5 clicando numa de 5 estrelas, que só DEVEM (MUST) aparecer depois que o sorteio é marcado como tocada. A nota só DEVE (MUST) ser aceita em sorteios marcados como tocada (RN07). Avaliar de novo DEVE (MUST) substituir a nota anterior, e as estrelas DEVEM (MUST) mostrar a nota atual.

#### Scenario: Avaliar música tocada (RN07)
- **GIVEN** o sorteio de "Tempo Perdido" está marcado como tocada
- **WHEN** o usuário clica na quinta estrela
- **THEN** o sorteio fica com nota 5
- **AND** as cinco estrelas aparecem acesas

#### Scenario: Estrelas escondidas antes de tocar
- **GIVEN** o sorteio de "Tempo Perdido" não está marcado como tocada
- **WHEN** o usuário abre a tela de resultado
- **THEN** as estrelas de avaliação não aparecem
- **AND** depois de clicar em "Toquei" elas aparecem

#### Scenario: Avaliar sem ter tocado (RN07)
- **GIVEN** o sorteio de "Tempo Perdido" não está marcado como tocada
- **WHEN** a requisição de avaliação chega com nota 4
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a nota
- **AND** exibe "Marque como tocada antes de avaliar."

#### Scenario: Nota fora da faixa
- **GIVEN** um sorteio marcado como tocada
- **WHEN** a requisição de avaliação chega com nota 0, 6 ou um valor não numérico
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a nota
- **AND** exibe "A nota deve ser de 1 a 5."
