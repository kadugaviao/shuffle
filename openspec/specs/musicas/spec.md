# musicas Specification

## Purpose

Manter o repertório pessoal de músicas conhecidas (CRUD completo), com os dados usados pelos filtros e pelo sorteio.

## Requirements

### Requirement: Cadastrar música (RN01)
O sistema DEVE (MUST) permitir cadastrar uma música com título e artista obrigatórios (RN01) e gênero, humor, dificuldade, link do YouTube, link do Spotify e outro link. Toda música nova DEVE (MUST) começar com favorita = falso e ativa = verdadeiro. Espaços no início e no fim do título DEVEM (MUST) ser descartados.

#### Scenario: Cadastro válido
- **GIVEN** existe o artista "Legião Urbana"
- **WHEN** o usuário cadastra "Tempo Perdido" de "Legião Urbana", gênero "rock", humor "calma", dificuldade 2
- **THEN** a música aparece no repertório como ativa e não favorita
- **AND** o sistema exibe "Música cadastrada."

#### Scenario: Título vazio (RN01)
- **GIVEN** o formulário de música
- **WHEN** o usuário envia o formulário com o título vazio ou só com espaços
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe "Informe o título da música." mantendo os dados digitados

#### Scenario: Sem artista (RN01)
- **GIVEN** o formulário de música
- **WHEN** o usuário envia o formulário sem escolher um artista
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe "Escolha o artista da música."

### Requirement: Música única por artista (RN02)
O sistema NÃO DEVE (MUST NOT) permitir duas músicas com o mesmo título e o mesmo artista (RN02), sem diferenciar maiúsculas de minúsculas. O mesmo título com artistas diferentes DEVE (MUST) ser aceito.

#### Scenario: Duplicata rejeitada
- **GIVEN** existe "Tempo Perdido" de "Legião Urbana"
- **WHEN** o usuário cadastra ou edita outra música para "tempo perdido" de "Legião Urbana"
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a alteração
- **AND** exibe "Essa música já está cadastrada para esse artista."

#### Scenario: Mesmo título, outro artista
- **GIVEN** existe "Hallelujah" de "Leonard Cohen"
- **WHEN** o usuário cadastra "Hallelujah" de "Jeff Buckley"
- **THEN** a música é cadastrada normalmente

### Requirement: Dificuldade entre 1 e 5 (RN03)
A dificuldade DEVE (MUST) ser obrigatória e estar entre 1 e 5 (RN03). O formulário de cadastro DEVE (MUST) vir preenchido com 3.

#### Scenario: Valor fora da faixa
- **GIVEN** o formulário de música
- **WHEN** o usuário envia dificuldade 0, 6 ou um valor não numérico
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe "A dificuldade deve ser um número de 1 a 5."

#### Scenario: Valor no limite
- **GIVEN** o formulário de música
- **WHEN** o usuário envia dificuldade 1 ou 5
- **THEN** a música é gravada com essa dificuldade

### Requirement: Humor da lista fixa
O humor DEVE (MUST) ser opcional e, quando informado, ser um destes: animada, calma, triste, romantica. O gênero DEVE (MUST) ser texto livre opcional.

#### Scenario: Humor inválido
- **GIVEN** o formulário de música
- **WHEN** a requisição chega com humor "eufórica"
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe "Escolha um humor da lista."

### Requirement: Link seguro
O outro link (cifra, letra, busca) DEVE (MUST) ser opcional e, quando informado, começar com "http://" ou "https://". O sistema NÃO DEVE (MUST NOT) aceitar outros esquemas de link.

#### Scenario: Link válido
- **GIVEN** o formulário de música
- **WHEN** o usuário informa no outro link "https://www.cifraclub.com.br/legiao-urbana/tempo-perdido/"
- **THEN** a música é gravada e o link aparece clicável no resultado, abrindo em nova aba

#### Scenario: Esquema proibido
- **GIVEN** o formulário de música
- **WHEN** o usuário informa no outro link "javascript:alert(1)"
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe "O link deve começar com http:// ou https://."

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

### Requirement: Editar música
O sistema DEVE (MUST) permitir editar todos os dados de uma música, inclusive marcar ou desmarcar favorita e ativar ou desativar, aplicando as validações RN01, RN02 e RN03.

