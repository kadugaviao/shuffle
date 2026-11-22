import unittest

from shuffle_meu import create_app
from shuffle_meu.musicas import validar_musica
from tests.base import BaseTest


def form(**campos):
    base = {"titulo": "Tempo Perdido", "artista_id": "1", "dificuldade": "3"}
    return {**base, **campos}


class TestValidarMusica(unittest.TestCase):
    def erros(self, **campos):
        return validar_musica(form(**campos))[1]

    def test_valido(self):
        dados, erros = validar_musica(form(titulo="  Tempo Perdido ", genero="", link=""))
        self.assertEqual(erros, [])
        self.assertEqual(dados["titulo"], "Tempo Perdido")
        self.assertIsNone(dados["genero"])  # vazio vira NULL para o CHECK do banco
        self.assertIsNone(dados["link"])

    def test_titulo_obrigatorio_rn01(self):
        self.assertIn("Informe o título da música.", self.erros(titulo="   "))

    def test_artista_obrigatorio_rn01(self):
        self.assertIn("Escolha o artista da música.", self.erros(artista_id=""))

    def test_dificuldade_rn03(self):
        for valor in ("0", "6", "abc", ""):
            self.assertIn("A dificuldade deve ser um número de 1 a 5.", self.erros(dificuldade=valor))
        for valor in ("1", "5"):
            self.assertEqual(self.erros(dificuldade=valor), [])

    def test_humor_da_lista(self):
        self.assertIn("Escolha um humor da lista.", self.erros(humor="eufórica"))
        self.assertEqual(self.erros(humor="romantica"), [])

    def test_link_seguro(self):
        self.assertIn("O link deve começar com http:// ou https://.", self.erros(link="javascript:alert(1)"))
        self.assertEqual(self.erros(link="https://www.youtube.com/watch?v=abc"), [])


class TestMusicas(BaseTest):
    def setUp(self):
        super().setUp()
        self.legiao = self.artista("Legião Urbana")

    def test_cadastro_valido(self):
        r = self.client.post("/musicas/nova", follow_redirects=True, data=form(
            artista_id=str(self.legiao), genero="rock", humor="calma", dificuldade="2"))
        self.assertIn("Música cadastrada.", self.texto(r))
        m = self.sql("SELECT * FROM musica")[0]
        self.assertEqual((m["titulo"], m["ativa"], m["favorita"], m["dificuldade"]), ("Tempo Perdido", 1, 0, 2))

    def test_nova_vem_com_dificuldade_3(self):
        self.assertIn('<option value="3" selected>', self.texto(self.client.get("/musicas/nova")))

    def test_erro_mantem_dados_digitados(self):
        r = self.client.post("/musicas/nova", data=form(artista_id=str(self.legiao), dificuldade="9",
                                                        genero="rock progressivo"))
        self.assertIn('value="Tempo Perdido"', self.texto(r))
        self.assertIn('value="rock progressivo"', self.texto(r))
        self.assertEqual(self.um("SELECT COUNT(*) FROM musica"), 0)

    def test_artista_inexistente(self):
        r = self.client.post("/musicas/nova", data=form(artista_id="999"))
        self.assertIn("Escolha o artista da música.", self.texto(r))

    def test_duplicata_rejeitada_rn02(self):
        self.musica("Tempo Perdido", self.legiao)
        r = self.client.post("/musicas/nova", data=form(titulo="TEMPO PERDIDO", artista_id=str(self.legiao)))
        self.assertIn("Essa música já está cadastrada para esse artista.", self.texto(r))
        outra = self.musica("Índios", self.legiao)
        r = self.client.post(f"/musicas/{outra}/editar", data=form(titulo="tempo perdido",
                                                                    artista_id=str(self.legiao)))
        self.assertIn("Essa música já está cadastrada para esse artista.", self.texto(r))
        self.assertEqual(self.um("SELECT titulo FROM musica WHERE id = ?", (outra,)), "Índios")

    def test_mesmo_titulo_outro_artista(self):
        cohen = self.artista("Leonard Cohen")
        buckley = self.artista("Jeff Buckley")
        self.musica("Hallelujah", cohen)
        self.client.post("/musicas/nova", data=form(titulo="Hallelujah", artista_id=str(buckley)))
        self.assertEqual(self.um("SELECT COUNT(*) FROM musica WHERE titulo = 'Hallelujah'"), 2)

    def test_busca_por_artista(self):
        djavan = self.artista("Djavan")
        self.musica("Tempo Perdido", self.legiao)
        self.musica("Índios", self.legiao)
        self.musica("Oceano", djavan)
        html = self.texto(self.client.get("/musicas?q=LEGIÃO"))
        self.assertIn("Índios", html)
        self.assertIn("Tempo Perdido", html)
        self.assertNotIn("Oceano", html)
        self.assertLess(html.index("Índios"), html.index("Tempo Perdido"))

    def test_filtros_combinados(self):
        self.musica("Tempo Perdido", self.legiao, genero="rock", favorita=1)
        self.musica("Índios", self.legiao, genero="rock")
        self.musica("Oceano", self.legiao, genero="MPB", favorita=1)
        html = self.texto(self.client.get("/musicas?genero=Rock&favorita=1"))
        self.assertIn("Tempo Perdido", html)
        self.assertNotIn(">Índios</a>", html)
        self.assertNotIn(">Oceano</a>", html)

    def test_nada_encontrado(self):
        self.musica("Tempo Perdido", self.legiao)
        self.assertIn("Nenhuma música encontrada.", self.texto(self.client.get("/musicas?q=xyz")))

    def test_marcar_favorita_e_desativar(self):
        m = self.musica("Tempo Perdido", self.legiao)
        self.client.post(f"/musicas/{m}/editar", data=form(artista_id=str(self.legiao), favorita="1"))
        linha = self.sql("SELECT favorita, ativa FROM musica")[0]
        self.assertEqual(tuple(linha), (1, 0))
        self.assertIn('class="musica-cartao inativa"', self.texto(self.client.get("/musicas")))

    def test_edicao_invalida(self):
        m = self.musica("Tempo Perdido", self.legiao, dificuldade=2)
        r = self.client.post(f"/musicas/{m}/editar", data=form(artista_id=str(self.legiao), dificuldade="7"))
        self.assertIn("A dificuldade deve ser um número de 1 a 5.", self.texto(r))
        self.assertEqual(self.um("SELECT dificuldade FROM musica"), 2)

    def test_editar_inexistente_404(self):
        self.assertEqual(self.client.get("/musicas/999/editar").status_code, 404)

    def test_exclusao_remove_historico_e_vinculos_rn08(self):
        m = self.musica("Tempo Perdido", self.legiao)
        for _ in range(3):
            self.sorteio(m)
        p = self.inserir("INSERT INTO playlist (nome) VALUES ('Roda de violão')")
        self.inserir("INSERT INTO playlist_musica VALUES (?, ?)", (p, m))
        self.client.post(f"/musicas/{m}/excluir")
        self.assertEqual(self.um("SELECT COUNT(*) FROM musica"), 0)
        self.assertEqual(self.um("SELECT COUNT(*) FROM sorteio"), 0)
        self.assertEqual(self.um("SELECT COUNT(*) FROM playlist_musica"), 0)
        self.assertEqual(self.um("SELECT COUNT(*) FROM playlist"), 1)

    def test_persistencia_apos_reinicio(self):
        self.client.post("/musicas/nova", data=form(artista_id=str(self.legiao)))
        reiniciado = create_app({"TESTING": True, "DATABASE": self.caminho}).test_client()
        self.assertIn("Tempo Perdido", self.texto(reiniciado.get("/musicas")))


