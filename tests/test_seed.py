from pathlib import Path
from unittest import mock

import seed
from shuffle_meu.links import spotify_id, youtube_id
from tests.base import BaseTest


class TestSeed(BaseTest):
    def contar(self, tabela):
        return self.um(f"SELECT COUNT(*) FROM {tabela}")

    def test_carga_completa_e_idempotente(self):
        con = self.conectar()
        seed.semear(con)
        vinculos = self.contar("playlist_musica")
        seed.semear(con)  # segunda execução não pode duplicar nada
        con.close()
        # contagens exatas: INSERT OR IGNORE descartaria em silêncio uma linha que violasse um CHECK
        self.assertEqual(self.contar("artista"), 18)
        self.assertEqual(self.contar("musica"), 20)
        self.assertEqual(self.contar("playlist"), 2)
        self.assertEqual(vinculos, 16)
        self.assertEqual(self.contar("playlist_musica"), vinculos)
        self.assertEqual(self.um("SELECT COUNT(*) FROM musica WHERE ativa = 0"), 1)
        self.assertGreaterEqual(self.um("SELECT COUNT(*) FROM musica WHERE favorita = 1"), 4)
        self.assertGreaterEqual(self.um("SELECT COUNT(DISTINCT genero) FROM musica"), 4)
        self.assertEqual({r[0] for r in self.sql("SELECT DISTINCT humor FROM musica")},
                         {"animada", "calma", "triste", "romantica"})
        self.assertEqual({r[0] for r in self.sql("SELECT DISTINCT dificuldade FROM musica")}, {1, 2, 3, 4, 5})

    def test_nao_sobrescreve_edicao_do_usuario(self):
        con = self.conectar()
        seed.semear(con)
        con.execute("UPDATE musica SET dificuldade = 5 WHERE titulo = 'Back in Black'")
        con.commit()
        seed.semear(con)
        con.close()
        self.assertEqual(self.um("SELECT dificuldade FROM musica WHERE titulo = 'Back in Black'"), 5)


class TestLinksDoSeed(BaseTest):
    """add-links-por-servico, D5/D7: links do seed válidos, verificados e sem sobrescrever edições."""

    YT = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    SP = "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"

    def semear(self, links=None):
        con = self.conectar()
        try:
            if links is None:
                seed.semear(con)
            else:
                with mock.patch.object(seed, "LINKS", links):
                    seed.semear(con)
        finally:
            con.close()

    def linha(self, titulo):
        return self.sql("SELECT youtube, spotify, link FROM musica WHERE titulo = ?", (titulo,))[0]

    def test_links_validos_e_registrados_como_verificados(self):
        doc = (Path(__file__).resolve().parent.parent / "docs" / "links-verificados.md").read_text(encoding="utf-8")
        titulos = {m[0] for m in seed.MUSICAS}
        for titulo, (youtube, spotify) in seed.LINKS.items():
            with self.subTest(titulo=titulo):
                self.assertIn(titulo, titulos)
                if youtube:
                    self.assertIsNotNone(youtube_id(youtube))
                    linha = next((l for l in doc.splitlines() if youtube in l), "")
                    self.assertIn("| sim |", linha)  # trava contra ID inventado: só entra o que passou na verificação
                if spotify:
                    self.assertIsNotNone(spotify_id(spotify))
                    self.assertIn(spotify, doc)

    def test_sem_youtube_fica_a_busca_no_outro_link(self):
        self.semear()
        for titulo, artista, *_ in seed.MUSICAS:
            youtube, spotify = seed.LINKS.get(titulo, (None, None))
            with self.subTest(titulo=titulo):
                esperado = (youtube, spotify, None if youtube else seed.busca_youtube(titulo, artista))
                self.assertEqual(tuple(self.linha(titulo)), esperado)

    def test_banco_antigo_recebe_links_sem_sobrescrever_edicoes(self):
        self.semear({})  # como um banco semeado antes dos links: só a busca no "Outro link"
        con = self.conectar()
        con.execute("UPDATE musica SET youtube = 'https://youtu.be/aqz-KE-bpKQ' WHERE titulo = 'Sonne'")
        con.execute("UPDATE musica SET link = 'https://www.cifraclub.com.br/chico-buarque/construcao/' WHERE titulo = 'Construção'")
        con.commit()
        con.close()
        links = {"Back in Black": (self.YT, self.SP), "Sonne": (self.YT, None), "Construção": (self.YT, None)}
        for _ in range(2):  # idempotente
            self.semear(links)
        self.assertEqual(tuple(self.linha("Back in Black")), (self.YT, self.SP, None))  # busca do seed limpa
        sonne = self.linha("Sonne")
        self.assertEqual(sonne["youtube"], "https://youtu.be/aqz-KE-bpKQ")  # link do usuário mantido
        self.assertEqual(sonne["link"], seed.busca_youtube("Sonne", "Rammstein"))  # o seed não preencheu
        self.assertEqual(tuple(self.linha("Construção")), (self.YT, None, "https://www.cifraclub.com.br/chico-buarque/construcao/"))
