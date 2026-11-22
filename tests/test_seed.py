import seed
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
        self.assertEqual(self.contar("artista"), 8)
        self.assertEqual(self.contar("musica"), 25)
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
        con.execute("UPDATE musica SET dificuldade = 5 WHERE titulo = 'Hey Jude'")
        con.commit()
        seed.semear(con)
        con.close()
        self.assertEqual(self.um("SELECT dificuldade FROM musica WHERE titulo = 'Hey Jude'"), 5)
