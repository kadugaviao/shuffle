# Plano do Projeto — **Shuffle Meu** 🎵
### Sistema de sorteio de músicas conhecidas

> Projeto da disciplina de Engenharia de Software: **Trabalho de G2 (avaliação final, em trios)**
> Equipe: Kadu Brum Gavião, Miguel Mombach Foza e Josiel Paz
> Escopo exigido: sistema de tema livre com **banco de dados (mínimo de 2 tabelas)** e **CRUD completo**
> Metodologia: uso **obrigatório** do **OpenSpec** (especificar e documentar antes de programar)
> Entrega: código **e** artefatos Markdown no GitHub
> Apresentação: **24 de novembro**

---

## 1. Visão geral

O **Shuffle Meu** é um sistema para cadastrar as músicas que o usuário **já conhece** (sabe cantar, tocar ou gosta muito) e **sortear qual tocar** a seguir. Ele serve para quem toca um instrumento e não sabe o que praticar, para quem quer animar uma roda de amigos ou um karaokê e para quem cansou do aleatório dos aplicativos de streaming, que tocam músicas desconhecidas.

O sorteio é **inteligente**: ele evita repetir músicas tocadas há pouco tempo e permite filtrar por gênero, humor, dificuldade e playlist.

---

## 2. Problema

- Aplicativos de streaming sorteiam músicas que o usuário não conhece.
- Quem toca violão, teclado etc. costuma repetir sempre as mesmas 5 músicas e esquece o resto do repertório.
- Em rodas de amigos sempre bate a dúvida: "e agora, qual a gente toca?"

## 3. Objetivo

Permitir que o usuário mantenha um **repertório pessoal** e use um **sorteador configurável** que valoriza a variedade.

---

## 4. Modelo de dados (banco de dados)

São 5 tabelas: 4 principais e 1 de ligação. O trabalho exige no mínimo 2; só `artista` e `musica` já cumprem esse requisito.

### 4.1 `artista`
| Campo | Tipo | Observação |
|---|---|---|
| id | INTEGER PK | autoincremento |
| nome | TEXT | obrigatório, único |
| pais | TEXT | opcional |
| criado_em | DATETIME | padrão: agora |

### 4.2 `musica`
| Campo | Tipo | Observação |
|---|---|---|
| id | INTEGER PK | autoincremento |
| titulo | TEXT | obrigatório |
| artista_id | INTEGER FK → artista.id | obrigatório |
| genero | TEXT | ex.: rock, MPB, sertanejo, pop |
| humor | TEXT | `animada`, `calma`, `triste`, `romantica` |
| dificuldade | INTEGER | 1 (fácil) a 5 (difícil), útil para quem toca |
| link | TEXT | opcional (YouTube/Spotify/cifra) |
| favorita | BOOLEAN | padrão: falso |
| ativa | BOOLEAN | padrão: verdadeiro; música desativada não entra no sorteio |
| criado_em | DATETIME | padrão: agora |

### 4.3 `playlist`
| Campo | Tipo | Observação |
|---|---|---|
| id | INTEGER PK | |
| nome | TEXT | obrigatório, ex.: "Roda de violão", "Churrasco" |
| descricao | TEXT | opcional |

**Tabela de ligação `playlist_musica`** (relação N:N): `playlist_id`, `musica_id`

### 4.4 `sorteio` (histórico)
| Campo | Tipo | Observação |
|---|---|---|
| id | INTEGER PK | |
| musica_id | INTEGER FK → musica.id | música sorteada |
| sorteado_em | DATETIME | padrão: agora |
| tocada | BOOLEAN | o usuário confirmou que tocou? |
| nota | INTEGER | 1 a 5, avaliação depois de tocar (opcional) |

### Relacionamentos
```
artista 1 ──── N musica
musica  N ──── N playlist   (via playlist_musica)
musica  1 ──── N sorteio
```

---

## 5. Funcionalidades

### 5.1 CRUD completo (obrigatório)

> Para cumprir o escopo do trabalho, **músicas** e **artistas** precisam ter as 4 operações (Create, Read, Update, Delete) funcionando de ponta a ponta, da tela até o banco.

**Artistas**
- Cadastrar, listar, editar e excluir artistas.
- Não é possível excluir um artista que ainda tem músicas (ou a exclusão pede confirmação e remove em cascata).

