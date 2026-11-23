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


class TestColunasDeLink(BaseTest):
    """add-links-por-servico, D2: colunas youtube e spotify em bancos novos e antigos."""

    def colunas(self, caminho):
        con = sqlite3.connect(caminho)
        try:
            return {linha[1] for linha in con.execute("PRAGMA table_info(musica)")}
        finally:
            con.close()

    def test_banco_novo_tem_as_colunas(self):
        self.assertTrue({"link", "youtube", "spotify"} <= self.colunas(self.caminho))

    def test_banco_antigo_recebe_as_colunas_sem_perder_musicas(self):
        import os
        import tempfile
        from pathlib import Path

        from shuffle_meu import create_app

        fd, antigo = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.addCleanup(os.remove, antigo)
        schema = (Path(__file__).resolve().parent.parent / "shuffle_meu" / "schema.sql").read_text(encoding="utf-8")
        schema_antigo = "\n".join(linha for linha in schema.splitlines() if not linha.lstrip().startswith(("youtube", "spotify")))
        con = sqlite3.connect(antigo)
        con.executescript(schema_antigo)
        con.execute("INSERT INTO artista (nome) VALUES ('Legião Urbana')")
        con.execute("INSERT INTO musica (titulo, artista_id, link) VALUES ('Tempo Perdido', 1, 'https://exemplo.net/cifra')")
        con.commit()
        con.close()
        self.assertNotIn("youtube", self.colunas(antigo))

        for _ in range(2):  # a segunda inicialização não pode falhar (idempotente)
            create_app({"TESTING": True, "DATABASE": antigo})
        self.assertTrue({"youtube", "spotify"} <= self.colunas(antigo))
        con = sqlite3.connect(antigo)
        linha = con.execute("SELECT titulo, link, youtube, spotify FROM musica").fetchone()
        con.close()
        self.assertEqual(linha, ("Tempo Perdido", "https://exemplo.net/cifra", None, None))

    def test_check_recusa_outros_esquemas(self):
        for coluna in ("youtube", "spotify"):
            with self.subTest(coluna=coluna), self.assertRaises(sqlite3.IntegrityError):
                self.musica(f"Teste {coluna}", **{coluna: "javascript:alert(1)"})
