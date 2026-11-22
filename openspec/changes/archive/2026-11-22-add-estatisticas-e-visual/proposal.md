# Proposal: add-estatisticas-e-visual

## Why

A tela 7 do plano ("Histórico e estatísticas") ficou só com o histórico no MVP: faltam as estatísticas da seção 5.3 de `docs/plan.md`. Ao mesmo tempo, o trio avaliou que o visual atual é simples demais para a apresentação de 24/11 e que algumas tarefas do dia a dia exigem cliques demais (marcar favorita, ativar/desativar, avaliar). Esta mudança fecha a tela 7, encurta esses caminhos e dá ao sistema uma identidade visual própria ("Midnight Stage"), registrada como design system para as próximas mudanças.

## What Changes

**Parte A: funcional**
- **Estatísticas** na tela de histórico: cartões de resumo, top 5 mais tocadas, músicas nunca sorteadas, média de notas por música e contagem de músicas por gênero.
- **Atalhos no Repertório**: marcar/desmarcar favorita e ativar/desativar direto no cartão da música, sem abrir o formulário.
- **Avaliação com 5 estrelas** clicáveis, que só aparecem depois de "Toquei" (substitui o seletor de nota + botão "Avaliar"; a RN07 continua valendo no servidor).
- **Tela inicial sem músicas**: convite "Cadastre sua primeira música" no lugar do sorteio quando o repertório está vazio.
- **Aba atual destacada** no menu.
- **Revelação do resultado**: animação curta estilo roleta logo depois de sortear.
- **Erros de formulário junto ao campo** e **confirmações em toasts**.
- O significado de `tocada = 0` não muda: pulada e sem resposta continuam iguais.

**Parte B: redesign visual "Midnight Stage"**
- Interface escura com cartões de vidro fosco, luz difusa no fundo e um único gradiente de destaque.
- Fontes Geist, Geist Mono e Instrument Serif hospedadas no próprio projeto (funciona sem internet).
- Navegação em barra superior de vidro no desktop e barra inferior com ícones no celular.
- Filtros em chips, repertório em cartões com capa gerada, estatísticas em barras de CSS puro.
- Requisitos não funcionais novos: contraste AA, `prefers-reduced-motion` e funcionamento sem internet; a responsividade a 360 px passa a valer para todas as telas, inclusive as novas.

### Fora do escopo (trabalho futuro)

Modo "Esquecidas", Setlist, modo festa em tela cheia, importar/exportar CSV, modo desafio, player embutido e modo claro. Também fica de fora qualquer mudança no schema do banco.

## Capabilities

### New Capabilities

- `estatisticas`: indicadores calculados a partir do repertório e do histórico de sorteios (resumo, top 5, nunca sorteadas, médias de nota, músicas por gênero).
- `interface`: requisitos transversais da interface: navegação com aba atual, confirmações e erros de formulário, responsividade, contraste, movimento reduzido e funcionamento sem internet.

### Modified Capabilities

- `sorteio`: a tela de resultado troca o botão "Avaliar" pelas estrelas exibidas após "Toquei"; nova revelação animada do resultado; nova tela inicial para repertório vazio; o requisito "Interface responsiva" sai daqui e passa para `interface`, ampliado para todas as telas.
- `historico`: a avaliação passa a ser feita pelas 5 estrelas, que só aparecem depois de "Toquei".
- `musicas`: novos atalhos de favorita e ativa no Repertório.

## Impact

- Código: templates Jinja (todos), `static/style.css` reescrito, `static/app.js` ampliado, novos ícones SVG inline, novas rotas `POST /musicas/<id>/favorita` e `POST /musicas/<id>/ativa`, novo módulo `estatisticas.py` (consultas), ajustes em `musicas.py` (erros por campo), `sorteio.py` e `historico.py`.
- Banco: nenhuma mudança de schema; só consultas novas sobre as tabelas existentes.
- Novos arquivos estáticos: `static/fonts/` (Geist, Geist Mono, Instrument Serif em woff2 + licença OFL).
- Testes: os testes que conferem trechos de HTML do MVP precisam ser atualizados junto com cada tela redesenhada.
- Documentação: `docs/screenshots/` com capturas a 360 px e desktop para a apresentação; README com a seção de estatísticas.
- Dependências: nenhuma nova (sem framework CSS, sem biblioteca JS).
