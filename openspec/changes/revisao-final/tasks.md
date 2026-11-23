# Tasks: revisao-final

Referências: achados em `docs/revisao-final.md` (IDs entre parênteses), comportamento nas deltas de `specs/`, decisões em `design.md` (D1–D10). Testes com `python -m unittest`. Cada correção de bug começa pelo teste, conferido falhando antes da correção. Ao fim de cada grupo, a suíte inteira DEVE estar verde e o grupo é commitado como `fix(revisao): grupo N - <nome>` (o último como `docs(revisao): ...`). Ordem de prioridade se o tempo apertar: grupo 1, grupo 2, grupo 4 (README e screenshots) e por último o grupo 3.

## 1. Tela de resultado (D1–D5, D10, D11, B2, A4)

- [ ] 1.1 Commitar o relatório e os artefatos desta mudança antes de qualquer código (`docs: auditoria e specs revisao-final`); verificar com `git log -1 --stat` que só entraram `docs/revisao-final.md` e `openspec/changes/revisao-final/`
- [ ] 1.2 Escrever os testes do resultado novo (D10): seletor com dois `aria-pressed="false"`, botão simples com um serviço, links "Abrir no…" como `<a class="link-abrir">`, "Fechar player" presente e escondido, "Toquei"/"Pular" antes da seção de ouvir no HTML, degraus `titulo-longo` e `titulo-palavra-longa`; ajustar os testes antigos de "Ouvir no YouTube"; verificar que os novos falham
- [ ] 1.3 Reestruturar `sorteio/resultado.html` em `.resultado-principal` + `.resultado-ouvir` (D1), com o seletor, os links e o fechar player (D2), o carimbo e a data no topo e as duas classes de título (D3); verificar que os testes de 1.2 e os de atributos do iframe passam
- [ ] 1.4 CSS: folha sem `max-width`, duas colunas a partir de 960 px com régua, `.segmentado-2`, `.link-abrir`, data em linha só, degrau de palavra longa só abaixo de 720 px; verificar no Chrome a 360 e 1440 px que não há vazio lateral nem rolagem horizontal, e que com o player aberto "Toquei" e "Pular" continuam acima dele no celular (cenário "Ações principais sempre à vista")
- [ ] 1.5 `app.js`: seletor com `aria-pressed`, troca de player, "Fechar player" com anúncio `aria-live` e foco devolvido, roleta posicionada por `offsetTop` do título (D3); verificar pelo DevTools Protocol os cenários "YouTube e Spotify", "Fechar o player" e "Abrir o resultado" (zero requisições externas), a roleta terminando no lugar do título e o movimento reduzido; suíte verde; commitar o grupo

## 2. Outras telas (D6–D9, D12, D13, D15, B1, S1, S3)

- [ ] 2.1 Teste e cenário do filtro por gênero no sorteio (S1): "ROCK" traz só a música de rock; verificar que passa (o comportamento já existe; o teste trava o requisito)
- [ ] 2.2 Teste de remover música fora da playlist (B1), conferido falhando; corrigir `playlists.remover()` com `rowcount` (D5); verificar que passa
- [ ] 2.3 Testes do repertório vazio (D15) e do plural (D12), conferidos falhando; implementar o "Caderno em branco" sem filtros e o filtro `plural` nas 4 contagens, ajustando os testes que conferiam "música(s)"; verificar que passam
- [ ] 2.4 Início: linha compacta "Última sorteada" abaixo do "Sortear" abaixo de 960 px (D6); hover do "Sortear" (D7); verificar a 360 px que a linha aparece sem rolar e a 1440 px que só a folha da direita aparece
- [ ] 2.5 Repertório: dificuldade no início de `.musica-acoes` (D8); aba atual com rótulo amarelo (D9); ícone `dado` no CTA do histórico vazio (D13); ajustes de base 4 (D10); verificar a 360 px que todas as linhas do repertório têm a mesma estrutura, e que os testes anti-slop e de contraste continuam passando; suíte verde; commitar o grupo

## 3. Formulários e acessibilidade (A1–A3, A5, A6, SEG1)

- [ ] 3.1 Testes dos limites de tamanho (SEG1) para música, artista e playlist, conferidos falhando; implementar os dicionários de limites e os `maxlength` (D6); verificar que passam, inclusive os cenários "Título longo demais" e "Nome de artista longo demais"
- [ ] 3.2 Testes de `aria-required`, dica ligada por `aria-describedby` e `aria-label` do interruptor inativo, conferidos falhando; implementar `aria()`/`campo()` com `obrigatorio` e `dica`, as três dicas dos links e o rótulo acessível do interruptor (D7); verificar que passam
- [ ] 3.3 `app.js`: foco no primeiro campo inválido, rótulo acessível do interruptor atualizado no atalho e região live dos avisos (D8); `role="list"` nas listas, ajustando os testes de HTML exato; verificar pelo DevTools Protocol o cenário "Foco no primeiro erro", a região live preenchida depois do carregamento e o `aria-label` após o atalho; suíte verde; commitar o grupo

## 4. Documentação e entrega (DOC1–DOC4, SEG2)

- [ ] 4.1 `requirements.txt` com `Flask==3.1.3` e `docs/plan.md` com os critérios de pronto marcados (exceto o ensaio); verificar `pip install -r requirements.txt` num venv novo
- [ ] 4.2 Refazer os screenshots (D9): celular 390 px a 2× (início, resultado, histórico) e desktop 1440 px (início, resultado), página inteira, mesma largura por grupo, WebP; apagar os que não forem usados; verificar abrindo cada imagem que nada fica atrás da barra fixa e que a aba atual aparece
- [ ] 4.3 Reescrever o `README.md` na estrutura de D9 (equipe, requisitos com versões, como rodar só com comandos, comandos úteis, problemas comuns, OpenSpec com as 5 mudanças arquivadas, stack, pastas, screenshots e limitações); verificar que não sobra "Shuffle Meu", "TODO" ou texto provisório
- [ ] 4.4 Cópia limpa: `git clone` num diretório temporário, executar cada comando do README na ordem (inclusive testes, recriar o banco, `openspec validate --strict` e `tools/verificar_links.py` com um link) e conferir o app respondendo em http://127.0.0.1:5000; anotar qualquer divergência e corrigir o README
- [ ] 4.5 Rodar a suíte, `openspec validate revisao-final --strict` e `openspec validate --all --strict`; atualizar `docs/revisao-final.md` com o estado de cada item (corrigido ou trabalho futuro); verificar que nenhum servidor ficou rodando; commitar o grupo

## Workflow follow-up

- Arquivar com `/opsx:archive revisao-final` depois da revisão do trio, sincronizando as specs de `sorteio`, `musicas`, `playlists` e `interface`.
