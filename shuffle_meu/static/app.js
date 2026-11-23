// Shuffle: melhorias progressivas. Tudo funciona sem este arquivo; aqui só entram animação e atalhos.
const movimentoReduzido = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

// Confirmação antes de enviar formulários marcados com data-confirmar (exclusões).
document.addEventListener("submit", (evento) => {
  const mensagem = evento.target.dataset.confirmar;
  if (mensagem && !confirm(mensagem)) evento.preventDefault();
});

// Toasts: sucesso some em 5 s (pausa com hover/foco); erro e aviso ficam até fechar.
function iniciarToasts() {
  const toasts = document.querySelectorAll(".toast");
  const regiao = document.querySelector("[data-anunciar]");
  if (toasts.length && regiao) {
    setTimeout(() => { regiao.textContent = [...toasts].map((t) => t.querySelector("p").textContent).join(" "); }, 100);
  }
  for (const toast of toasts) {
    const sair = () => {
      toast.classList.add("saindo");
      setTimeout(() => toast.remove(), movimentoReduzido() ? 0 : 120); // = --rapido
    };
    const fechar = toast.querySelector(".toast-fechar");
    fechar.hidden = false;
    fechar.addEventListener("click", sair);
    if (!("auto" in toast.dataset)) continue;

    let restante = 5000;
    let inicio = 0;
    let timer = null;
    const rodar = () => { if (timer === null) { inicio = Date.now(); timer = setTimeout(sair, restante); } };
    const pausar = () => {
      if (timer === null) return;
      clearTimeout(timer);
      timer = null;
      restante -= Date.now() - inicio;
    };
    toast.addEventListener("mouseenter", pausar);
    toast.addEventListener("focusin", pausar);
    toast.addEventListener("mouseleave", rodar);
    toast.addEventListener("focusout", rodar);
    rodar();
  }
}

// Roleta (D7): faixa vertical de títulos sobe e desacelera até a sorteada (1,2 s), depois o carimbo entra.
// Só existe logo após sortear; com movimento reduzido o CSS já mostra o resultado parado.
function iniciarRoleta() {
  const folha = document.querySelector("[data-roleta]");
  if (!folha || movimentoReduzido()) return;
  const titulos = JSON.parse(folha.dataset.roleta);
  const sorteada = titulos.at(-1);
  const outros = titulos.slice(0, -1);
  const itens = Array.from({ length: 20 }, (_, i) => (outros.length ? outros[i % outros.length] : sorteada));
  itens.push(sorteada);
  const faixa = folha.querySelector(".rolo-faixa");
  const titulo = folha.querySelector(".titulo-sorteado");
  faixa.parentElement.classList.toggle("rolo-longo", titulo.classList.contains("titulo-longo")); // mesmo degrau do título
  faixa.parentElement.classList.toggle("rolo-palavra-longa", titulo.classList.contains("titulo-palavra-longa"));
  folha.querySelector(".rolo").style.paddingTop = `${titulo.offsetTop}px`; // a janela abre onde o título vai aparecer
  faixa.replaceChildren(...itens.map((t) => Object.assign(document.createElement("li"), { textContent: t })));
  folha.classList.add("rodando");
  requestAnimationFrame(() => requestAnimationFrame(() => {
    faixa.style.transform = `translateY(${-100 * (itens.length - 1) / itens.length}%)`;
  }));
  setTimeout(() => {
    folha.classList.replace("rodando", "revelado");
    folha.querySelector("[data-anuncio]").textContent =
      `Sorteada: ${folha.querySelector(".titulo-sorteado").textContent}, ${folha.querySelector(".artista").textContent}`;
  }, 1200); // = duração de --rolar
}

