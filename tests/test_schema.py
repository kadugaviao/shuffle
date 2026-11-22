import sqlite3

from tests.base import BaseTest


class TestSchema(BaseTest):
    def test_cria_as_cinco_tabelas(self):
        tabelas = {r[0] for r in self.sql("SELECT name FROM sqlite_master WHERE type = 'table'")}
        self.assertTrue({"artista", "musica", "playlist", "playlist_musica", "sorteio"} <= tabelas)

    def test_dificuldade_fora_da_faixa_rn03(self):
        for valor in (0, 6):
            with self.assertRaises(sqlite3.IntegrityError):
                self.musica(f"Teste {valor}", dificuldade=valor)

    def test_titulo_e_artista_unicos_rn02(self):
        self.musica("Tempo Perdido")
        with self.assertRaises(sqlite3.IntegrityError):
            self.musica("TEMPO PERDIDO")

    def test_nota_exige_tocada_rn07(self):
        m = self.musica()
        with self.assertRaises(sqlite3.IntegrityError):
            self.sorteio(m, nota=4)
        self.sorteio(m, tocada=1, nota=4)

    def test_foreign_keys_ligado_na_conexao_da_app(self):
        from shuffle_meu.db import get_db

        with self.app.app_context():
            self.assertEqual(get_db().execute("PRAGMA foreign_keys").fetchone()[0], 1)
