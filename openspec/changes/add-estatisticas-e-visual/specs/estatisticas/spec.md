# Spec Delta: estatisticas

## Purpose

Mostrar indicadores calculados a partir do repertório e do histórico de sorteios, para o usuário ver o que mais toca, o que esquece e do que mais gosta.

## ADDED Requirements

### Requirement: Tela de histórico e estatísticas
A tela de histórico DEVE (MUST) mostrar as estatísticas acima da lista de sorteios, com um resumo de quatro números: músicas no repertório, sorteios feitos, sorteios tocados e nota média geral (média de todas as notas dadas, com uma casa decimal e vírgula).

#### Scenario: Resumo com dados
- **GIVEN** o repertório tem 25 músicas e o histórico tem 10 sorteios, 6 deles tocados, com as notas 4, 5 e 5
- **WHEN** o usuário abre a tela de histórico
- **THEN** o resumo mostra 25 músicas, 10 sorteios, 6 tocadas e nota média 4,7

#### Scenario: Resumo sem sorteios
- **GIVEN** o repertório tem 3 músicas e nenhum sorteio foi feito
- **WHEN** o usuário abre a tela de histórico
- **THEN** o resumo mostra 3 músicas, 0 sorteios, 0 tocadas e "—" na nota média

### Requirement: Top 5 mais tocadas
O sistema DEVE (MUST) mostrar as até 5 músicas com mais sorteios marcados como tocada, da mais tocada para a menos tocada, com a quantidade de vezes. Em caso de empate DEVE (MUST) valer a ordem alfabética do título. Músicas nunca tocadas NÃO DEVEM (MUST NOT) aparecer no ranking.

#### Scenario: Ranking com empate
- **GIVEN** "Evidências" foi tocada 4 vezes, "Oceano" 2 vezes, "Hey Jude" 2 vezes e "Índios" foi sorteada 3 vezes sem ser tocada
- **WHEN** o usuário abre a tela de histórico
- **THEN** o ranking mostra "Evidências" (4), "Hey Jude" (2) e "Oceano" (2), nessa ordem
- **AND** "Índios" não aparece no ranking

#### Scenario: Mais de 5 músicas tocadas
- **GIVEN** 7 músicas diferentes foram tocadas
- **WHEN** o usuário abre a tela de histórico
- **THEN** o ranking mostra só as 5 primeiras

#### Scenario: Nenhuma música tocada
- **GIVEN** nenhum sorteio foi marcado como tocada
- **WHEN** o usuário abre a tela de histórico
- **THEN** o ranking exibe "Nenhuma música tocada ainda."

### Requirement: Músicas nunca sorteadas
O sistema DEVE (MUST) listar, em ordem alfabética, as músicas ativas que não têm nenhum sorteio no histórico. Músicas inativas NÃO DEVEM (MUST NOT) aparecer nessa lista, porque não podem ser sorteadas.

#### Scenario: Lista de esquecidas
- **GIVEN** as músicas ativas "Yesterday" e "Ainda Bem" nunca foram sorteadas, e a inativa "We Will Rock You" também não
- **WHEN** o usuário abre a tela de histórico
- **THEN** a lista mostra "Ainda Bem" e "Yesterday", nessa ordem
- **AND** não mostra "We Will Rock You"

#### Scenario: Todas já sorteadas
- **GIVEN** toda música ativa tem ao menos um sorteio
- **WHEN** o usuário abre a tela de histórico
- **THEN** a lista exibe "Todas as músicas ativas já foram sorteadas."

### Requirement: Média de notas por música
O sistema DEVE (MUST) mostrar, para cada música com ao menos uma nota, a média das notas com uma casa decimal e vírgula e a quantidade de avaliações. A ordem DEVE (MUST) ser da maior média para a menor; empates ficam com quem tem mais avaliações e, depois, pela ordem alfabética do título.

#### Scenario: Médias ordenadas
- **GIVEN** "Oceano" tem as notas 5 e 4, "Evidências" tem a nota 5 e "Hey Jude" tem as notas 3 e 3
- **WHEN** o usuário abre a tela de histórico
- **THEN** a lista mostra "Evidências" 5,0 (1 avaliação), "Oceano" 4,5 (2 avaliações) e "Hey Jude" 3,0 (2 avaliações), nessa ordem

#### Scenario: Nenhuma avaliação
- **GIVEN** nenhum sorteio tem nota
- **WHEN** o usuário abre a tela de histórico
- **THEN** a seção exibe "Nenhuma música avaliada ainda."

### Requirement: Músicas por gênero
O sistema DEVE (MUST) mostrar quantas músicas do repertório (ativas e inativas) existem em cada gênero, do maior para o menor, com empates em ordem alfabética. Gêneros que diferem só em maiúsculas/minúsculas DEVEM (MUST) contar juntos, exibidos com a grafia mais usada entre eles, e músicas sem gênero DEVEM (MUST) aparecer como "Sem gênero".

#### Scenario: Contagem por gênero
- **GIVEN** o repertório tem 3 músicas "rock", 1 "Rock", 2 "MPB" e 1 sem gênero
- **WHEN** o usuário abre a tela de histórico
- **THEN** a contagem mostra rock 4, MPB 2 e Sem gênero 1, nessa ordem

#### Scenario: Repertório vazio
- **GIVEN** não há músicas cadastradas
- **WHEN** o usuário abre a tela de histórico
- **THEN** a seção exibe "Nenhuma música no repertório."