class TestAtalhos(BaseTest):
    def setUp(self):
        super().setUp()
        self.tempo = self.musica("Tempo Perdido", genero="rock")

    def valor(self, coluna):
        return self.um(f"SELECT {coluna} FROM musica WHERE id = ?", (self.tempo,))

    def test_marcar_favorita_mantem_filtros_e_posicao(self):
        r = self.client.post(f"/musicas/{self.tempo}/favorita?genero=rock", data={"valor": "1"})
        self.assertEqual(self.valor("favorita"), 1)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.headers["Location"], f"/musicas?genero=rock#musica-{self.tempo}")

    def test_desativar(self):
        self.client.post(f"/musicas/{self.tempo}/ativa", data={"valor": "0"})
        self.assertEqual(self.valor("ativa"), 0)
        self.assertIn("Nenhuma música encontrada", self.texto(self.client.post("/sortear", follow_redirects=True)))

    def test_clique_repetido_nao_desfaz(self):
        for _ in range(2):
            self.client.post(f"/musicas/{self.tempo}/favorita", data={"valor": "1"})
        self.assertEqual(self.valor("favorita"), 1)

    def test_musica_inexistente_e_valor_invalido(self):
        self.assertEqual(self.client.post("/musicas/999/favorita", data={"valor": "1"}).status_code, 404)
        self.assertEqual(self.client.post(f"/musicas/{self.tempo}/ativa", data={"valor": "2"}).status_code, 400)
        self.assertEqual(self.client.post(f"/musicas/{self.tempo}/ativa").status_code, 400)
        self.assertEqual(self.valor("ativa"), 1)

    def test_query_estranha_nao_quebra(self):
        r = self.client.post(f"/musicas/{self.tempo}/favorita?id=7&x=1", data={"valor": "1"})
        self.assertEqual(r.headers["Location"], f"/musicas#musica-{self.tempo}")
        self.assertEqual(self.client.get("/musicas?id=7").status_code, 200)

    def test_cartao_tem_atalhos_acessiveis(self):
        html = self.texto(self.client.get("/musicas?genero=rock"))
        self.assertIn('aria-pressed="false" aria-label="Favorita: Tempo Perdido"', html)
        self.assertIn('role="switch" aria-checked="true" aria-label="Ativa: Tempo Perdido"', html)
        self.assertIn(f'action="/musicas/{self.tempo}/favorita?genero=rock"', html)
