# Revisão final do Shuffle

Auditoria feita em **23/11/2026**, véspera da apresentação, só com leitura do código (nenhum arquivo de código foi alterado nesta fase). As correções propostas estão na mudança OpenSpec `revisao-final`.

## Como a revisão foi feita

- **Base:** `python -m unittest` (167 testes, todos passando), `openspec validate --specs --strict` e `openspec validate --all --strict` (7 de 7 itens válidos), leitura de `docs/plan.md`, `openspec/config.yaml`, das 7 specs, das 5 mudanças arquivadas, de `docs/links-verificados.md` e do código.
- **Entradas ruins:** script com o cliente de teste do Flask sobre um banco semeado:
  - IDs inexistentes em todas as rotas (13 rotas);
  - parâmetros inválidos na URL e no POST do sorteio (`n=abc`, `n=-5`, `dificuldade_max=9`, `artista_id=abc`, gênero com 5000 caracteres, `%00`);
  - notas inválidas;
  - XSS em título, artista, gênero e link;
  - textos de 5000 caracteres;
  - maiúsculas e acentos na RN02 e no nome de artista.
- **Navegador:** Chrome headless a 360 e 1440 px, com 30 capturas de página inteira (todas as telas e estados vazios, de erro e com 0, 1 e 2 players). Um roteiro pelo DevTools Protocol cobriu:
  - atalhos de favorita e ativa sem recarregar, persistindo depois do reload;
  - roleta e carimbo;
  - aviso da RN05 (fechar) e aviso de sucesso (some em 5 s);
  - filtro do repertório pelo teclado;
  - troca de player;
  - nenhuma requisição externa ao abrir telas.
- **Fluxos de negócio:** já cobertos por testes automáticos e conferidos nesta rodada: CRUD de artistas, músicas e playlists; sorteio simples e com filtros; anti-repetição e fallback da RN06; peso de favoritas; Toquei, Pular e estrelas (RN07); cascata (RN08); estatísticas vazias e com dados; seed rodado duas vezes; banco antigo recebendo as colunas novas.
- **Cópia limpa:** `git clone` do GitHub, seguindo o README ao pé da letra: venv, `pip install`, `python seed.py`, `python -m unittest` e `flask --app shuffle_meu run` respondendo 200. Debug desligado.
- **Design e acessibilidade:** revisões da ui-craft (`design-reviewer` e `a11y-auditor`) contra o design system "Lambe-lambe" e a seção Anti-slop, sobre o código e as capturas.

## Conformidade com o trabalho de G2

| Exigência | Situação | Evidência |
|---|---|---|
| Banco com no mínimo 2 tabelas | Cumprido | 5 tabelas em `shuffle_meu/schema.sql`. |
| CRUD completo de músicas e artistas | Cumprido | Rotas de listar, cadastrar, editar e excluir nos dois, testadas de ponta a ponta. |
| OpenSpec: specs antes do código | Cumprido | Em cada uma das 5 mudanças, o commit `docs: specs ...` vem antes dos commits de código. O último commit (`fix(texto)`) não passou pelo OpenSpec, mas não mudou nenhum requisito. |
| Código e Markdown no GitHub | Cumprido | Repositório público, sem commits pendentes. |

## Achados

Severidade: **Alta** afeta a apresentação ou viola regra registrada; **Média** é visível ou atrapalha o uso; **Baixa** é acabamento. Esforço: **P** (até ~30 min), **M** (algumas horas), **G** (mais que isso).

### Bug

| ID | Sev. | Onde | Como reproduzir | Correção sugerida | Esf. |
|---|---|---|---|---|---|
| B1 | Baixa | `playlists.py:106` (`remover`) | POST `/playlists/1/musicas/9999/remover`: responde "Música removida da playlist." sem ter removido nada. | Se nenhuma linha foi apagada, avisar "Essa música não está na playlist." (erro). | P |
| B2 | Média | `resultado.html:15` + `style.css:512-517` | A regra de título longo (palavra com mais de 8 letras) vale também no desktop: "Evidências" sai a 72 px e "Sem Links Nenhum" a 120 px, e a escala muda de uma música para outra sem motivo visual. | Aplicar o degrau de palavra longa só abaixo de 720 px (classe separada); no desktop, só o limite de 24 caracteres. | P |

