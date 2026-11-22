# Spec Delta: sorteio

## MODIFIED Requirements

### Requirement: Sorteio simples (RN04)
O sistema DEVE (MUST) sortear uma música entre as que têm ativa = verdadeiro (RN04). Uma música inativa NÃO DEVE (MUST NOT) ser sorteada.

#### Scenario: Só ativas participam (RN04)
- **GIVEN** o repertório tem "Tempo Perdido" ativa e "Índios" inativa
- **AND** nenhuma das duas foi sorteada recentemente
- **WHEN** o usuário clica em "Sortear" sem filtros
- **THEN** o resultado é "Tempo Perdido"

#### Scenario: Tela de resultado
- **GIVEN** existe ao menos uma música ativa
- **WHEN** o usuário clica em "Sortear"
- **THEN** o sistema mostra o título, o artista e o link (se houver) da música sorteada
- **AND** os botões "Toquei" e "Pular"
- **AND** as estrelas de avaliação só aparecem depois que o sorteio é marcado como tocada

## ADDED Requirements

### Requirement: Revelação animada do resultado
Logo depois de um sorteio, a tela de resultado DEVE (MUST) exibir uma animação de no máximo 1,5 segundo em que títulos do repertório passam e desaceleram até parar na música sorteada. A animação NÃO DEVE (MUST NOT) se repetir ao recarregar a página ou ao abrir o sorteio pelo histórico, e o resultado DEVE (MUST) ficar disponível mesmo sem JavaScript.

#### Scenario: Revelação depois de sortear
- **GIVEN** o repertório tem músicas ativas
- **WHEN** o usuário clica em "Sortear"
- **THEN** títulos passam rápido e desaceleram até parar na música sorteada em até 1,5 segundo
- **AND** só então os botões do resultado ficam disponíveis

#### Scenario: Recarregar não repete
- **GIVEN** o usuário já viu a revelação de um sorteio
- **WHEN** ele recarrega a página ou abre o mesmo sorteio pelo histórico
- **THEN** o resultado aparece direto, sem a animação

#### Scenario: Navegador sem JavaScript
- **GIVEN** o JavaScript está desativado no navegador
- **WHEN** o usuário sorteia
- **THEN** o título, o artista e os botões do resultado aparecem normalmente

### Requirement: Tela inicial com repertório vazio
Quando não há nenhuma música cadastrada, a tela inicial DEVE (MUST) mostrar, no lugar do botão "Sortear" e dos filtros, o convite "Cadastre sua primeira música" com um botão que leva ao formulário de nova música.

#### Scenario: Primeiro acesso
- **GIVEN** não há nenhuma música cadastrada
- **WHEN** o usuário abre a tela inicial
- **THEN** a tela mostra "Cadastre sua primeira música" e o botão para o formulário de nova música
- **AND** não mostra o botão "Sortear"

#### Scenario: Só músicas inativas
- **GIVEN** existem músicas, mas todas estão inativas
- **WHEN** o usuário abre a tela inicial e clica em "Sortear"
- **THEN** o sistema exibe a mensagem amigável da RN05, como antes

## REMOVED Requirements

### Requirement: Interface responsiva
**Reason**: A responsividade vale para todas as telas, não só para o sorteio. O requisito passa para a capacidade `interface`, que reúne os requisitos transversais e agora cobre também as telas novas.
**Migration**: Ver "Interface responsiva" em `interface/spec.md`, que mantém o cenário "Sorteio pelo celular" e acrescenta o percurso por todas as telas.
