from tests.base import BaseTest


class TestArtistas(BaseTest):
    def test_listar_em_ordem_com_contagem(self):
        legiao = self.artista("Legião Urbana")
        djavan = self.artista("Djavan")
        self.musica("Tempo Perdido", legiao)
        self.musica("Índios", legiao)
        self.musica("Oceano", djavan)
        html = self.texto(self.client.get("/artistas"))
        self.assertLess(html.index("Djavan"), html.index("Legião Urbana"))
        self.assertIn('<span class="numero">1</span> música<', html)
        self.assertIn('<span class="numero">2</span> músicas<', html)

    def test_lista_vazia(self):
        self.assertIn("Nenhum artista cadastrado ainda.", self.texto(self.client.get("/artistas")))

    def test_cadastro_valido(self):
        r = self.client.post("/artistas/novo", data={"nome": "  Legião Urbana ", "pais": "Brasil"},
                             follow_redirects=True)
        self.assertIn("Artista cadastrado.", self.texto(r))
        self.assertEqual(self.sql("SELECT nome, pais FROM artista")[0][:], ("Legião Urbana", "Brasil"))

    def test_nome_vazio(self):
        r = self.client.post("/artistas/novo", data={"nome": "   ", "pais": "Brasil"})
        self.assertIn("Informe o nome do artista.", self.texto(r))
        self.assertIn('value="Brasil"', self.texto(r))  # mantém os dados digitados
        self.assertIn('id="campo-nome" aria-invalid="true" aria-describedby="erro-nome"', self.texto(r))
        self.assertEqual(self.um("SELECT COUNT(*) FROM artista"), 0)

    def test_nome_longo_demais(self):
        # cenário "Nome de artista longo demais"
        r = self.client.post("/artistas/novo", data={"nome": "x" * 121, "pais": "Brasil"})
        self.assertIn('id="erro-nome"', self.texto(r))
        self.assertIn("O nome pode ter no máximo 120 caracteres.", self.texto(r))
        r = self.client.post("/artistas/novo", data={"nome": "Djavan", "pais": "p" * 81})
        self.assertIn("O país pode ter no máximo 80 caracteres.", self.texto(r))
        self.assertEqual(self.um("SELECT COUNT(*) FROM artista"), 0)

    def test_nome_obrigatorio_marcado(self):
        self.assertRegex(self.texto(self.client.get("/artistas/novo")), r'id="campo-nome"[^>]*aria-required="true"')

    def test_nome_repetido_sem_diferenciar_maiusculas_e_acentos(self):
        self.artista("Legião Urbana")
        r = self.client.post("/artistas/novo", data={"nome": "LEGIÃO URBANA"})
        self.assertIn("Já existe um artista com esse nome.", self.texto(r))
        self.assertEqual(self.um("SELECT COUNT(*) FROM artista"), 1)

    def test_edicao_valida(self):
        a = self.artista("Legiao Urbana")
        self.musica("Tempo Perdido", a)
        self.client.post(f"/artistas/{a}/editar", data={"nome": "Legião Urbana"})
        self.assertIn("Legião Urbana", self.texto(self.client.get("/musicas")))

    def test_edicao_para_nome_repetido(self):
        self.artista("Djavan")
        a = self.artista("Legião Urbana")
        r = self.client.post(f"/artistas/{a}/editar", data={"nome": "djavan"})
        self.assertIn("Já existe um artista com esse nome.", self.texto(r))
        self.assertEqual(self.um("SELECT nome FROM artista WHERE id = ?", (a,)), "Legião Urbana")

    def test_editar_inexistente_404(self):
        self.assertEqual(self.client.get("/artistas/999/editar").status_code, 404)

    def test_excluir_sem_musicas(self):
        a = self.artista("Djavan")
        self.client.post(f"/artistas/{a}/excluir")
        self.assertEqual(self.um("SELECT COUNT(*) FROM artista"), 0)

    def test_excluir_com_musicas_bloqueado(self):
        a = self.artista("Legião Urbana")
        self.musica("Tempo Perdido", a)
        self.musica("Índios", a)
        r = self.client.post(f"/artistas/{a}/excluir", follow_redirects=True)
        self.assertIn("Este artista tem 2 música(s). Exclua as músicas antes de excluir o artista.", self.texto(r))
        self.assertEqual(self.um("SELECT COUNT(*) FROM artista"), 1)
        self.assertEqual(self.um("SELECT COUNT(*) FROM musica"), 2)

    def test_formulario_de_exclusao_pede_confirmacao(self):
        self.artista("Djavan")
        self.assertIn("data-confirmar=", self.texto(self.client.get("/artistas")))
