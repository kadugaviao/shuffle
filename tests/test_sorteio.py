import json
import random
import re
import time
import unittest

from shuffle_meu.sorteio import AVISO_TODAS_RECENTES, MSG_NENHUMA, escolher, ler_filtros, player
from tests.base import BaseTest

YT = "dQw4w9WgXcQ"
SP = "4uLU6hMCjMI75M1A2tKUQC"


class TestPlayer(unittest.TestCase):
    """Extração do ID do player (design D1): só formatos conhecidos, host por igualdade, ID estrito."""

    def test_youtube_aceitos(self):
        for link in (f"https://www.youtube.com/watch?v={YT}", f"https://youtube.com/watch?v={YT}",
                     f"https://m.youtube.com/watch?v={YT}&t=42s", f"https://music.youtube.com/watch?v={YT}&si=x",
                     f"http://www.youtube.com/watch?feature=share&v={YT}", f"https://youtu.be/{YT}?si=abc",
                     f"https://youtu.be/{YT}/", f"https://www.youtube.com/shorts/{YT}", f"https://YouTube.com/watch?v={YT}"):
            with self.subTest(link=link):
                self.assertEqual(player(link), {"servico": "YouTube", "src": f"https://www.youtube-nocookie.com/embed/{YT}?autoplay=1"})

    def test_spotify_aceitos(self):
        for link in (f"https://open.spotify.com/track/{SP}", f"https://open.spotify.com/track/{SP}?si=abc",
                     f"https://open.spotify.com/intl-pt/track/{SP}", f"https://open.spotify.com/intl-pt-br/track/{SP}/"):
            with self.subTest(link=link):
                self.assertEqual(player(link), {"servico": "Spotify", "src": f"https://open.spotify.com/embed/track/{SP}"})

    def test_recusados(self):
        for link in ("", None, "https://www.youtube.com/results?search_query=tempo+perdido",
                     f"https://www.youtube.com/playlist?list={YT}", f"https://www.youtube.com/watch?v={YT}x",
                     f"https://www.youtube.com/watch?v={YT[:10]}", "https://youtu.be/abc\"onload=x",
                     f"https://youtube.com.exemplo.net/watch?v={YT}", f"https://exemplo.net/youtube.com/watch?v={YT}",
                     f"https://youtube.com@exemplo.net/watch?v={YT}", f"https://notyoutube.com/watch?v={YT}",
                     f"javascript:alert(1)//youtube.com/watch?v={YT}", f"ftp://youtu.be/{YT}",
                     f"https://www.youtube.com/embed/{YT}", f"https://open.spotify.com/album/{SP}",
                     f"https://open.spotify.com/playlist/{SP}", f"https://open.spotify.com/track/{SP[:21]}",
                     f"https://open.spotify.com/track/{SP}<b>", f"https://open.spotify.com/intl-/track/{SP}",
                     f"https://open.spotify.com/intl-portugues/track/{SP}", f"https://open.spotify.com/intl-p/track/{SP}",
                     f"https://spotify.com/track/{SP}", "https://www.cifraclub.com.br/legiao-urbana/tempo-perdido/"):
            with self.subTest(link=link):
                self.assertIsNone(player(link))


class TestPlayerNaTela(BaseTest):
    def tela(self, link, titulo="Tempo Perdido"):
        return self.texto(self.client.get(f"/sorteios/{self.sorteio(self.musica(titulo, link=link))}"))

    def assertSoNoTemplate(self, html, src):
        self.assertEqual(html.count(src), 1)
        self.assertLess(html.index("<template data-player-modelo>"), html.index(src))
        self.assertLess(html.index(src), html.index("</template>"))
        self.assertEqual(html.count("<iframe"), 1)  # só o do template, inerte

    def test_video_do_youtube(self):
        html = self.tela(f"https://music.youtube.com/watch?v={YT}")
        self.assertIn("Ouvir aqui</button>", html)
        self.assertIn("data-ouvir hidden>", html)  # sem JS não há botão morto
        self.assertSoNoTemplate(html, f'src="https://www.youtube-nocookie.com/embed/{YT}?autoplay=1"')
        self.assertIn('title="Player do YouTube: Tempo Perdido"', html)
        self.assertIn("Abrir link", html)

    def test_faixa_do_spotify(self):
        html = self.tela(f"https://open.spotify.com/intl-pt/track/{SP}?si=abc")
        self.assertSoNoTemplate(html, f'src="https://open.spotify.com/embed/track/{SP}"')
        self.assertIn("Abrir link", html)

    def test_link_sem_player(self):
        html = self.tela("https://www.youtube.com/results?search_query=tempo+perdido")
        self.assertNotIn("Ouvir aqui", html)
        self.assertNotIn("<template", html)
        self.assertIn("Abrir link", html)

    def test_links_maliciosos_nao_viram_player(self):
        for i, link in enumerate((f"https://youtube.com.exemplo.net/watch?v={YT}", 'https://youtu.be/abc"onload=x')):
            with self.subTest(link=link):
                html = self.tela(link, titulo=f"Música {i}")
                self.assertNotIn("Ouvir aqui", html)
                self.assertNotIn("<iframe", html)
                self.assertFalse(any("exemplo.net" in v or "onload" in v for v in re.findall(r'src="([^"]*)"', html)))


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
                       "Toquei</button>", "Pular</button>"):
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

    def test_carimbo_conforme_o_estado(self):
        s = self.sorteio(self.musica("Tempo Perdido"))
        self.assertIn('<p class="carimbo" aria-hidden="true">Toca essa!</p>', self.texto(self.client.get(f"/sorteios/{s}")))
        self.client.post(f"/sorteios/{s}/toquei")
        html = self.texto(self.client.get(f"/sorteios/{s}"))
        self.assertIn('<p class="carimbo carimbo-tocada" aria-hidden="true">Tocada</p>', html)
        self.assertNotIn("Toca essa!", html)

    def test_titulo_longo_desce_um_degrau(self):
        s = self.sorteio(self.musica("Eu Sei Que Vou Te Amar (ao vivo)"))
        self.assertIn('<h1 class="titulo-sorteado titulo-longo">', self.texto(self.client.get(f"/sorteios/{s}")))

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
