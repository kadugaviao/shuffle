import json
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
                       "Toquei ✅", "Pular ⏭️"):
            self.assertIn(trecho, html)
        self.assertNotIn('name="nota"', html)  # estrelas só depois de "Toquei"

    def test_roleta_so_na_primeira_visualizacao(self):
        for t in ("Tempo Perdido", "Índios", "Oceano"):
            self.musica(t)
        url = self.sortear().headers["Location"]
        html = self.texto(self.client.get(url))
        self.assertIn("data-roleta='[", html)
        sorteada = self.ultimo()
        roleta = json.loads(html.split("data-roleta='", 1)[1].split("'", 1)[0])
        self.assertEqual(roleta[-1], sorteada)  # o rolo para na música sorteada
        self.assertLessEqual(len(roleta), 13)
        self.assertNotIn("data-roleta", self.texto(self.client.get(url)))  # recarregar não repete
        s = self.um("SELECT MAX(id) FROM sorteio")
        self.assertNotIn("data-roleta", self.texto(self.client.get(f"/sorteios/{s}")))  # nem pelo histórico

    def test_resultado_sem_javascript_tem_conteudo(self):
        self.musica("Tempo Perdido")
        html = self.texto(self.client.get(self.sortear().headers["Location"]))
        # o HTML entregue já traz título, artista e botões; o JS só anima
        self.assertIn('<h1 class="titulo-sorteado">Tempo Perdido</h1>', html)
        self.assertIn("Legião Urbana", html)

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
        self.assertIn("Nada com esse filtro. Tira algum?", html)  # texto literal da spec, não só a constante
        self.assertIn('value="triste" checked', html)  # chip de humor volta marcado
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

    def test_primeiro_acesso_sem_musicas(self):
        html = self.texto(self.client.get("/"))
        self.assertIn("Cadastre sua primeira música", html)
        self.assertIn('href="/musicas/nova"', html)
        self.assertNotIn("primario sortear", html)

    def test_so_musicas_inativas(self):
        self.musica("Índios", ativa=0)
        self.assertIn("primario sortear", self.texto(self.client.get("/")))
        self.assertIn(MSG_NENHUMA, self.texto(self.client.post("/sortear", follow_redirects=True)))

    def test_filtros_em_chips_e_selects(self):
        self.musica("Tempo Perdido", genero="rock")
        html = self.texto(self.client.get("/?humor=calma&dificuldade_max=3&genero=ROCK&n=7"))
        self.assertIn('name="humor" value="calma" checked', html)
        self.assertIn('name="dificuldade_max" value="3" checked', html)
        self.assertIn('name="genero" value="rock" checked><span>Rock</span>', html)  # exibe capitalizado, valor intacto
        self.assertIn('value="7"', html)
        self.assertIn('<span class="unidade" aria-hidden="true">rodadas</span>', html)

    def test_sem_filtros_marca_todos(self):
        self.musica("Tempo Perdido", genero="rock")
        html = self.texto(self.client.get("/"))
        for nome in ("humor", "dificuldade_max", "genero"):
            self.assertIn(f'name="{nome}" value="" checked', html)

    def test_cartao_de_espera_sem_sorteios(self):
        self.musica("Tempo Perdido")
        html = self.texto(self.client.get("/"))
        self.assertIn("Sua última música aparece aqui", html)
        self.assertNotIn("Última sorteada:", html)
        self.sorteio(1)
        html = self.texto(self.client.get("/"))
        self.assertIn("Última sorteada: Tempo Perdido — Legião Urbana", html)
        self.assertNotIn("Sua última música aparece aqui", html)

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
