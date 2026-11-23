# Spec Delta: interface

## ADDED Requirements

### Requirement: Tamanho máximo dos textos
O sistema DEVE (MUST) recusar no servidor textos maiores que os limites do formulário (título 200, gênero 60, links 500, nome de artista 120, país 80, nome de playlist 120, descrição 200 caracteres), mesmo que o pedido não venha do formulário, mostrando o erro junto ao campo e preservando os dados digitados.

#### Scenario: Título longo demais
- **GIVEN** um pedido de cadastro de música com título de 201 caracteres
- **WHEN** o sistema recebe o pedido
- **THEN** a música não é gravada
- **AND** o erro "O título pode ter no máximo 200 caracteres." aparece junto ao campo Título

#### Scenario: Nome de artista longo demais
- **GIVEN** um pedido de cadastro de artista com nome de 121 caracteres
- **WHEN** o sistema recebe o pedido
- **THEN** o artista não é gravado e o erro aparece junto ao campo Nome

## MODIFIED Requirements

### Requirement: Erros de formulário junto ao campo
Erros de validação DEVEM (MUST) aparecer junto ao campo que os causou, com o campo marcado como inválido, na mesma tela do formulário e com os dados digitados preservados. Ao voltar com erro, o foco DEVE (MUST) estar no primeiro campo inválido, e os campos obrigatórios DEVEM (MUST) ser identificados como obrigatórios para tecnologias assistivas.

#### Scenario: Título vazio
- **GIVEN** o formulário de nova música
- **WHEN** o usuário salva com o título vazio e dificuldade 3
- **THEN** a mensagem "Informe o título da música." aparece logo abaixo do campo Título
- **AND** o campo Título fica marcado como inválido e a dificuldade continua 3

#### Scenario: Foco no primeiro erro
- **GIVEN** o formulário de nova música
- **WHEN** o usuário salva com o título preenchido, sem artista e com um álbum no campo Spotify
- **THEN** o foco fica no campo Artista, o primeiro com erro
- **AND** os campos Título e Artista estão marcados como obrigatórios
