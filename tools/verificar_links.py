"""Verifica no Chrome se links do YouTube e do Spotify tocam no player embutido do Shuffle.

Uso (precisa de internet e do Google Chrome; não faz parte da suíte de testes):

    python tools/verificar_links.py https://youtu.be/<ID> https://open.spotify.com/track/<ID>
    python tools/verificar_links.py --arquivo links.txt     # um link por linha; linhas com # são ignoradas

Para cada link, monta o embed com as mesmas regras e atributos do app (shuffle_meu.links), abre-o dentro de uma
página local em 127.0.0.1 e lê o texto que aparece dentro do player. Imprime OK ou FALHA, o serviço, o ID e o
texto lido (título e canal ou artista) para conferir com a música esperada. Sai com código 1 se algum falhar.

O Chrome é controlado pelo DevTools Protocol via --remote-debugging-pipe (descritores 3 e 4, mensagens JSON
terminadas em \\0), então não há dependência além da biblioteca padrão.
"""

import argparse
import html
import json
import os
import select
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shuffle_meu.links import players  # noqa: E402  (mesmas regras do app)

ERROS_YOUTUBE = ("video unavailable", "this video is unavailable", "vídeo indisponível", "error 15",
                 "configuration error", "playback on other websites has been disabled")
ERROS_SPOTIFY = ("page not found", "something went wrong", "not available", "indisponível",
                 "request timeout", "upstream", "error")  # páginas de erro do próprio Spotify
ESPERA = 9  # segundos para o player carregar


class Pagina(BaseHTTPRequestHandler):
    """Página mínima com o iframe do player, igual ao do app (src montado pelo app, mesmos atributos)."""

    def do_GET(self):
        src = (parse_qs(urlsplit(self.path).query).get("src") or [""])[0]
        corpo = (f'<!doctype html><meta charset="utf-8"><iframe src="{html.escape(src)}" width="640" height="360" '
                 'allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen '
                 'referrerpolicy="strict-origin-when-cross-origin"></iframe>').encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, format, *args):  # silencioso: o relatório é a saída
        pass


class Chrome:
    """Chrome headless controlado pelo DevTools Protocol num par de pipes."""

    def __init__(self):
        self.perfil = tempfile.mkdtemp(prefix="verificar-links-")
        para_chrome, self._escrita = os.pipe()
        self._leitura, do_chrome = os.pipe()

        def ligar_pipes():  # no processo filho: o Chrome lê comandos no fd 3 e escreve respostas no fd 4
            a, b = os.dup(para_chrome), os.dup(do_chrome)
            os.dup2(a, 3)
            os.dup2(b, 4)

        executavel = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
        if not executavel:
            sys.exit("Chrome não encontrado (google-chrome, chromium ou chromium-browser).")
        self.processo = subprocess.Popen(
            [executavel, "--headless=new", "--remote-debugging-pipe", "--no-first-run", "--mute-audio",
             f"--user-data-dir={self.perfil}", "about:blank"],
            preexec_fn=ligar_pipes, close_fds=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.close(para_chrome)
        os.close(do_chrome)
        self._id = 0
        self._buffer = b""
        self.eventos = []

    def _receber(self, prazo):
        while b"\0" not in self._buffer:
            restante = prazo - time.monotonic()
            if restante <= 0 or not select.select([self._leitura], [], [], restante)[0]:
                return None
            bloco = os.read(self._leitura, 65536)
            if not bloco:
                return None
            self._buffer += bloco
        mensagem, self._buffer = self._buffer.split(b"\0", 1)
        return json.loads(mensagem)

    def comando(self, metodo, params=None, sessao=None, timeout=15):
        self._id += 1
        pedido = {"id": self._id, "method": metodo, "params": params or {}}
        if sessao:
            pedido["sessionId"] = sessao
        os.write(self._escrita, json.dumps(pedido).encode() + b"\0")
        prazo = time.monotonic() + timeout
        while (resposta := self._receber(prazo)) is not None:
            if resposta.get("id") == self._id:
                return resposta.get("result", {})
            self.eventos.append(resposta)
        raise TimeoutError(metodo)

    def esperar(self, segundos):
        prazo = time.monotonic() + segundos
        while (evento := self._receber(prazo)) is not None:
            self.eventos.append(evento)

    def fechar(self):
        self.processo.terminate()
        try:
            self.processo.wait(5)
        except subprocess.TimeoutExpired:
            self.processo.kill()
        shutil.rmtree(self.perfil, ignore_errors=True)


def texto_do_player(chrome, url):
    """Abre a página local e devolve o texto visível dentro do iframe do player ('' se não carregou)."""
    alvo = chrome.comando("Target.createTarget", {"url": "about:blank"})["targetId"]
    sessao = chrome.comando("Target.attachToTarget", {"targetId": alvo, "flatten": True})["sessionId"]
    chrome.comando("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": False, "flatten": True}, sessao)
    chrome.eventos.clear()
    chrome.comando("Page.navigate", {"url": url}, sessao)
    chrome.esperar(ESPERA)
    texto = ""
    for evento in chrome.eventos:
        if evento.get("method") == "Target.attachedToTarget" and evento["params"]["targetInfo"]["type"] == "iframe":
            resultado = chrome.comando("Runtime.evaluate", {
                "expression": "document.body ? document.body.innerText.replace(/\\s+/g, ' ').trim() : ''",
                "returnByValue": True}, evento["params"]["sessionId"])
            texto = resultado.get("result", {}).get("value") or texto
    chrome.comando("Target.closeTarget", {"targetId": alvo})
    return texto


def main():
    argumentos = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    argumentos.add_argument("links", nargs="*")
    argumentos.add_argument("--arquivo", type=Path)
    opcoes = argumentos.parse_args()
    links = list(opcoes.links)
    if opcoes.arquivo:
        links += [l.strip() for l in opcoes.arquivo.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    if not links:
        argumentos.error("informe ao menos um link")

    servidor = ThreadingHTTPServer(("127.0.0.1", 0), Pagina)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{servidor.server_address[1]}/?src="
    chrome = Chrome()
    falhas = 0
    try:
        for link in links:
            encontrados = players(link, None) or players(None, link)
            if not encontrados:
                print(f"FALHA  -        -            {link}  (link não reconhecido como vídeo do YouTube nem faixa do Spotify)", flush=True)
                falhas += 1
                continue
            player = encontrados[0]
            id_ = player["src"].split("/")[-1].split("?")[0]
            texto = texto_do_player(chrome, base + player["src"])
            erros = ERROS_YOUTUBE if player["chave"] == "youtube" else ERROS_SPOTIFY
            ok = bool(texto) and not any(e in texto.lower() for e in erros)
            falhas += not ok
            print(f"{'OK   ' if ok else 'FALHA'}  {player['servico']:<7}  {id_:<22}  {texto[:110] or '(player não carregou)'}", flush=True)
    finally:
        chrome.fechar()
        servidor.shutdown()
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
