from tests.base import BaseTest


class TestPlaylists(BaseTest):
    def playlist(self, nome, *musicas):
        p = self.inserir("INSERT INTO playlist (nome) VALUES (?)", (nome,))
        for m in musicas:
            self.inserir("INSERT INTO playlist_musica VALUES (?, ?)", (p, m))
        return p

    def test_criacao_valida(self):
        self.client.post("/playlists", data={"nome": "Roda de violão", "descricao": "Fáceis de tocar"})
        html = self.texto(self.client.get("/playlists"))
        self.assertIn("Roda de violão", html)
        self.assertIn('<span class="numero">0</span> músicas', html)

    def test_nome_vazio(self):
        r = self.client.post("/playlists", data={"nome": "  ", "descricao": "Fáceis"})
        html = self.texto(r)
        self.assertEqual(r.status_code, 200)  # mesma tela, sem redirecionar
        self.assertIn('id="campo-nome" aria-invalid="true" aria-describedby="erro-nome"', html)
        self.assertIn("Informe o nome da playlist.", html)
        self.assertIn('value="Fáceis"', html)  # mantém o que foi digitado
        self.assertEqual(self.um("SELECT COUNT(*) FROM playlist"), 0)

    def test_editar_com_nome_vazio(self):
        p = self.playlist("Churrasco")
        r = self.client.post(f"/playlists/{p}/editar", data={"nome": ""})
        html = self.texto(r)
        self.assertEqual(r.status_code, 200)
        self.assertIn('id="erro-nome"', html)
        self.assertIn('<details class="cartao editar-playlist" open>', html)
        self.assertEqual(self.um("SELECT nome FROM playlist"), "Churrasco")

    def test_lista_com_contagem(self):
        musicas = [self.musica(f"M{i}") for i in range(4)]
        self.playlist("Roda de violão", *musicas[:2])
        self.playlist("Churrasco", *musicas)
        html = self.texto(self.client.get("/playlists"))
        html = html[html.index('<ul class="lista-cartoes">'):]  # o placeholder do formulário também cita "Roda de violão"
        self.assertLess(html.index("Churrasco"), html.index("Roda de violão"))
        self.assertIn('<span class="numero">4</span> músicas', html)
        self.assertIn('<span class="numero">2</span> músicas', html)

    def test_renomear(self):
        m = self.musica("Oceano")
        p = self.playlist("Churras", m)
        self.client.post(f"/playlists/{p}/editar", data={"nome": "Churrasco"})
        html = self.texto(self.client.get(f"/playlists/{p}"))
        self.assertIn("<h1>Churrasco</h1>", html)
        self.assertIn("<strong>Oceano</strong>", html)

    def test_exclusao_mantem_as_musicas(self):
        m = self.musica("Oceano")
        p = self.playlist("Churrasco", m)
        self.client.post(f"/playlists/{p}/excluir")
        self.assertEqual(self.um("SELECT COUNT(*) FROM playlist"), 0)
        self.assertEqual(self.um("SELECT COUNT(*) FROM playlist_musica"), 0)
        self.assertEqual(self.um("SELECT COUNT(*) FROM musica"), 1)

    def test_adicionar(self):
        m = self.musica("Tempo Perdido")
        p = self.playlist("Roda de violão")
        self.client.post(f"/playlists/{p}/musicas", data={"musica_id": m})
        self.assertIn("<strong>Tempo Perdido</strong>", self.texto(self.client.get(f"/playlists/{p}")))

    def test_adicionar_repetida(self):
        m = self.musica("Tempo Perdido")
        p = self.playlist("Roda de violão", m)
        r = self.client.post(f"/playlists/{p}/musicas", data={"musica_id": m}, follow_redirects=True)
        self.assertIn("Essa música já está na playlist.", self.texto(r))
        self.assertEqual(self.um("SELECT COUNT(*) FROM playlist_musica"), 1)

    def test_adicionar_sem_escolher(self):
        p = self.playlist("Roda de violão")
        for dados in ({}, {"musica_id": 999}):
            r = self.client.post(f"/playlists/{p}/musicas", data=dados, follow_redirects=True)
            self.assertIn("Escolha uma música do repertório.", self.texto(r))

    def test_mesma_musica_em_varias_playlists(self):
        m = self.musica("Oceano")
        self.playlist("Churrasco", m)
        roda = self.playlist("Roda de violão")
        self.client.post(f"/playlists/{roda}/musicas", data={"musica_id": m})
        self.assertEqual(self.um("SELECT COUNT(*) FROM playlist_musica WHERE musica_id = ?", (m,)), 2)

    def test_remover(self):
        m = self.musica("Tempo Perdido")
        roda = self.playlist("Roda de violão", m)
        outra = self.playlist("Churrasco", m)
        self.client.post(f"/playlists/{roda}/musicas/{m}/remover")
        self.assertNotIn("<strong>Tempo Perdido</strong>", self.texto(self.client.get(f"/playlists/{roda}")))
        self.assertEqual(self.um("SELECT COUNT(*) FROM musica"), 1)
        self.assertEqual(self.um("SELECT playlist_id FROM playlist_musica"), outra)

    def test_remover_musica_fora_da_playlist(self):
        roda = self.playlist("Roda de violão", self.musica("Tempo Perdido"))
        oceano = self.musica("Oceano")
        html = self.texto(self.client.post(f"/playlists/{roda}/musicas/{oceano}/remover", follow_redirects=True))
        self.assertIn('class="toast toast-erro"', html)
        self.assertIn("Essa música não está na playlist.", html)
        self.assertNotIn("Música removida da playlist.", html)

    def test_playlist_inexistente_404(self):
        self.assertEqual(self.client.get("/playlists/999").status_code, 404)
