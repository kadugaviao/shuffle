# sorteio Specification

## Purpose

Sortear qual música do repertório tocar a seguir, valorizando a variedade: só músicas ativas, filtros, anti-repetição e peso para favoritas.

## Requirements

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

### Requirement: Sorteio com filtros
O sistema DEVE (MUST) permitir filtrar o sorteio por gênero, humor, dificuldade máxima, artista e playlist. Os filtros informados DEVEM (MUST) ser combinados entre si (todos precisam ser atendidos); filtro em branco NÃO DEVE (MUST NOT) restringir.

#### Scenario: Filtro por humor e dificuldade
- **GIVEN** "Oceano" é calma com dificuldade 4 e "Tempo Perdido" é calma com dificuldade 2
- **WHEN** o usuário sorteia com humor "calma" e dificuldade máxima 3
- **THEN** o resultado é "Tempo Perdido"

#### Scenario: Filtro por playlist
- **GIVEN** a playlist "Roda de violão" contém só "Tempo Perdido"
- **WHEN** o usuário sorteia com a playlist "Roda de violão"
- **THEN** o resultado é "Tempo Perdido"

#### Scenario: Filtro por artista
- **GIVEN** "Djavan" tem uma única música ativa, "Oceano"
- **WHEN** o usuário sorteia com o artista "Djavan"
- **THEN** o resultado é "Oceano"

### Requirement: Nenhuma música encontrada (RN05)
Quando nenhuma música ativa atender aos filtros, o sistema DEVE (MUST) exibir uma mensagem amigável em vez de um erro (RN05) e NÃO DEVE (MUST NOT) registrar sorteio no histórico.

#### Scenario: Filtro sem resultado (RN05)
- **GIVEN** não existe música ativa com humor "triste"
- **WHEN** o usuário sorteia com humor "triste"
- **THEN** o sistema volta para a tela inicial com a mensagem "Nenhuma música encontrada com esses filtros. Tente afrouxar os filtros."
- **AND** mantém os filtros escolhidos
- **AND** nenhum sorteio é registrado

#### Scenario: Repertório vazio (RN05)
- **GIVEN** não há nenhuma música ativa cadastrada
- **WHEN** o usuário clica em "Sortear"
- **THEN** o sistema exibe a mesma mensagem amigável, sem erro

### Requirement: Sorteio com anti-repetição
O sistema DEVE (MUST) impedir que uma música sorteada nas últimas N rodadas seja sorteada novamente. Uma rodada é qualquer sorteio registrado no histórico, inclusive os pulados. N DEVE (MUST) ser escolhido no formulário de sorteio, de 0 a 50, com padrão 5; N = 0 desliga a anti-repetição.

#### Scenario: Música recente é ignorada
- **GIVEN** a música "Tempo Perdido" foi sorteada na rodada anterior
- **AND** N = 5
- **AND** existe outra música ativa que atende aos filtros e não foi sorteada recentemente
- **WHEN** o usuário solicita um novo sorteio
- **THEN** "Tempo Perdido" NÃO deve ser o resultado

#### Scenario: Bloqueio expira depois de N rodadas
- **GIVEN** N = 2 e "Tempo Perdido" foi sorteada 3 rodadas atrás
- **WHEN** o usuário solicita um sorteio
- **THEN** "Tempo Perdido" pode ser sorteada

#### Scenario: N inválido
- **GIVEN** o formulário de sorteio
- **WHEN** a requisição chega com N = -1, 51 ou um valor não numérico
- **THEN** o sistema usa o padrão N = 5

### Requirement: Todas bloqueadas pela anti-repetição (RN06)
Se todas as músicas que atendem aos filtros estiverem bloqueadas pela anti-repetição, o sistema DEVE (MUST) ignorar o bloqueio, sortear entre elas e exibir um aviso (RN06).

#### Scenario: Todas as músicas bloqueadas (RN06)
- **GIVEN** existem apenas 3 músicas ativas, e todas foram sorteadas recentemente
- **WHEN** o usuário solicita um sorteio
- **THEN** o sistema sorteia entre elas mesmo assim
- **AND** exibe o aviso "Você já tocou todas recentemente!"

### Requirement: Peso para favoritas
Entre as músicas candidatas, uma favorita DEVE (MUST) ter o dobro da chance de ser sorteada em relação a uma não favorita.

#### Scenario: Chance dobrada
- **GIVEN** as candidatas são "Tempo Perdido" (favorita) e "Oceano" (não favorita)
- **WHEN** o sistema calcula as chances do sorteio
- **THEN** "Tempo Perdido" tem 2/3 de chance e "Oceano" tem 1/3

#### Scenario: Verificação estatística
- **GIVEN** as mesmas duas candidatas e 3.000 sorteios com anti-repetição desligada
- **WHEN** os resultados são contados
- **THEN** "Tempo Perdido" sai entre 60% e 73% das vezes

### Requirement: Desempenho do sorteio
O sorteio DEVE (MUST) responder em menos de 1 segundo com até 1.000 músicas cadastradas.

#### Scenario: Repertório grande
- **GIVEN** 1.000 músicas ativas e 1.000 sorteios no histórico
- **WHEN** o usuário clica em "Sortear" com filtros
- **THEN** a tela de resultado é respondida pelo servidor em menos de 1 segundo

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
