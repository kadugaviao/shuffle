"""Contraste WCAG AA das cores do design system "Lambe-lambe", lidas direto do :root do style.css (design D4)."""

import re
import unittest
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "shuffle_meu" / "static" / "style.css"

# (texto, fundo): pares usados em texto de qualquer tamanho
NORMAL = [("tinta", "papel"), ("tinta", "papel-2"), ("tinta-2", "papel"), ("tinta-2", "papel-2"),
          ("tinta", "amarelo"), ("tinta-2", "amarelo"), ("papel", "tinta"), ("amarelo", "tinta"),
          ("vermelho-texto", "papel"), ("vermelho-texto", "papel-2")]
# pares que o design só permite em texto grande (24 px, ou 18,66 px em negrito)
GRANDE = [("papel", "vermelho"), ("vermelho", "papel"), ("sucesso", "papel"), ("tinta", "vermelho")]


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


class TestContraste(unittest.TestCase):
    def setUp(self):
        self.t = tokens(CSS.read_text(encoding="utf-8"))

    def test_texto_normal(self):
        for texto, fundo in NORMAL:
            with self.subTest(texto=texto, fundo=fundo):
                self.assertGreaterEqual(contraste(self.t[texto], self.t[fundo]), 4.5)

    def test_texto_grande(self):
        for texto, fundo in GRANDE:
            with self.subTest(texto=texto, fundo=fundo):
                self.assertGreaterEqual(contraste(self.t[texto], self.t[fundo]), 3)

    def test_vermelho_e_sucesso_nao_passam_pequenos_e_por_isso_sao_restritos(self):
        # Documenta D4: vermelho e sucesso como texto pequeno reprovam; daí o --vermelho-texto.
        self.assertLess(contraste(self.t["vermelho"], self.t["papel"]), 4.5)
        self.assertLess(contraste(self.t["sucesso"], self.t["papel"]), 4.5)

    def test_amarelo_nunca_e_texto_sobre_papel(self):
        self.assertLess(contraste(self.t["amarelo"], self.t["papel"]), 3)