### Spec

| ID | Sev. | Onde | Como reproduzir | Correção sugerida | Esf. |
|---|---|---|---|---|---|
| S1 | Média | `specs/sorteio` ("Sorteio com filtros") | O requisito cita o filtro por gênero, mas não há cenário nem teste que sorteie por gênero (só a leitura do parâmetro e a exibição do chip). | Cenário "Filtro por gênero" (sem diferenciar maiúsculas) e teste. | P |
| S2 | Baixa | `specs/playlists` ("Remover música da playlist") | Sem cenário para remover música que não está na playlist (ver B1). | Cenário novo junto com a correção de B1. | P |
| S3 | Baixa | `specs/musicas` ("Listar repertório") | O convite de repertório zerado ("O caderno ainda está em branco", com botão "Nova música") existe no código, mas não na spec. | Cenário "Repertório vazio" (ver D15). | P |
| S4 | Baixa | `specs/interface` (responsiva, teclado, movimento reduzido, offline, revelação ≤1,5 s) | Cenários verificados só manualmente e por captura; não há teste automático. | Registrar no README como foram conferidos; teste automático fica como trabalho futuro. | M |

RN01 a RN08: todas têm requisito, implementação e teste; nenhuma divergência encontrada.

### Segurança

| ID | Sev. | Onde | Como reproduzir | Correção sugerida | Esf. |
|---|---|---|---|---|---|
| SEG1 | Baixa | `musicas.py`, `artistas.py`, `playlists.py` | Os limites de tamanho estão só no HTML (`maxlength`); um POST direto grava título e nome de artista com 5000 caracteres. | Validar no servidor com os mesmos limites do formulário (título 200, gênero 60, nome de artista 120, país 80, playlist 120, descrição 200), com erro junto ao campo. | P |
| SEG2 | Baixa | `__init__.py:16` | `SECRET_KEY` cai em `"dev"` quando a variável de ambiente não existe. A sessão só guarda as marcas `revelar` e `tocou` e os avisos, então não há dado sensível. | Manter (uso local), documentar no README. | P |
| SEG3 | Baixa | rotas POST | Sem proteção CSRF. Risco real só se o servidor for publicado; já documentado nas limitações. | Trabalho futuro. | M |

Sem achado:
- SQL sempre parametrizado. As interpolações usam só nomes fixos do código: colunas do atalho, `CONDICOES` do sorteio, colunas novas do schema.
- O Jinja escapa título, artista, gênero e links. Confirmado com payload de XSS nas 5 telas.
- O único `|safe` é o dos ícones, que são constantes.
- Os links só aceitam `http`/`https`, validados no servidor e com `CHECK` no banco.
- YouTube e Spotify passam pelas regras estritas de `links.py`.
- Os iframes são montados só com o ID validado.
- O debug vem desligado por padrão.

### Design

