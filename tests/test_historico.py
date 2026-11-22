from tests.base import BaseTest


class TestHistorico(BaseTest):
    def test_novo_registro(self):
        self.musica("Tempo Perdido")
        r = self.client.post("/sortear")
        s = self.sql("SELECT * FROM sorteio")
        self.assertEqual(len(s), 1)
        self.assertEqual(s[0]["tocada"], 0)
        self.assertTrue(r.headers["Location"].startswith(f"/sorteios/{s[0]['id']}"))

    def test_recarregar_resultado_nao_cria_sorteio(self):
        self.musica("Tempo Perdido")
        url = self.client.post("/sortear").headers["Location"]
        self.client.get(url)
        self.client.get(url)
        self.assertEqual(self.um("SELECT COUNT(*) FROM sorteio"), 1)

    def test_toquei(self):
        s = self.sorteio(self.musica("Tempo Perdido"))
        r = self.client.post(f"/sorteios/{s}/toquei", follow_redirects=True)
        self.assertEqual(self.um("SELECT tocada FROM sorteio"), 1)
        html = self.texto(r)
        self.assertIn("Tocada</p>", html)
        self.assertNotIn("Toquei ✅", html)
        self.assertEqual(html.count('name="nota" value='), 5)  # as estrelas aparecem
        self.assertIn('class="estrelas entrando"', html)  # com o pop de entrada, só logo após o Toquei
        self.assertNotIn("entrando", self.texto(self.client.get(f"/sorteios/{s}")))

    def test_estrelas_escondidas_antes_de_tocar(self):
        s = self.sorteio(self.musica("Tempo Perdido"))
        html = self.texto(self.client.get(f"/sorteios/{s}"))
        self.assertNotIn('name="nota"', html)
        self.assertIn("Toquei ✅", html)

    def test_estrelas_mostram_a_nota_atual(self):
        s = self.sorteio(self.musica("Tempo Perdido"), tocada=1, nota=3)
        html = self.texto(self.client.get(f"/sorteios/{s}"))
        self.assertEqual(html.count('class="estrela acesa"'), 3)
        self.assertIn('aria-label="Dar nota 3 de 5" aria-pressed="true"', html)
        self.assertEqual(html.count('aria-pressed="true"'), 1)

    def test_avaliar_musica_tocada_rn07(self):
        s = self.sorteio(self.musica("Tempo Perdido"), tocada=1)
        self.client.post(f"/sorteios/{s}/avaliar", data={"nota": "3"})
        self.client.post(f"/sorteios/{s}/avaliar", data={"nota": "5"})  # avaliar de novo substitui
        self.assertEqual(self.um("SELECT nota FROM sorteio"), 5)

    def test_avaliar_sem_ter_tocado_rn07(self):
        s = self.sorteio(self.musica("Tempo Perdido"))
        r = self.client.post(f"/sorteios/{s}/avaliar", data={"nota": "4"}, follow_redirects=True)
        self.assertIn("Marque como tocada antes de avaliar.", self.texto(r))
        self.assertIsNone(self.um("SELECT nota FROM sorteio"))

    def test_nota_fora_da_faixa(self):
        s = self.sorteio(self.musica("Tempo Perdido"), tocada=1)
        for nota in ("0", "6", "abc"):
            r = self.client.post(f"/sorteios/{s}/avaliar", data={"nota": nota}, follow_redirects=True)
            self.assertIn("A nota deve ser de 1 a 5.", self.texto(r))
        self.assertIsNone(self.um("SELECT nota FROM sorteio"))

    def test_toquei_com_query_estranha_nao_quebra(self):
        s = self.sorteio(self.musica("Tempo Perdido"))
        r = self.client.post(f"/sorteios/{s}/toquei?id=9&humor=calma")
        self.assertEqual(r.status_code, 302)
        self.assertIn("humor=calma", r.headers["Location"])

    def test_toquei_inexistente_404(self):
        self.assertEqual(self.client.post("/sorteios/999/toquei").status_code, 404)

    def test_pular(self):
        self.musica("Tempo Perdido", humor="calma")
        self.musica("Oceano", humor="calma")
        self.musica("Índios", humor="animada")
        url = self.client.post("/sortear", data={"humor": "calma", "n": "5"}).headers["Location"]
        html = self.texto(self.client.get(url))
        # o botão Pular reenvia os mesmos filtros e o mesmo N
        self.assertIn('<input type="hidden" name="humor" value="calma">', html)
        self.assertIn('<input type="hidden" name="n" value="5">', html)
        self.client.post("/sortear", data={"humor": "calma", "n": "5"})
        primeiro, segundo = self.sql(
            "SELECT s.tocada, m.titulo, m.humor FROM sorteio s JOIN musica m ON m.id = s.musica_id ORDER BY s.id")
        self.assertEqual(primeiro["tocada"], 0)
        self.assertNotEqual(primeiro["titulo"], segundo["titulo"])
        self.assertEqual(segundo["humor"], "calma")

    def test_ordem_e_conteudo(self):
        oceano = self.musica("Oceano")
        tempo = self.musica("Tempo Perdido")
        self.sorteio(oceano, sorteado_em="2026-11-22 23:00:00")
        self.sorteio(tempo, sorteado_em="2026-11-22 23:05:00", tocada=1, nota=4)
        html = self.texto(self.client.get("/historico"))
        self.assertLess(html.index("Tempo Perdido"), html.index("Oceano"))
        self.assertIn("Tocada · nota 4", html)
        self.assertIn("Não tocada", html)
        self.assertIn(f'href="/sorteios/{1}"', html)

    def test_historico_vazio(self):
        self.assertIn("Nenhum sorteio ainda.", self.texto(self.client.get("/historico")))
        self.assertIn("Que tal sortear agora?", self.texto(self.client.get("/historico")))

    def test_ultima_sorteada_na_inicial(self):
        self.sorteio(self.musica("Tempo Perdido"))
        self.assertIn("Última sorteada: Tempo Perdido — Legião Urbana", self.texto(self.client.get("/")))

    def test_exclusao_da_musica_rn08(self):
        oceano = self.musica("Oceano")
        tempo = self.musica("Tempo Perdido")
        self.sorteio(oceano)
        self.sorteio(oceano)
        self.client.post(f"/musicas/{oceano}/excluir")
        self.assertNotIn("Oceano", self.texto(self.client.get("/historico")))
        # sem os sorteios de Oceano, Tempo Perdido é a única e não há bloqueio: nenhum aviso RN06
        url = self.client.post("/sortear", data={"n": "5"}).headers["Location"]
        self.assertNotIn("Você já tocou todas recentemente!", self.texto(self.client.get(url)))
        self.assertEqual(self.um("SELECT musica_id FROM sorteio"), tempo)