**Músicas**
- **Create:** cadastrar uma música com título, artista, gênero, humor, dificuldade e link.
- **Read:** listar músicas com busca por título/artista e filtros (gênero, humor, favorita).
- **Update:** editar dados, marcar ou desmarcar como favorita, ativar ou desativar.
- **Delete:** excluir a música, com confirmação.

**Playlists**
- Criar, renomear e excluir playlists.
- Adicionar e remover músicas de uma playlist.

### 5.2 Sorteio 🎲 (funcionalidade principal)
- **Sorteio simples:** sorteia uma música aleatória entre as ativas.
- **Sorteio com filtros:** por gênero, humor, dificuldade máxima, artista ou playlist.
- **Anti-repetição:** músicas sorteadas nas últimas *N* rodadas (configurável, padrão 5) não entram no sorteio.
- **Peso para favoritas:** favoritas têm o dobro de chance de serem sorteadas.
- **"Esquecidas":** modo que prioriza músicas que não são sorteadas há mais tempo, ou que nunca foram.
- **Sortear de novo:** se o usuário não gostar do resultado, pode pular. O pulo é registrado como `tocada = falso`.
- **Setlist:** sorteia uma sequência de *X* músicas sem repetição, útil para apresentações e rodas.

### 5.3 Histórico e estatísticas 📊
- Lista dos últimos sorteios com data e hora.
- Top 5 músicas mais tocadas.
- Músicas que nunca foram sorteadas.
- Média de notas por música.
- Contagem de músicas por gênero.

### 5.4 Extras (se der tempo)
- **Modo festa:** tela cheia com animação de "roleta" antes de revelar a música.
- **Importar e exportar** o repertório em CSV.
- **Abrir link:** botão que abre a cifra ou o vídeo da música sorteada.
- **Desafio:** sorteia uma música com dificuldade acima da média do usuário, para ele praticar.

---

## 6. Regras de negócio

| Código | Regra |
|---|---|
| RN01 | O título da música e o artista são obrigatórios. |
| RN02 | Não pode haver duas músicas com o mesmo título **e** o mesmo artista. |
| RN03 | A dificuldade deve estar entre 1 e 5. |
| RN04 | Apenas músicas com `ativa = verdadeiro` participam do sorteio. |
| RN05 | Se o filtro não encontrar nenhuma música, o sistema exibe uma mensagem amigável em vez de dar erro. |
| RN06 | Se todas as músicas filtradas estiverem bloqueadas pela anti-repetição, o bloqueio é ignorado (com aviso). |
| RN07 | A nota só pode ser dada em sorteios marcados como `tocada`. |
| RN08 | Excluir uma música remove também o histórico e os vínculos com playlists. |

---

## 7. Requisitos não funcionais
- Interface simples e responsiva (funciona no celular).
- Sorteio responde em menos de 1 segundo com até 1.000 músicas.
- Dados persistidos em banco de dados relacional.
- Código **e** artefatos OpenSpec versionados no GitHub, com um README explicando como rodar.

---

## 8. Sugestão de tecnologias
| Camada | Opção sugerida | Alternativa |
|---|---|---|
| Back-end | Python + Flask | Node.js + Express |
| Banco | SQLite | MySQL / PostgreSQL |
| Front-end | HTML + CSS + JS (ou templates Jinja) | React |
| Especificação | OpenSpec (CLI) + agente de IA (Claude Code, Copilot, Cursor...) | — |
| Versionamento | Git + GitHub | — |

---

## 9. Metodologia: OpenSpec (obrigatório)

A regra do trabalho é **especificar e documentar antes de programar**. A IA só escreve código depois que os artefatos Markdown estão prontos, e é guiada por eles.

### 9.1 Iniciando no terminal
```bash
npm install -g @fission-ai/openspec@latest
openspec init        # na raiz do repositório; escolha o agente usado pelo trio
```

### 9.2 O fluxo de 4 passos aplicado ao projeto
| Passo | Comando no agente | O que o trio faz no Shuffle Meu |
|---|---|---|
| 1. **Explore** | `/opsx:explore` | Discute com a IA o modelo de dados, as regras do sorteio e os casos de uso, **sem escrever código**. |
| 2. **Propose** | `/opsx:propose add-mvp` | A IA formaliza a discussão nos artefatos (`proposal.md`, `design.md`, `tasks.md` e as specs). O trio revisa e corrige antes de seguir. |
| 3. **Apply** | `/opsx:apply` | A IA implementa banco, CRUD e sorteio seguindo **estritamente** o `tasks.md`, marcando cada tarefa concluída. |
| 4. **Archive** | `/opsx:archive` | Arquiva a mudança concluída, atualiza `openspec/specs/` e limpa o contexto ativo. |

