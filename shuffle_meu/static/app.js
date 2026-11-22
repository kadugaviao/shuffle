// Pede confirmação antes de enviar formulários marcados com data-confirmar (exclusões).
document.addEventListener("submit", (evento) => {
  const mensagem = evento.target.dataset.confirmar;
  if (mensagem && !confirm(mensagem)) evento.preventDefault();
});