#### Scenario: Marcar favorita e desativar
- **GIVEN** "Tempo Perdido" está ativa e não favorita
- **WHEN** o usuário edita a música, marca favorita e desmarca ativa
- **THEN** o repertório mostra "Tempo Perdido" como favorita e inativa

#### Scenario: Edição inválida
- **GIVEN** "Tempo Perdido" tem dificuldade 2
- **WHEN** o usuário edita a dificuldade para 7
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a alteração e a música continua com dificuldade 2

### Requirement: Excluir música com cascata (RN08)
O sistema DEVE (MUST) excluir uma música só após confirmação do usuário. Excluir uma música DEVE (MUST) remover também os sorteios dela no histórico e os vínculos dela com playlists (RN08).

#### Scenario: Exclusão remove histórico e vínculos (RN08)
- **GIVEN** "Tempo Perdido" foi sorteada 3 vezes e está na playlist "Roda de violão"
- **WHEN** o usuário exclui a música e confirma
- **THEN** a música some do repertório
- **AND** os 3 sorteios dela somem do histórico
- **AND** a playlist "Roda de violão" continua existindo, sem "Tempo Perdido"

#### Scenario: Confirmação cancelada
- **GIVEN** a música "Tempo Perdido"
- **WHEN** o usuário clica em excluir e cancela a confirmação
- **THEN** a música, seus sorteios e seus vínculos continuam iguais

### Requirement: Persistência em banco relacional
Os dados de artistas, músicas, playlists e sorteios DEVEM (MUST) ser gravados em banco de dados relacional e DEVEM (MUST) continuar disponíveis depois que o sistema é reiniciado.

#### Scenario: Reinício do servidor
- **GIVEN** o usuário cadastrou a música "Tempo Perdido"
- **WHEN** o servidor é parado e iniciado de novo
- **THEN** "Tempo Perdido" continua no repertório

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

### Requirement: Links do YouTube e do Spotify
Os campos YouTube e Spotify DEVEM (MUST) ser opcionais. Quando informado, o campo YouTube só DEVE (MUST) aceitar link de vídeo (youtube.com/watch?v=, music.youtube.com/watch?v=, youtu.be/, youtube.com/shorts/) e o campo Spotify só link de faixa (open.spotify.com/track/ ou open.spotify.com/intl-xx/track/), com as mesmas regras estritas de domínio e de ID do player. O erro DEVE (MUST) aparecer junto ao campo, preservando os dados digitados.

#### Scenario: Os três links
- **GIVEN** o formulário de música
- **WHEN** o usuário informa o YouTube "https://youtu.be/jNQXAC9IVRw", o Spotify "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC" e o outro link "https://www.cifraclub.com.br/legiao-urbana/tempo-perdido/"
- **THEN** a música é gravada com os três links

#### Scenario: Busca no campo YouTube
- **GIVEN** o formulário de música
- **WHEN** o usuário informa no campo YouTube "https://www.youtube.com/results?search_query=tempo+perdido"
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe junto ao campo YouTube "Cole o link de um vídeo do YouTube (youtube.com/watch?v=… ou youtu.be/…)."
- **AND** os demais campos continuam com o que foi digitado

#### Scenario: Álbum no campo Spotify
- **GIVEN** o formulário de música
- **WHEN** o usuário informa no campo Spotify "https://open.spotify.com/album/4uLU6hMCjMI75M1A2tKUQC"
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música
- **AND** exibe junto ao campo Spotify "Cole o link de uma faixa do Spotify (open.spotify.com/track/…)."

#### Scenario: Link do serviço trocado
- **GIVEN** o formulário de música
- **WHEN** o usuário cola um link de faixa do Spotify no campo YouTube
- **THEN** o sistema NÃO DEVE (MUST NOT) gravar a música e exibe o erro junto ao campo YouTube

#### Scenario: Banco criado antes dos campos novos
- **GIVEN** um banco criado por uma versão anterior, sem as colunas de YouTube e Spotify, com músicas cadastradas
- **WHEN** o sistema é iniciado
- **THEN** as colunas passam a existir vazias e nenhuma música é perdida
