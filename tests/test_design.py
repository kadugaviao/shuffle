import unittest
import zlib

from shuffle_meu import decimal1, iniciais, matiz
from shuffle_meu.musicas import rotulo_genero
from tests.base import BaseTest

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
        self.assertIn('style="--h: 312"', html)
        self.assertIn('aria-label="Dificuldade 3 de 5"', html)
        self.assertEqual(html.count('class="cheia"'), 3)
