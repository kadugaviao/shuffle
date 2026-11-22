# Delta: historico

## MODIFIED Requirements

### Requirement: Registrar sorteio
Cada sorteio realizado DEVE (MUST) ser registrado no histórico com a música sorteada, a data e hora e tocada = falso, antes de o resultado ser mostrado.

#### Scenario: Novo registro
- **GIVEN** o histórico tem 4 sorteios
- **WHEN** o usuário sorteia "Tempo Perdido"
- **THEN** o histórico passa a ter 5 sorteios, o mais recente com "Tempo Perdido" e não tocada

#### Scenario: Recarregar o resultado
- **GIVEN** o usuário está na tela de resultado de um sorteio
- **WHEN** ele recarrega a página no navegador
- **THEN** o sistema mostra o mesmo resultado e NÃO DEVE (MUST NOT) registrar um novo sorteio

### Requirement: Marcar como tocada (Toquei)
Na tela de resultado o sistema DEVE (MUST) permitir marcar o sorteio como tocada = verdadeiro pelo botão "Toquei".

#### Scenario: Toquei
- **GIVEN** o resultado mostra "Tempo Perdido", ainda não tocada
- **WHEN** o usuário clica em "Toquei"
- **THEN** o sorteio fica com tocada = verdadeiro
- **AND** a tela passa a mostrar "Tocada" e libera a avaliação

### Requirement: Pular e sortear de novo
O botão "Pular" DEVE (MUST) manter o sorteio atual com tocada = falso e fazer um novo sorteio com os mesmos filtros e o mesmo N. A música pulada DEVE (MUST) contar como rodada para a anti-repetição.

#### Scenario: Pular
- **GIVEN** o resultado mostra "Tempo Perdido", sorteada com humor "calma" e N = 5
- **AND** existe outra música calma ativa não sorteada recentemente
- **WHEN** o usuário clica em "Pular"
- **THEN** o sorteio de "Tempo Perdido" continua no histórico como não tocada
- **AND** um novo sorteio é feito com humor "calma" e N = 5, com resultado diferente de "Tempo Perdido"

### Requirement: Avaliar sorteio tocado (RN07)
O sistema DEVE (MUST) permitir dar ao sorteio uma nota inteira de 1 a 5 pelo botão "Avaliar". A nota só DEVE (MUST) ser aceita em sorteios marcados como tocada (RN07). Avaliar de novo DEVE (MUST) substituir a nota anterior.

#### Scenario: Avaliar música tocada (RN07)
- **GIVEN** o sorteio de "Tempo Perdido" está marcado como tocada
- **WHEN** o usuário avalia com nota 5
- **THEN** o sorteio fica com nota 5

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

### Requirement: Listar histórico
O sistema DEVE (MUST) listar os 50 sorteios mais recentes, do mais novo para o mais antigo, com data e hora local, título, artista, situação (tocada ou não) e nota. Cada item DEVE (MUST) abrir a tela de resultado daquele sorteio, onde o usuário pode marcar como tocada e avaliar.

#### Scenario: Ordem e conteúdo
- **GIVEN** o usuário sorteou "Oceano" às 20:00 e "Tempo Perdido" às 20:05, e tocou e avaliou "Tempo Perdido" com nota 4
- **WHEN** o usuário abre o histórico
- **THEN** "Tempo Perdido" aparece primeiro, com 20:05, "Tocada" e nota 4
- **AND** "Oceano" aparece depois, com 20:00, "Não tocada" e sem nota

#### Scenario: Histórico vazio
- **GIVEN** nenhum sorteio foi feito
- **WHEN** o usuário abre o histórico
- **THEN** o sistema exibe "Nenhum sorteio ainda. Que tal sortear agora?"

### Requirement: Última música na tela inicial
A tela inicial DEVE (MUST) mostrar a última música sorteada, com o artista e a data e hora do sorteio, quando houver.

#### Scenario: Com sorteio anterior
- **GIVEN** o último sorteio foi "Tempo Perdido"
- **WHEN** o usuário abre a tela inicial
- **THEN** a tela mostra "Última sorteada: Tempo Perdido — Legião Urbana"

### Requirement: Histórico removido com a música (RN08)
Quando uma música é excluída, todos os sorteios dela DEVEM (MUST) sair do histórico (RN08) e deixar de contar para a anti-repetição.

#### Scenario: Exclusão da música (RN08)
- **GIVEN** "Oceano" tem 2 sorteios no histórico
- **WHEN** o usuário exclui a música "Oceano"
- **THEN** o histórico não mostra mais nenhum sorteio de "Oceano"
