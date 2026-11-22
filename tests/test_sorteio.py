import random
import time
import unittest

from shuffle_meu.sorteio import AVISO_TODAS_RECENTES, MSG_NENHUMA, escolher, ler_filtros
from tests.base import BaseTest


def c(id, favorita=0):
    return {"id": id, "favorita": favorita}


class TestEscolher(unittest.TestCase):
    def test_recente_nunca_sai(self):
        rng = random.Random(1)
        for _ in range(200):
            musica, aviso = escolher([c(1), c(2), c(3)], {1}, rng)
            self.assertNotEqual(musica["id"], 1)
            self.assertIsNone(aviso)

    def test_todas_bloqueadas_rn06(self):
        musica, aviso = escolher([c(1), c(2)], {1, 2}, random.Random(1))
        self.assertIn(musica["id"], (1, 2))
        self.assertEqual(aviso, AVISO_TODAS_RECENTES)

    def test_favorita_tem_peso_dobrado(self):
        rng = random.Random(42)
        vezes = sum(escolher([c(1, favorita=1), c(2)], set(), rng)[0]["id"] == 1 for _ in range(3000))
        self.assertTrue(0.60 <= vezes / 3000 <= 0.73, vezes / 3000)


class TestLerFiltros(unittest.TestCase):
    def test_n_invalido_vira_5(self):
        for valor in ("-1", "51", "abc", ""):
            self.assertEqual(ler_filtros({"n": valor})[1], 5)
        self.assertEqual(ler_filtros({"n": "0"})[1], 0)
        self.assertEqual(ler_filtros({"n": "50"})[1], 50)

    def test_filtro_em_branco_nao_restringe(self):
        self.assertEqual(ler_filtros({"genero": " ", "humor": "", "artista_id": "x"})[0], {})


class TestSorteio(BaseTest):
    def sortear(self, **dados):
        r = self.client.post("/sortear", data=dados)
        self.assertEqual(r.status_code, 302)
        return r

    def ultimo(self):
        linhas = self.sql("SELECT m.titulo FROM sorteio s JOIN musica m ON m.id = s.musica_id ORDER BY s.id DESC")
        return linhas[0][0] if linhas else None

    def test_so_ativas_participam_rn04(self):
        self.musica("Tempo Perdido")
        self.musica("Índios", ativa=0)
        for _ in range(10):
            self.sortear(n="0")
            self.assertEqual(self.ultimo(), "Tempo Perdido")

    def test_tela_de_resultado(self):
        self.musica("Tempo Perdido", link="https://exemplo.com/cifra")
        r = self.sortear()
        html = self.texto(self.client.get(r.headers["Location"]))
        for trecho in ("Tempo Perdido", "Legião Urbana", 'href="https://exemplo.com/cifra"', 'target="_blank"',
                       "Toquei", "Pular", "Avaliar"):
            self.assertIn(trecho, html)

    def test_resultado_inexistente_404(self):
        self.assertEqual(self.client.get("/sorteios/999").status_code, 404)

    def test_filtro_por_humor_e_dificuldade(self):
        self.musica("Oceano", humor="calma", dificuldade=4)
        self.musica("Tempo Perdido", humor="calma", dificuldade=2)
        self.musica("Índios", humor="animada", dificuldade=1)
        for _ in range(10):
            self.sortear(humor="calma", dificuldade_max="3", n="0")
            self.assertEqual(self.ultimo(), "Tempo Perdido")

    def test_filtro_por_playlist(self):
        m = self.musica("Tempo Perdido")
        self.musica("Índios")
        p = self.inserir("INSERT INTO playlist (nome) VALUES ('Roda de violão')")
        self.inserir("INSERT INTO playlist_musica VALUES (?, ?)", (p, m))
        for _ in range(10):
            self.sortear(playlist_id=str(p), n="0")
            self.assertEqual(self.ultimo(), "Tempo Perdido")

    def test_filtro_por_artista(self):
        self.musica("Tempo Perdido")
        djavan = self.artista("Djavan")
        self.musica("Oceano", djavan)
        self.musica("Flor de Lis", djavan, ativa=0)
        for _ in range(10):
            self.sortear(artista_id=str(djavan), n="0")
            self.assertEqual(self.ultimo(), "Oceano")

    def test_filtro_sem_resultado_rn05(self):
        self.musica("Tempo Perdido", humor="calma")
        r = self.sortear(humor="triste")
        self.assertIn("humor=triste", r.headers["Location"])  # volta com os filtros
        html = self.texto(self.client.get(r.headers["Location"]))
        self.assertIn(MSG_NENHUMA, html)
        self.assertIn('<option value="triste" selected>', html)
        self.assertEqual(self.um("SELECT COUNT(*) FROM sorteio"), 0)

    def test_repertorio_vazio_rn05(self):
        r = self.client.post("/sortear", follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn(MSG_NENHUMA, self.texto(r))

    def test_musica_recente_e_ignorada(self):
        tempo = self.musica("Tempo Perdido")
        self.musica("Índios")
        self.sorteio(tempo)
        for _ in range(3):  # com N = 5 o histórico tem no máximo 4 sorteios aqui: Tempo Perdido segue bloqueada
            self.sortear(n="5")
            self.assertEqual(self.ultimo(), "Índios")
            self.sql("DELETE FROM sorteio WHERE id = (SELECT MAX(id) FROM sorteio)")

    def test_bloqueio_expira_depois_de_n_rodadas(self):
        tempo = self.musica("Tempo Perdido")
        outra = self.musica("Índios")
        self.sorteio(tempo)
        self.sorteio(outra)
        self.sorteio(outra)  # Tempo Perdido foi 3 rodadas atrás; com N = 2 só Índios está bloqueada
        self.sortear(n="2")
        self.assertEqual(self.ultimo(), "Tempo Perdido")

    def test_todas_as_musicas_bloqueadas_rn06(self):
        ids = [self.musica(t) for t in ("A", "B", "C")]
        for m in ids:
            self.sorteio(m)
        r = self.sortear()
        self.assertIn(AVISO_TODAS_RECENTES, self.texto(self.client.get(r.headers["Location"])))
        self.assertEqual(self.um("SELECT COUNT(*) FROM sorteio"), 4)

    def test_desempenho_com_1000_musicas(self):
        a = self.artista_padrao()
        con = self.conectar()
        con.executemany(
            "INSERT INTO musica (titulo, artista_id, humor, dificuldade, favorita) VALUES (?, ?, ?, ?, ?)",
            [(f"Música {i}", a, ("animada", "calma")[i % 2], i % 5 + 1, i % 7 == 0) for i in range(1000)],
        )
        con.executemany("INSERT INTO sorteio (musica_id) VALUES (?)", [(i % 1000 + 1,) for i in range(1000)])
        con.commit()
        con.close()
        inicio = time.perf_counter()
        r = self.sortear(humor="calma", dificuldade_max="4", n="50")
        self.client.get(r.headers["Location"])
        self.assertLess(time.perf_counter() - inicio, 1.0)