| ID | Sev. | Onde | Como reproduzir | Correção sugerida | Esf. |
|---|---|---|---|---|---|
| D1 | Alta | resultado a 1440 px; `style.css:508` (`.resultado { max-width: 52rem }`) | A folha ocupa cerca de 76% do contêiner e deixa a direita vazia, contra a regra "nunca deixar um lado sobrando". As outras telas largas (início, repertório, histórico, artistas, playlists) ocupam o contêiner; formulários e detalhe de playlist são a exceção registrada. | Folha na largura do contêiner; a partir de 960 px, duas colunas: ações à esquerda, bloco "Ouvir aqui" com player e links "Abrir no…" à direita, separados por régua. | M |
| D2 | Alta | `resultado.html:21-28` | Até 4 botões de borda e peso iguais e larguras diferentes ("Ouvir no YouTube", "Ouvir no Spotify", "Abrir no YouTube", "Abrir no Spotify"); a 360 px viram uma pilha de quatro. | Linha "Ouvir aqui" com seletor segmentado [YouTube \| Spotify] (só os serviços disponíveis; com um serviço, o botão simples "Ouvir aqui"); "Abrir no…" como links de texto de 14 px com o ícone `link`, numa linha só. | M |
| D3 | Alta | `resultado.html:21-51` | Hierarquia invertida: "Toquei" e "Pular" vêm depois dos 4 botões de ouvir e abrir. | "Toquei" e "Pular" logo depois do artista, como ações principais. | P |
| D4 | Alta | `resultado.html:30-38` | Ao abrir o player, o iframe empurra "Toquei", "Pular" e estrelas para baixo; a 360 px elas saem da tela. | Player na coluna própria (desktop) e depois das ações (celular), ver D1. | M |
| D5 | Média | `resultado.html:13`; `style.css:511` | Quando o título quebra, o carimbo cai numa linha própria e deixa um bloco solto entre título e artista. | Carimbo na mesma linha da data e da capa (topo da folha), girado, sem depender do tamanho do título. | P |
| D6 | Média | `inicio.html:45-58`; `style.css:458-462` | A 360 px o bloco "Última sorteada" aparece depois de todos os filtros, a mais de 1000 px do topo. | No celular, linha compacta "Última sorteada: …" logo abaixo do "Sortear" (a spec de histórico exige que ela apareça no início). | P |
| D7 | Média | `style.css:238` | O "Sortear" é o único controle principal sem resposta ao passar o mouse. | Mesmo sublinhado dos botões primários, instantâneo. | P |
| D8 | Média | repertório a 360 px; `style.css:385`, `497` | A dificuldade quebra para linha própria quando as etiquetas são largas; as linhas ficam com 2 ou 3 alturas. | Dificuldade em posição fixa, na linha dos atalhos. | M |
| D9 | Baixa | barra inferior a 360 px | A régua vermelha da aba atual (4 px) fica colada na borda e lê como risco solto. | Rótulo da aba atual em amarelo, além da régua. | P |
| D10 | Baixa | `style.css:296`, `305`, `355`, `387`, `552` | Valores fora da base 4 (14 px no chip, 6 px na etiqueta, 5 px na marca do chip) e o `96px` mágico no `.rolo`, que amarra a roleta à altura da capa e quebra ao reorganizar o resultado (D1). | Trocar por tokens e derivar o deslocamento da roleta da estrutura. | P |
| D11 | Baixa | resultado a 360 px | "Sorteada em" quebra em duas linhas ao lado da capa. | Data numa linha só, em Plex Mono 14. | P |
| D12 | Baixa | artistas, playlists, repertório | Plural fixo "1 música(s)". | Pluralizar ("1 música", "8 músicas"); ajustar os testes. | P |
| D13 | Baixa | `historico.html` (estado vazio) | O botão "Que tal sortear agora?" usa o ícone "+" (de cadastrar). | Ícone `dado` ou `shuffle`. | P |
| D14 | Baixa | `resultado.html:27` | "Abrir link" é genérico; o conteúdo varia (busca do YouTube no seed, cifra, letra). | Rótulo depende do domínio; trabalho futuro. | M |
| D15 | Baixa | repertório com o banco vazio | Título "Nenhuma música encontrada." com a frase "O caderno ainda está em branco" e os filtros à mostra. | No vazio total: título "Caderno em branco", sem filtros, botão "Nova música". | P |
| D16 | Baixa | início a 1440 px | Abaixo da folha "Última sorteada", cerca de 600 px vazios ao lado dos filtros (estava no desenho original). | Trabalho futuro (mexe na composição do cartaz). | M |

### Acessibilidade

