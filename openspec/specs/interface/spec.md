# interface Specification

## Purpose

Reunir os requisitos que valem para todas as telas: navegação, mensagens ao usuário, responsividade, acessibilidade e funcionamento sem internet.

## Requirements

### Requirement: Navegação com aba atual
Todas as telas DEVEM (MUST) ter o menu com Início, Repertório, Artistas, Playlists e Histórico, destacando a seção atual de forma visível e identificável por leitores de tela. Telas internas (formulários, detalhe de playlist, resultado do sorteio) DEVEM (MUST) destacar a seção a que pertencem. No celular, o menu DEVE (MUST) ficar fixo na parte de baixo da tela, com ícone e nome de cada seção.

#### Scenario: Seção atual
- **GIVEN** o usuário está na tela de edição de uma música
- **WHEN** ele olha o menu
- **THEN** o item "Repertório" aparece destacado e marcado como página atual
- **AND** nenhum outro item aparece destacado

#### Scenario: Menu no celular
- **GIVEN** um navegador com 360 px de largura
- **WHEN** o usuário abre qualquer tela
- **THEN** os 5 itens do menu ficam numa barra fixa na parte de baixo, com ícone e nome
- **AND** a barra não cobre o último conteúdo da página quando ele rola até o fim

### Requirement: Mensagens de confirmação temporárias
Confirmações de sucesso (como "Artista cadastrado." e "Avaliação salva.") DEVEM (MUST) aparecer como aviso flutuante no canto da tela e sumir sozinhas depois de 5 segundos. Mensagens de erro e de alerta DEVEM (MUST) continuar visíveis até o usuário fechá-las. Toda mensagem DEVE (MUST) ser anunciada por leitores de tela.

#### Scenario: Confirmação some sozinha
- **GIVEN** o usuário cadastrou um artista
- **WHEN** a lista de artistas aparece
- **THEN** o aviso "Artista cadastrado." aparece no canto da tela
- **AND** some sozinho depois de 5 segundos

#### Scenario: Alerta fica até fechar
- **GIVEN** o sorteio ignorou a anti-repetição (RN06)
- **WHEN** a tela de resultado aparece
- **THEN** o aviso "Você já tocou todas recentemente!" continua visível até o usuário fechá-lo

### Requirement: Erros de formulário junto ao campo
Erros de validação DEVEM (MUST) aparecer junto ao campo que os causou, com o campo marcado como inválido, na mesma tela do formulário e com os dados digitados preservados.

#### Scenario: Título vazio
- **GIVEN** o formulário de nova música
- **WHEN** o usuário salva com o título vazio e dificuldade 3
- **THEN** a mensagem "Informe o título da música." aparece logo abaixo do campo Título
- **AND** o campo Título fica marcado como inválido e a dificuldade continua 3

### Requirement: Interface responsiva
Todas as telas, inclusive as estatísticas, DEVEM (MUST) funcionar no celular e no desktop: com largura de 360 px, todo o conteúdo e os controles DEVEM (MUST) ficar visíveis e utilizáveis sem rolagem horizontal da página.

#### Scenario: Telas a 360 px
- **GIVEN** um navegador com 360 px de largura
- **WHEN** o usuário percorre Início, resultado do sorteio, Repertório, formulário de música, Artistas, Playlists e Histórico
- **THEN** nenhuma tela tem rolagem horizontal e nenhum botão ou campo fica cortado

#### Scenario: Sorteio pelo celular
- **GIVEN** um navegador com 360 px de largura
- **WHEN** o usuário abre a tela inicial, sorteia e vê o resultado
- **THEN** o botão "Sortear", os filtros e os botões do resultado cabem na tela sem rolagem horizontal

### Requirement: Contraste de texto AA
Todo texto DEVE (MUST) ter contraste de no mínimo 4,5:1 com o fundo, ou 3:1 para texto grande (a partir de 24 px, ou 18,66 px em negrito), inclusive texto sobre o gradiente de destaque. Só ficam de fora controles desabilitados e elementos puramente decorativos.

#### Scenario: Conferência de contraste
- **GIVEN** as telas do sistema com dados de exemplo
- **WHEN** o contraste de cada combinação de cor de texto e fundo é medido
- **THEN** todas atingem o mínimo exigido para o tamanho do texto

### Requirement: Movimento reduzido
Quando o sistema operacional do usuário pede movimento reduzido, a interface NÃO DEVE (MUST NOT) exibir animações decorativas (fundo em movimento, brilho pulsando, roleta, efeitos de clique) e as transições DEVEM (MUST) ser instantâneas.

#### Scenario: Resultado sem roleta
- **GIVEN** o navegador está com a preferência de movimento reduzido ativada
- **WHEN** o usuário sorteia uma música
- **THEN** o resultado aparece imediatamente, sem a animação de roleta
- **AND** o fundo e o botão "Sortear" ficam parados

### Requirement: Navegação por teclado
Todos os controles DEVEM (MUST) ser alcançáveis e acionáveis pelo teclado, com indicador de foco visível, inclusive os chips de filtro, as estrelas de avaliação e os atalhos de favorita e ativa.

#### Scenario: Avaliar pelo teclado
- **GIVEN** um sorteio marcado como tocada
- **WHEN** o usuário chega às estrelas com Tab e aciona a quarta com Enter
- **THEN** o foco aparece visível em cada estrela percorrida
- **AND** o sorteio fica com nota 4

### Requirement: Funcionamento sem internet
A interface DEVE (MUST) manter a aparência completa (fontes, ícones e estilos) sem conexão com a internet, usando apenas arquivos servidos pelo próprio sistema.

#### Scenario: Apresentação offline
- **GIVEN** o computador está sem conexão com a internet e o sistema está rodando localmente
- **WHEN** o usuário abre qualquer tela
- **THEN** as fontes, os ícones e os estilos aparecem iguais aos da versão conectada
