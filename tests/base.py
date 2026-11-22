import os
import sqlite3
import tempfile
import unittest

from shuffle_meu import create_app


class BaseTest(unittest.TestCase):
    """App com banco temporário. `sql()` acessa o banco por fora, como um usuário olhando as tabelas."""

    def setUp(self):
        fd, self.caminho = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.app = create_app({"TESTING": True, "DATABASE": self.caminho})
        self.client = self.app.test_client()

    def tearDown(self):
        os.remove(self.caminho)

    def conectar(self):
        con = sqlite3.connect(self.caminho)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def sql(self, consulta, params=()):
        """Executa e devolve as linhas (lista vazia para INSERT/UPDATE/DELETE)."""
        return self._executar(consulta, params)[0]

    def inserir(self, consulta, params=()):
        """Executa um INSERT e devolve o id da linha criada."""
        return self._executar(consulta, params)[1]

    def _executar(self, consulta, params):
        con = self.conectar()
        try:
            cur = con.execute(consulta, params)
            linhas = cur.fetchall()
            con.commit()
            return linhas, cur.lastrowid
        finally:
            con.close()

    def um(self, consulta, params=()):
        """Primeiro valor da primeira linha (ex.: um COUNT)."""
        return self.sql(consulta, params)[0][0]

    def artista(self, nome="Legião Urbana", pais=None):
        return self.inserir("INSERT INTO artista (nome, pais) VALUES (?, ?)", (nome, pais))

    def musica(self, titulo="Tempo Perdido", artista_id=None, **campos):
        campos = {"titulo": titulo, "artista_id": artista_id or self.artista_padrao(), **campos}
        colunas = ", ".join(campos)
        marcas = ", ".join("?" * len(campos))
        return self.inserir(f"INSERT INTO musica ({colunas}) VALUES ({marcas})", tuple(campos.values()))

    def artista_padrao(self):
        linhas = self.sql("SELECT id FROM artista ORDER BY id LIMIT 1")
        return linhas[0][0] if linhas else self.artista()

    def sorteio(self, musica_id, **campos):
        campos = {"musica_id": musica_id, **campos}
        colunas = ", ".join(campos)
        marcas = ", ".join("?" * len(campos))
        return self.inserir(f"INSERT INTO sorteio ({colunas}) VALUES ({marcas})", tuple(campos.values()))

    def texto(self, resposta):
        return resposta.get_data(as_text=True)