> Cada funcionalidade grande (ex.: estatísticas, modo festa) pode virar uma nova mudança, repetindo os 4 passos.

### 9.3 Estrutura de especificação
```
openspec/
├── config.yaml             # contexto do projeto, stack e convenções (criado pelo openspec init)
├── specs/                  # fonte da verdade: como o sistema funciona hoje
│   ├── musicas/spec.md     # requisitos e cenários do CRUD de músicas
│   ├── artistas/spec.md
│   ├── playlists/spec.md
│   ├── sorteio/spec.md     # regras do sorteio (filtros, peso, anti-repetição)
│   └── historico/spec.md
└── changes/
    ├── add-mvp/            # mudança em andamento
    │   ├── proposal.md     # o que e por quê
    │   ├── design.md       # decisões técnicas
    │   ├── tasks.md        # checklist de implementação
    │   └── specs/...       # deltas das specs
    └── archive/            # mudanças concluídas (ex.: 2026-11-23-add-mvp/)
```

### 9.4 Exemplo de requisito no formato OpenSpec
```markdown
### Requirement: Sorteio com anti-repetição
O sistema DEVE impedir que uma música sorteada nas últimas N rodadas seja sorteada novamente.

#### Scenario: Música recente é ignorada
- **GIVEN** a música "Tempo Perdido" foi sorteada na rodada anterior
- **AND** N = 5
- **WHEN** o usuário solicita um novo sorteio
- **THEN** "Tempo Perdido" NÃO deve ser o resultado

#### Scenario: Todas as músicas bloqueadas
- **GIVEN** existem apenas 3 músicas ativas, e todas foram sorteadas recentemente
- **WHEN** o usuário solicita um sorteio
- **THEN** o sistema sorteia entre elas mesmo assim
- **AND** exibe o aviso "Você já tocou todas recentemente!"
```

---

## 10. Telas previstas
1. **Início:** botão grande "🎲 Sortear", filtros rápidos e a última música sorteada.
2. **Repertório:** lista de músicas com busca, filtros e os botões editar e excluir.
3. **Formulário de música:** cadastro e edição.
4. **Artistas:** CRUD simples.
5. **Playlists:** lista e gerenciamento das músicas de cada playlist.
6. **Resultado do sorteio:** música, artista, link, e os botões "Toquei ✅", "Pular ⏭️" e "Avaliar ⭐".
7. **Histórico e estatísticas.**

---

## 11. Cronograma (até a apresentação em 24/11)
| Etapa | Passo OpenSpec | Entrega |
|---|---|---|
| 1 | Explore + Propose | `openspec init`, `config.yaml` e a mudança `add-mvp` com proposal, design, tasks e specs revisados pelo trio |
| 2 | Apply | Banco de dados criado + CRUD de artistas e músicas |
| 3 | Apply | CRUD de playlists + sorteio simples e com filtros |
| 4 | Apply | Anti-repetição, peso de favoritas, histórico |
| 5 | Archive | Arquivar `add-mvp`, estatísticas, ajustes visuais, README, ensaio da apresentação |

> Prioridade se o tempo apertar: **CRUD de músicas + artistas + sorteio simples**, com os artefatos OpenSpec. Isso já cumpre o escopo mínimo do trabalho. O resto é bônus.

---

## 12. Critérios de pronto (MVP)
- [ ] Banco com as tabelas `artista`, `musica`, `playlist`, `playlist_musica` e `sorteio` (mínimo exigido: 2)
- [ ] CRUD completo de músicas e artistas funcionando
- [ ] Sorteio funcionando com pelo menos 1 filtro
- [ ] Histórico de sorteios salvo
- [ ] OpenSpec iniciado (`openspec/config.yaml`) e specs em Markdown no repositório (`openspec/specs/`)
- [ ] Mudança `add-mvp` passou pelos 4 passos e está em `openspec/changes/archive/`
- [ ] Histórico de commits mostra as specs escritas **antes** do código
- [ ] README com o nome dos integrantes do trio e as instruções de instalação e execução
- [ ] Código e artefatos no GitHub, com o repositório acessível ao professor
- [ ] Apresentação ensaiada para **24/11**