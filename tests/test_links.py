"""Extração por serviço (design D1 de add-links-por-servico): só formatos conhecidos, host por igualdade, ID estrito."""

import unittest

from shuffle_meu.links import players, spotify_id, youtube_id

YT = "jNQXAC9IVRw"
SP = "4uLU6hMCjMI75M1A2tKUQC"

YOUTUBE_VALIDOS = (f"https://www.youtube.com/watch?v={YT}", f"https://youtube.com/watch?v={YT}",
                   f"https://m.youtube.com/watch?v={YT}&t=42s", f"https://music.youtube.com/watch?v={YT}&si=x",
                   f"http://www.youtube.com/watch?feature=share&v={YT}", f"https://youtu.be/{YT}?si=abc",
                   f"https://youtu.be/{YT}/", f"https://www.youtube.com/shorts/{YT}", f"https://YouTube.com/watch?v={YT}")
SPOTIFY_VALIDOS = (f"https://open.spotify.com/track/{SP}", f"https://open.spotify.com/track/{SP}?si=abc",
                   f"https://open.spotify.com/intl-pt/track/{SP}", f"https://open.spotify.com/intl-pt-br/track/{SP}/")
RECUSADOS = ("", None, "https://www.youtube.com/results?search_query=tempo+perdido",
             f"https://www.youtube.com/playlist?list={YT}", f"https://www.youtube.com/watch?v={YT}x",
             f"https://www.youtube.com/watch?v={YT[:10]}", 'https://youtu.be/abc"onload=x',
             f"https://youtube.com.exemplo.net/watch?v={YT}", f"https://exemplo.net/youtube.com/watch?v={YT}",
             f"https://youtube.com@exemplo.net/watch?v={YT}", f"https://notyoutube.com/watch?v={YT}",
             f"javascript:alert(1)//youtube.com/watch?v={YT}", f"ftp://youtu.be/{YT}",
             f"https://www.youtube.com/embed/{YT}", f"https://music.youtube.com/shorts/{YT}",
             f"https://open.spotify.com/album/{SP}", f"https://open.spotify.com/playlist/{SP}",
             f"https://open.spotify.com/track/{SP[:21]}", f"https://open.spotify.com/track/{SP}<b>",
             f"https://open.spotify.com/intl-/track/{SP}", f"https://open.spotify.com/intl-portugues/track/{SP}",
             f"https://open.spotify.com/intl-p/track/{SP}", f"https://spotify.com/track/{SP}",
             "https://www.cifraclub.com.br/legiao-urbana/tempo-perdido/")


class TestYoutubeId(unittest.TestCase):
    def test_aceitos(self):
        for link in YOUTUBE_VALIDOS:
            with self.subTest(link=link):
                self.assertEqual(youtube_id(link), YT)

    def test_recusados_e_spotify(self):
        for link in RECUSADOS + SPOTIFY_VALIDOS:
            with self.subTest(link=link):
                self.assertIsNone(youtube_id(link))


class TestSpotifyId(unittest.TestCase):
    def test_aceitos(self):
        for link in SPOTIFY_VALIDOS:
            with self.subTest(link=link):
                self.assertEqual(spotify_id(link), SP)

    def test_recusados_e_youtube(self):
        for link in RECUSADOS + YOUTUBE_VALIDOS:
            with self.subTest(link=link):
                self.assertIsNone(spotify_id(link))


class TestPlayers(unittest.TestCase):
    YT_PLAYER = {"chave": "youtube", "servico": "YouTube", "src": f"https://www.youtube-nocookie.com/embed/{YT}?autoplay=1"}
    SP_PLAYER = {"chave": "spotify", "servico": "Spotify", "src": f"https://open.spotify.com/embed/track/{SP}"}

    def test_zero_um_e_dois(self):
        self.assertEqual(players(None, None), [])
        self.assertEqual(players("https://exemplo.net/", "https://exemplo.net/"), [])
        self.assertEqual(players(f"https://youtu.be/{YT}", None), [self.YT_PLAYER])
        self.assertEqual(players(None, f"https://open.spotify.com/track/{SP}"), [self.SP_PLAYER])
        # sempre YouTube antes de Spotify
        self.assertEqual(players(f"https://youtu.be/{YT}", f"https://open.spotify.com/track/{SP}"), [self.YT_PLAYER, self.SP_PLAYER])

    def test_link_do_servico_trocado_nao_vira_player(self):
        self.assertEqual(players(f"https://open.spotify.com/track/{SP}", f"https://youtu.be/{YT}"), [])
