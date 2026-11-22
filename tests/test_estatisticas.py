from shuffle_meu import decimal1
from shuffle_meu.db import get_db
from shuffle_meu.estatisticas import calcular, por_genero
from tests.base import BaseTest


class TestEstatisticas(BaseTest):
    def calcular(self):
        with self.app.app_context():
            return calcular(get_db())

    def titulos(self, linhas):
        return [linha["titulo"] for linha in linhas]

    def test_resumo_com_dados(self):
        ids = [self.musica(f"M{i:02}") for i in range(25)]
        notas = [4, 5, 5, None, None, None]
        for i in range(10):
            tocada = i < 6
            self.sorteio(ids[i], tocada=int(tocada), nota=notas[i] if tocada else None)
        r = self.calcular()["resumo"]
        self.assertEqual((r["musicas"], r["sorteios"], r["tocadas"]), (25, 10, 6))
        self.assertEqual(decimal1(r["media"]), "4,7")

    def test_resumo_sem_sorteios(self):
        for t in ("A", "B", "C"):
            self.musica(t)
        r = self.calcular()["resumo"]
        self.assertEqual((r["musicas"], r["sorteios"], r["tocadas"]), (3, 0, 0))
        self.assertEqual(decimal1(r["media"]), "—")

    def test_top5_com_empate_e_sem_nao_tocadas(self):
        evid, oceano, hey, indios = (self.musica(t) for t in ("Evidências", "Oceano", "Hey Jude", "Índios"))
        for m, vezes in ((evid, 4), (oceano, 2), (hey, 2)):
            for _ in range(vezes):
                self.sorteio(m, tocada=1)
        for _ in range(3):
            self.sorteio(indios)
        top = self.calcular()["top5"]
        self.assertEqual(self.titulos(top), ["Evidências", "Hey Jude", "Oceano"])
        self.assertEqual([m["vezes"] for m in top], [4, 2, 2])

    def test_top5_limita_a_cinco(self):
        for i in range(7):
            self.sorteio(self.musica(f"Música {i}"), tocada=1)
        self.assertEqual(len(self.calcular()["top5"]), 5)

    def test_nunca_sorteadas_so_ativas_em_ordem(self):
        self.musica("Yesterday")
        self.musica("Ainda Bem")
        self.musica("We Will Rock You", ativa=0)
        self.sorteio(self.musica("Oceano"))
        self.assertEqual(self.titulos(self.calcular()["nunca"]), ["Ainda Bem", "Yesterday"])

    def test_medias_ordenadas(self):
        oceano, evid, hey = (self.musica(t) for t in ("Oceano", "Evidências", "Hey Jude"))
        for m, nota in ((oceano, 5), (oceano, 4), (evid, 5), (hey, 3), (hey, 3)):
            self.sorteio(m, tocada=1, nota=nota)
        medias = self.calcular()["medias"]
        self.assertEqual(self.titulos(medias), ["Evidências", "Oceano", "Hey Jude"])
        self.assertEqual([decimal1(m["media"]) for m in medias], ["5,0", "4,5", "3,0"])
        self.assertEqual([m["avaliacoes"] for m in medias], [1, 2, 2])

    def test_generos_com_grafias_misturadas(self):
        self.assertEqual(por_genero(["rock", "rock", "rock", "Rock", "MPB", "MPB", None]),
                         [("rock", 4), ("MPB", 2), ("Sem gênero", 1)])
        self.assertEqual(por_genero([]), [])


class TestTelaEstatisticas(BaseTest):
    def test_estados_vazios(self):
        html = self.texto(self.client.get("/historico"))
        for mensagem in ("Nenhuma música tocada ainda.", "Nenhuma música avaliada ainda.", "Nenhuma música no repertório.",
                         "Nenhum sorteio ainda."):
            self.assertIn(mensagem, html)

    def test_todas_ja_sorteadas(self):
        self.sorteio(self.musica("Oceano"))
        self.assertIn("Todas as músicas ativas já foram sorteadas.", self.texto(self.client.get("/historico")))

    def test_resumo_e_ver_todas(self):
        for i in range(12):
            self.musica(f"Música {i:02}")
        html = self.texto(self.client.get("/historico"))
        self.assertIn('<span class="numero metrica-valor">12</span>', html)
        self.assertIn("Ver todas (12)", html)  # nunca sorteadas: 10 visíveis e o resto no <details>

    def test_pagina_com_o_seed(self):
        import seed

        con = self.conectar()
        seed.semear(con)
        con.close()
        self.sorteio(1, tocada=1, nota=5)
        r = self.client.get("/historico")
        self.assertEqual(r.status_code, 200)
        self.assertIn("rock", self.texto(r))
