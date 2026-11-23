# Spec Delta: interface

## ADDED Requirements

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

## MODIFIED Requirements

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