| ID | Sev. | Onde | Como reproduzir | Correção sugerida | Esf. |
|---|---|---|---|---|---|
| A1 | Média | `musicas/lista.html:46` | O interruptor de música inativa mostra "Fora do sorteio", mas o nome acessível é "Ativa: título" (WCAG 2.5.3, nome não contém o rótulo visível). | `aria-label` = rótulo visível + título ("Fora do sorteio: título"), atualizado pelo mesmo JS. | P |
| A2 | Média | `musicas/form.html`, `_macros.html:5` | Com erro, o foco não vai ao primeiro campo inválido, e os obrigatórios (Título, Artista) não têm `aria-required` (3.3.1, 3.3.2). | `autofocus` no primeiro campo com erro; `aria-required="true"` nos obrigatórios (vale também para artista e playlist). | P |
| A3 | Média | `musicas/form.html:34-44` | O formato esperado dos campos de link fica só no rótulo e no `placeholder`, que some ao digitar (3.3.2). | Dica curta abaixo de cada campo de link, ligada por `aria-describedby`. | P |
| A4 | Média | `app.js:106-111` | Ao ouvir, o foco vai para dentro do iframe de terceiros, sem aviso e sem como fechar o player (4.1.3). | Botão "Fechar player" junto do player e aviso em `aria-live` ("Player do YouTube aberto"). | M |
| A5 | Média | `base.html:36-39` | Avisos presentes no carregamento (`role="alert"`/`status` já no HTML) costumam não ser anunciados (4.1.3). | Região live vazia no HTML; o JS insere o texto do aviso depois do carregamento. Sem JS, o aviso continua visível e estático. | M |
| A6 | Baixa | listas com `list-style: none` | O VoiceOver/Safari descarta a semântica de lista (1.3.1). | `role="list"` em `.setlist`, `.lista-cartoes`, `.lista-simples` e `.barras`; ajustar os testes que conferem o HTML exato. | P |
| A7 | Baixa | `style.css:439` (estrelas) | Com foco no grupo, todas as estrelas acendem; `aria-pressed` só na nota exata. | Trabalho futuro (trocar por radiogroup). | M |
| A8 | Baixa | avisos fixos | O aviso fixo pode cobrir o foco de algo embaixo (2.4.11). | Fica como está: a spec exige aviso flutuante no canto. | — |

### Docs

| ID | Sev. | Onde | Como reproduzir | Correção sugerida | Esf. |
|---|---|---|---|---|---|
| DOC1 | Média | `README.md` | Faltam os passos de clonar e entrar na pasta. Usa `python` em vez de `python3`. Não tem "Problemas comuns" e não diz como instalar a CLI do OpenSpec. A estrutura não é a pedida para a entrega. | Reescrever o README na estrutura pedida (título, equipe, requisitos, como rodar, comandos úteis, problemas comuns, OpenSpec, stack e pastas, screenshots e limitações) e testar cada comando numa cópia limpa. | M |
| DOC2 | Média | `docs/screenshots/*.webp`, README | Escalas diferentes (celular 2×, desktop 1×), cortes no meio de blocos (início e histórico no desktop), barra inferior fixa tapando conteúdo (chips, contagem) e a pilha de 4 botões no resultado. | Refazer depois das correções: celular a 390 px (início, resultado, histórico), desktop a 1440 px (início, resultado), mesma escala e enquadramento por grupo, sem conteúdo atrás da barra fixa, marca da aba atual visível. | M |
| DOC3 | Baixa | `docs/plan.md:248-257` | "Critérios de pronto" todos desmarcados, embora cumpridos. | Marcar os cumpridos; deixar só o ensaio. | P |
| DOC4 | Baixa | `requirements.txt` | `Flask>=3.0` sem versão fixa (a instalada e testada é a 3.1.3). | Fixar `Flask==3.1.3`. | P |

## Resumo

| Severidade | Quantidade |
|---|---|
| Alta | 4 |
| Média | 13 |
| Baixa | 20 |
| **Total** | **37** |

Os 5 itens mais importantes para a apresentação:
1. **D1:** a tela de resultado deixa a direita vazia no desktop.
2. **D2 + D3:** botões de ouvir e abrir empilhados, competindo com "Toquei" e "Pular".
3. **D4:** o player empurra as ações para fora da tela no celular.
4. **DOC1 + DOC2:** README sem os passos de clonar, e screenshots inconsistentes.
5. **S1:** filtro por gênero sem cenário nem teste.
