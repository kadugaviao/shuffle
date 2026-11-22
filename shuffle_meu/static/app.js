// Shuffle: melhorias progressivas. Tudo funciona sem este arquivo; aqui só entram animação e atalhos.
const movimentoReduzido = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

// Confirmação antes de enviar formulários marcados com data-confirmar (exclusões).
document.addEventListener("submit", (evento) => {
  const mensagem = evento.target.dataset.confirmar;
  if (mensagem && !confirm(mensagem)) evento.preventDefault();
});

// Toasts: sucesso some em 5 s (pausa com hover/foco); erro e aviso ficam até fechar.
function iniciarToasts() {
  for (const toast of document.querySelectorAll(".toast")) {
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

// Pop (0,96 → 1,04 → 1) ao clicar em botões marcados com data-pop, como o "Sortear".
document.addEventListener("click", (evento) => {
  const botao = evento.target.closest("[data-pop]");
  if (!botao || movimentoReduzido()) return;
  botao.classList.remove("pop");
  void botao.offsetWidth; // reinicia a animação em cliques seguidos
  botao.classList.add("pop");
});

// Roleta (D4): títulos passam e desaceleram até a música sorteada, ~1,2 s. Só existe logo após sortear.
function iniciarRoleta() {
  const cartao = document.querySelector("[data-roleta]");
  if (!cartao || movimentoReduzido()) return; // com movimento reduzido o CSS já mostra o resultado
  const titulos = JSON.parse(cartao.dataset.roleta);
  const rolo = cartao.querySelector(".rolo");
  const passos = 14;
  const atrasos = Array.from({ length: passos }, (_, k) => 30 + 150 * (k / (passos - 1)) ** 2); // ~1,15 s no total
  let i = 0;
  cartao.classList.add("rodando");
  const passo = () => {
    const ultimo = i === passos - 1;
    rolo.textContent = ultimo ? titulos.at(-1) : titulos[i % Math.max(titulos.length - 1, 1)];
    rolo.classList.remove("tique");
    void rolo.offsetWidth;
    rolo.classList.add("tique");
    if (!ultimo) {
      setTimeout(passo, atrasos[++i]);
      return;
    }
    setTimeout(() => {
      cartao.classList.replace("rodando", "revelado");
      cartao.querySelector("[data-anuncio]").textContent =
        `Sorteada: ${cartao.querySelector(".titulo-sorteado").textContent}, ${cartao.querySelector(".artista").textContent}`;
    }, 140);
  };
  passo();
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
  if (interruptor) form.closest(".musica-cartao")?.classList.toggle("inativa", !ligado);
  if (!movimentoReduzido()) {
    botao.classList.remove("pop");
    void botao.offsetWidth;
    botao.classList.add("pop");
  }
});

// Filtros do Repertório: chips e "Só favoritas" aplicam na hora (o botão Filtrar fica para quem não tem JS).
document.addEventListener("change", (evento) => {
  const form = evento.target.closest("form[data-auto-enviar]");
  if (form && evento.target.matches("input[type=radio], input[type=checkbox]")) form.requestSubmit();
});

iniciarToasts();
iniciarRoleta();
