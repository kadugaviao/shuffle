"""Contraste WCAG AA das cores de texto do design system, lidas direto do :root do style.css."""

import re
import unittest
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "shuffle_meu" / "static" / "style.css"


def tokens(css):
    raiz = re.search(r":root\s*\{(.*?)\n\}", css, re.S).group(1)
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})\b", raiz))


def luminancia(hexa):
    canais = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contraste(a, b):
    claro, escuro = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


def sobre(fundo, alfa=0.04, cor="#FFFFFF"):
    """Cor efetiva de rgba(cor, alfa) sobre o fundo (a superfície translúcida dos cartões)."""
    return "#" + "".join(
        f"{round(int(cor[i:i + 2], 16) * alfa + int(fundo[i:i + 2], 16) * (1 - alfa)):02X}" for i in (1, 3, 5)
    )


class TestContraste(unittest.TestCase):
    def setUp(self):
        self.t = tokens(CSS.read_text(encoding="utf-8"))

    def test_texto_sobre_fundo_e_superficie(self):
        fundos = {"fundo": self.t["fundo"], "superficie": sobre(self.t["fundo"])}
        for texto in ("texto", "texto-2", "perigo", "sucesso", "aviso"):
            for nome, fundo in fundos.items():
                with self.subTest(texto=texto, fundo=nome):
                    self.assertGreaterEqual(contraste(self.t[texto], fundo), 4.5)

    def test_texto_sobre_o_gradiente(self):
        for parada in ("violeta", "rosa", "ambar"):
            with self.subTest(parada=parada):
                self.assertGreaterEqual(contraste(self.t["texto-sobre-gradiente"], self.t[parada]), 4.5)

    def test_apagado_nao_passa_e_por_isso_e_restrito(self):
        # Documenta a regra do design system: --texto-apagado só em desabilitados e decoração.
        self.assertLess(contraste(self.t["texto-apagado"], self.t["fundo"]), 4.5)

