import re

from tests.base import BaseTest


class TestNavegacao(BaseTest):
    def atual(self, url):
        html = self.texto(self.client.get(url))
        atuais = re.findall(r'<a class="aba" href="([^"]+)" aria-current="page">', html)
        self.assertEqual(len(atuais), 1, f"{url}: {atuais}")  # exatamente uma seção destacada
        return atuais[0]

    def test_secao_atual(self):
        m = self.musica("Tempo Perdido")
        p = self.inserir("INSERT INTO playlist (nome) VALUES ('Roda')")
        s = self.sorteio(m)
        casos = {"/": "/", "/musicas": "/musicas", "/musicas/nova": "/musicas", f"/musicas/{m}/editar": "/musicas",
                 "/artistas/novo": "/artistas", f"/playlists/{p}": "/playlists", f"/sorteios/{s}": "/",
                 "/historico": "/historico"}
        for url, esperado in casos.items():
            with self.subTest(url=url):
                self.assertEqual(self.atual(url), esperado)


class TestToasts(BaseTest):
    def test_sucesso_e_status_com_auto(self):
        r = self.client.post("/artistas/novo", data={"nome": "Djavan"}, follow_redirects=True)
        html = self.texto(r)
        self.assertRegex(html, r'class="toast toast-sucesso" role="status" data-auto>')
        self.assertIn("Artista cadastrado.", html)

    def test_erro_e_alert_sem_auto(self):
        m = self.musica()
        r = self.client.post(f"/sorteios/{self.sorteio(m)}/avaliar", data={"nota": "4"}, follow_redirects=True)
        self.assertIn('class="toast toast-erro" role="alert">', self.texto(r))

    def test_aviso_rn06_e_alert(self):
        m = self.musica()
        self.sorteio(m)
        r = self.client.post("/sortear", follow_redirects=True)
        self.assertIn('class="toast toast-aviso" role="alert">', self.texto(r))
        self.assertIn("Você já tocou todas recentemente!", self.texto(r))

    def test_sem_mensagens_sem_regiao(self):
        self.assertNotIn('class="toasts"', self.texto(self.client.get("/artistas")))


class TestNome(BaseTest):
    def test_titulo_e_marca(self):
        html = self.texto(self.client.get("/musicas"))
        self.assertIn("<title>Repertório | Shuffle</title>", html)
        self.assertRegex(html, r'<a class="marca" href="/">.*<span>Shuffle</span></a>')

    def test_nome_antigo_ausente(self):
        m = self.musica("Tempo Perdido")
        p = self.inserir("INSERT INTO playlist (nome) VALUES ('Roda')")
        s = self.sorteio(m)
        for url in ("/", f"/sorteios/{s}", "/musicas", "/musicas/nova", "/artistas", "/playlists", f"/playlists/{p}",
                    "/historico"):
            with self.subTest(url=url):
                self.assertNotIn("Shuffle Meu", self.texto(self.client.get(url)))
