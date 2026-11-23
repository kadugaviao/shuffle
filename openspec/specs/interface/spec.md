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
Todo texto DEVE (MUST) ter contraste de no mínimo 4,5:1 com o fundo, ou 3:1 para texto grande (a partir de 24 px, ou 18,66 px em negrito), inclusive texto sobre o amarelo, o vermelho e a tinta. Texto sobre o vermelho de impressão só DEVE (MUST) ser usado em tamanho grande. O amarelo NÃO DEVE (MUST NOT) ser usado como cor de texto sobre o papel. Só ficam de fora controles desabilitados e elementos puramente decorativos.

#### Scenario: Conferência de contraste
- **GIVEN** as telas do sistema com dados de exemplo
- **WHEN** o contraste de cada combinação de cor de texto e fundo é medido
- **THEN** todas atingem o mínimo exigido para o tamanho do texto

#### Scenario: Botão vermelho
- **GIVEN** o botão "Sortear" e os demais botões de ação primária, que têm fundo vermelho
- **WHEN** o contraste do texto é medido
- **THEN** o texto tem pelo menos 3:1 e está em tamanho grande (18,66 px em negrito ou mais)

### Requirement: Movimento reduzido
Quando o sistema operacional do usuário pede movimento reduzido, a interface NÃO DEVE (MUST NOT) exibir animações (roleta, entrada do carimbo, deslocamento do botão "Sortear", entrada de avisos e de estrelas) e as transições DEVEM (MUST) ser instantâneas.

#### Scenario: Resultado sem roleta
- **GIVEN** o navegador está com a preferência de movimento reduzido ativada
- **WHEN** o usuário sorteia uma música
- **THEN** o resultado aparece imediatamente, sem a animação de roleta
- **AND** o carimbo já aparece no lugar, sem mudar de tamanho

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

### Requirement: Nome do sistema
Todas as telas DEVEM (MUST) mostrar o nome "Shuffle" na marca da navegação, escrito em caixa alta ("SHUFFLE"), e o título da aba do navegador DEVE (MUST) terminar com "| Shuffle". O nome antigo "Shuffle Meu" NÃO DEVE (MUST NOT) aparecer em nenhuma tela.

#### Scenario: Título e marca
- **GIVEN** o sistema está rodando
- **WHEN** o usuário abre o Repertório
- **THEN** a aba do navegador mostra "Repertório | Shuffle"
- **AND** a navegação mostra a marca "SHUFFLE", que leva à tela inicial

#### Scenario: Nome antigo ausente
- **GIVEN** o repertório tem músicas e sorteios
- **WHEN** o usuário percorre Início, resultado do sorteio, Repertório, formulário de música, Artistas, Playlists e Histórico
- **THEN** nenhuma tela mostra o texto "Shuffle Meu"

### Requirement: Identidade visual "Lambe-lambe"
A interface DEVE (MUST) usar só as cores do design system "Lambe-lambe" (papel, papel alternado, tinta, tinta secundária, amarelo, vermelho e as variações registradas no design), as fontes Big Shoulders Display, Archivo e IBM Plex Mono servidas pelo próprio sistema, raio 0 em blocos e réguas e no máximo 4 px em campos e botões.

#### Scenario: Conferência dos tokens
- **GIVEN** a folha de estilos do sistema
- **WHEN** as cores, fontes e raios declarados são conferidos
- **THEN** todas as cores de texto, fundo e borda vêm dos tokens do design system
- **AND** nenhum raio passa de 4 px
- **AND** as únicas famílias de fonte são Big Shoulders Display, Archivo e IBM Plex Mono, com fallbacks do sistema

#### Scenario: Números alinhados
- **GIVEN** a tela de histórico com estatísticas
- **WHEN** o usuário olha o resumo, o ranking e as contagens
- **THEN** os números aparecem em IBM Plex Mono com algarismos de largura fixa

### Requirement: Proibições anti-slop
A interface NÃO DEVE (MUST NOT) usar gradientes, desfoque de fundo (vidro), brilho (glow), textura de ruído, sombras difusas, curvas de animação com repique (mola, bounce, overshoot), animações em cascata no carregamento, emoji como ícone nem preto puro (#000) em texto. A única sombra permitida é o deslocamento de impressão do botão "Sortear".

#### Scenario: Folha de estilos limpa
- **GIVEN** a folha de estilos e os templates do sistema
- **WHEN** eles são verificados pelos testes automáticos
- **THEN** não há `gradient(`, `backdrop-filter`, `blur(` nem curva `cubic-bezier` com valores fora de 0 a 1 no eixo do progresso
- **AND** a única `box-shadow` é a do botão "Sortear"
- **AND** nenhum template contém emoji

#### Scenario: Botões do resultado sem emoji
- **GIVEN** um sorteio que ainda não foi tocado
- **WHEN** o usuário abre a tela de resultado
- **THEN** os botões mostram "Toquei" e "Pular" com ícones desenhados em traço, sem emoji

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