// Atalhos do Repertório (D2): POST via fetch e troca o estado no lugar; se falhar, envia o formulário normal.
document.addEventListener("submit", async (evento) => {
  const form = evento.target;
  if (!form.matches("[data-atalho]") || evento.defaultPrevented) return;
  evento.preventDefault();
  const botao = form.querySelector("button");
  const valor = form.elements.valor;
  try {
    const resposta = await fetch(form.action, { method: "POST", body: new FormData(form), redirect: "manual" });
    if (!resposta.ok && resposta.type !== "opaqueredirect") throw new Error(String(resposta.status));
  } catch {
    form.submit();
    return;
  }
  const ligado = valor.value === "1";
  const interruptor = botao.getAttribute("role") === "switch";
  botao.setAttribute(interruptor ? "aria-checked" : "aria-pressed", String(ligado));
  valor.value = ligado ? "0" : "1";
  if (interruptor) {
    form.closest(".musica-cartao")?.classList.toggle("inativa", !ligado);
    const rotulo = ligado ? "Ativa" : "Fora do sorteio";
    botao.querySelector(".interruptor-rotulo").textContent = rotulo;
    botao.setAttribute("aria-label", botao.getAttribute("aria-label").replace(/^[^:]*/, rotulo)); // nome = rótulo visível
  }
});

// Filtros do Repertório: chips e "Só favoritas" aplicam na hora quando clicados. Pelo teclado não: as setas
// mudam o radio a cada passo e recarregar ali tiraria o foco (WCAG 3.2.2); quem usa teclado aplica com "Filtrar".
let ultimoPeloPonteiro = false;
document.addEventListener("pointerdown", () => { ultimoPeloPonteiro = true; });
document.addEventListener("keydown", () => { ultimoPeloPonteiro = false; });
document.addEventListener("change", (evento) => {
  const form = evento.target.closest("form[data-auto-enviar]");
  if (form && ultimoPeloPonteiro && evento.target.matches("input[type=radio], input[type=checkbox]")) form.requestSubmit();
});

// Player embutido (add-player-embutido D2, revisao-final D2): cada iframe fica num <template> inerte e só é criado
// no clique, então abrir o resultado não faz requisição a YouTube ou Spotify. Um player por vez: com dois serviços,
// o seletor troca o player; "Fechar player" esvazia o bloco. Sem JS o bloco fica escondido e sobram os links de abrir.
function iniciarPlayer() {
  const bloco = document.querySelector("[data-ouvir-bloco]");
  if (!bloco) return;
  bloco.hidden = false;
  const botoes = [...bloco.querySelectorAll("[data-ouvir]")];
  const player = bloco.querySelector("[data-player]");
  const fechar = bloco.querySelector("[data-fechar-player]");
  const anuncio = bloco.querySelector("[data-anuncio-player]");
  const seletor = botoes[0].hasAttribute("aria-pressed");
  const marcar = (escolhido) => {
    for (const b of botoes) {
      if (seletor) b.setAttribute("aria-pressed", String(b === escolhido));
      else b.hidden = b === escolhido; // botão simples some enquanto o player está aberto
    }
    fechar.hidden = escolhido === null;
  };
  for (const botao of botoes) {
    botao.addEventListener("click", () => {
      if (botao.getAttribute("aria-pressed") === "true") return;
      player.replaceChildren(document.querySelector(`[data-player-modelo="${botao.dataset.ouvir}"]`).content.cloneNode(true));
      marcar(botao);
      anuncio.textContent = `${player.querySelector("iframe").title.split(":")[0]} aberto.`;
      (seletor ? botao : fechar).focus(); // o foco não entra no iframe de terceiros
    });
  }
  fechar.addEventListener("click", () => {
    player.replaceChildren();
    marcar(null);
    anuncio.textContent = "Player fechado.";
    botoes[0].focus();
  });
}

// Formulário que voltou com erro: foco no primeiro campo inválido, que é o próximo passo de quem preenche.
document.querySelector('[aria-invalid="true"]')?.focus();

iniciarToasts();
iniciarRoleta();
iniciarPlayer();
