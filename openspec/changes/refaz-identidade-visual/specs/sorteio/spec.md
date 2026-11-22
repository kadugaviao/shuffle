# Spec Delta: sorteio

## MODIFIED Requirements

### Requirement: Nenhuma música encontrada (RN05)
Quando nenhuma música ativa atender aos filtros, o sistema DEVE (MUST) exibir uma mensagem amigável em vez de um erro (RN05) e NÃO DEVE (MUST NOT) registrar sorteio no histórico.

#### Scenario: Filtro sem resultado (RN05)
- **GIVEN** não existe música ativa com humor "triste"
- **WHEN** o usuário sorteia com humor "triste"
- **THEN** o sistema volta para a tela inicial com a mensagem "Nada com esse filtro. Tira algum?"
- **AND** mantém os filtros escolhidos
- **AND** nenhum sorteio é registrado

#### Scenario: Repertório vazio (RN05)
- **GIVEN** não há nenhuma música ativa cadastrada
- **WHEN** o usuário clica em "Sortear"
- **THEN** o sistema exibe a mesma mensagem amigável, sem erro

### Requirement: Revelação animada do resultado
Logo depois de um sorteio, a tela de resultado DEVE (MUST) exibir uma animação de no máximo 1,5 segundo em que títulos do repertório passam na vertical e desaceleram até parar na música sorteada, sem repique. Ao parar, um carimbo "TOCA ESSA!" DEVE (MUST) aparecer sobre o resultado. A animação NÃO DEVE (MUST NOT) se repetir ao recarregar a página ou ao abrir o sorteio pelo histórico, e o resultado DEVE (MUST) ficar disponível mesmo sem JavaScript.

#### Scenario: Revelação depois de sortear
- **GIVEN** o repertório tem músicas ativas
- **WHEN** o usuário clica em "Sortear"
- **THEN** títulos passam rápido de baixo para cima e desaceleram até parar na música sorteada, sem passar do ponto e voltar
- **AND** o carimbo "TOCA ESSA!" aparece em seguida, e a animação toda termina em até 1,5 segundo
- **AND** só então os botões do resultado ficam disponíveis

#### Scenario: Recarregar não repete
- **GIVEN** o usuário já viu a revelação de um sorteio
- **WHEN** ele recarrega a página ou abre o mesmo sorteio pelo histórico
- **THEN** o resultado aparece direto, sem a animação
- **AND** o carimbo aparece parado no lugar

#### Scenario: Sorteio já tocado
- **GIVEN** um sorteio marcado como tocada
- **WHEN** o usuário abre esse sorteio
- **THEN** o carimbo mostra "TOCADA" no lugar de "TOCA ESSA!"

#### Scenario: Navegador sem JavaScript
- **GIVEN** o JavaScript está desativado no navegador
- **WHEN** o usuário sorteia
- **THEN** o título, o artista, o carimbo e os botões do resultado aparecem normalmente
