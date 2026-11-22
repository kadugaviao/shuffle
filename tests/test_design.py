import re
import unittest
import zlib
from pathlib import Path

from shuffle_meu import decimal1, iniciais, matiz
from shuffle_meu.musicas import rotulo_genero
from tests.base import BaseTest

PACOTE = Path(__file__).resolve().parent.parent / "shuffle_meu"
FAMILIAS = {"Big Shoulders Display", "Archivo", "IBM Plex Mono"}

ICONES = ("dado", "shuffle", "musica", "microfone", "lista", "historico", "coracao", "estrela", "check", "pular",
          "fechar", "mais", "lapis", "lixeira", "busca", "link", "alerta", "grafico")


class TestFiltros(unittest.TestCase):
    def test_matiz_estavel(self):
        self.assertEqual(matiz("Djavan"), zlib.crc32("Djavan".encode()) % 360)
        self.assertEqual(matiz("Djavan"), 312)  # valor fixo: muda só se o algoritmo mudar
        self.assertTrue(0 <= matiz("") < 360)

    def test_iniciais(self):
        self.assertEqual(iniciais("Chitãozinho & Xororó"), "CX")
        self.assertEqual(iniciais("Djavan"), "D")
        self.assertEqual(iniciais("The Beatles"), "TB")
        self.assertEqual(iniciais(""), "")

    def test_rotulo_genero(self):
        self.assertEqual([rotulo_genero(g) for g in ("pop", "rock", "MPB", "samba", "sertanejo")],
                         ["Pop", "Rock", "MPB", "Samba", "Sertanejo"])
        self.assertEqual(rotulo_genero("rock progressivo"), "Rock progressivo")
        self.assertEqual(rotulo_genero(None), "")

    def test_decimal1(self):
        self.assertEqual(decimal1(4.25), "4,3")
        self.assertEqual(decimal1(14 / 3), "4,7")
        self.assertEqual(decimal1(5), "5,0")
        self.assertEqual(decimal1(None), "—")


class TestMacros(BaseTest):
    def render(self, fonte, **ctx):
        with self.app.test_request_context():
            return self.app.jinja_env.from_string(fonte).render(**ctx)

    def test_todos_os_icones(self):
        for nome in ICONES:
            with self.subTest(nome=nome):
                svg = self.render('{% from "_icones.html" import icone %}{{ icone(n) }}', n=nome)
                self.assertIn('<svg class="icone', svg)
                self.assertIn('stroke-width="1.5"', svg)
                self.assertIn('aria-hidden="true"', svg)
                self.assertRegex(svg, r"<(path|rect|circle|polygon|line)")

    def test_campo_com_erro(self):
        html = self.render(
            '{% from "_macros.html" import campo, aria %}'
            '{% call campo("titulo", "Título", erros) %}<input name="titulo" {{ aria("titulo", erros) }}>{% endcall %}',
            erros={"titulo": "Informe o título da música."},
        )
        self.assertIn('<label for="campo-titulo">Título</label>', html)
        self.assertIn('id="campo-titulo" aria-invalid="true" aria-describedby="erro-titulo"', html)
        self.assertIn('id="erro-titulo"', html)
        self.assertLess(html.index("<input"), html.index("Informe o título da música."))

    def test_chips_marca_o_atual_sem_diferenciar_maiusculas(self):
        html = self.render('{% from "_macros.html" import chips %}{{ chips("genero", "Gênero", ops, "Rock", "Todos") }}',
                           ops=[("rock", "rock"), ("MPB", "MPB")])
        self.assertIn('value="rock" checked', html)
        self.assertNotIn('value="" checked', html)

    def test_capa_e_dificuldade(self):
        html = self.render('{% from "_macros.html" import capa, dificuldade %}{{ capa("Djavan") }}{{ dificuldade(3) }}')
        self.assertIn('class="capa capa-0"', html)  # Djavan: matiz 312, 312 % 3 = 0 (amarelo)
        self.assertIn('aria-label="Dificuldade 3 de 5"', html)
        self.assertEqual(html.count('class="cheia"'), 3)


class TestAntiSlop(unittest.TestCase):
    """Proibições da seção "Anti-slop" do design.md conferidas no CSS (design D11)."""

    def setUp(self):
        css = (PACOTE / "static" / "style.css").read_text(encoding="utf-8")
        self.css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)  # comentários podem citar o que é proibido

    def test_sem_gradiente_vidro_nem_blur(self):
        for proibido in ("gradient(", "backdrop-filter", "blur(", "text-shadow"):
            with self.subTest(proibido=proibido):
                self.assertNotIn(proibido, self.css)

    def test_sem_preto_puro(self):
        self.assertIsNone(re.search(r"#000(000)?\b|\bblack\b", self.css, re.I))

    def test_easing_sem_repique(self):
        for valores in re.findall(r"cubic-bezier\(([^)]*)\)", self.css):
            _, y1, _, y2 = (float(v) for v in valores.split(","))
            with self.subTest(curva=valores):
                self.assertTrue(0 <= y1 <= 1 and 0 <= y2 <= 1)

    def test_raio_maximo_4px(self):
        for valor in re.findall(r"border-radius:\s*([^;]+);", self.css):
            with self.subTest(valor=valor):
                self.assertIn(valor.strip(), ("0", "4px", "var(--raio-controle)"))

    def test_uma_sombra_so(self):
        sombras = {v.strip() for v in re.findall(r"box-shadow:\s*([^;]+);", self.css)} - {"none"}
        self.assertEqual(sombras, {"var(--impressao)"})

    def test_so_as_tres_familias(self):
        self.assertEqual(set(re.findall(r'font-family:\s*"([^"]+)"', self.css)), FAMILIAS)
        for antiga in ("Inter", "Geist", "Instrument"):
            self.assertNotIn(antiga, self.css)

    def test_templates_sem_emoji(self):
        emoji = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u23E9-\u23FA\uFE0F]")
        for template in (PACOTE / "templates").rglob("*.html"):
            with self.subTest(template=template.name):
                self.assertIsNone(emoji.search(template.read_text(encoding="utf-8")))

    def test_pasta_de_fontes(self):
        arquivos = {f.name for f in (PACOTE / "static" / "fonts").iterdir()}
        for nome in arquivos:
            with self.subTest(arquivo=nome):
                self.assertRegex(nome, r"^(big-shoulders-display|archivo|ibm-plex-mono|OFL-(big-shoulders-display|archivo|ibm-plex-mono))")
        for fonte in re.findall(r'url\("fonts/([^"]+)"\)', self.css):
            self.assertIn(fonte, arquivos)
