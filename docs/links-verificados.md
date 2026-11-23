# Links verificados do seed

Links do YouTube e do Spotify usados em `seed.py` (`LINKS`), verificados em **23/11/2026** com `tools/verificar_links.py` (Chrome headless abrindo o player como o app abre, a partir de uma página em `127.0.0.1`). Nenhum ID foi escrito de memória: cada candidato veio de uma página encontrada em pesquisa na web (resultados do YouTube e do Spotify) e só entrou aqui depois de passar na verificação.

**Critérios** (design D6 da mudança `add-links-por-servico`):

- **YouTube:** ordem de tentativa: vídeo oficial (canal do artista, VEVO, gravadora ou "Artista - Topic"), depois outro vídeo do canal oficial (ao vivo, acústico, lyric) e por fim uma versão ao vivo ou acústica de canal confiável (emissora, rádio, festival). Passa só se o player mostra o título e o canal, sem "This video is unavailable" nem mensagem de erro. Vídeos que incorporavam, mas eram de canais pessoais, foram descartados.
- **Spotify:** faixa do artista original (álbum ou remasterização; de "Boate Azul" só foi encontrada a gravação ao vivo da dupla). Passa só se o player mostra o título e o artista esperados.
- Sem vídeo aprovado, o campo YouTube fica vazio e a música mantém a busca do YouTube no "Outro link". Em música, a maioria dos vídeos oficiais bloqueia a reprodução fora do YouTube por decisão das gravadoras.

O status de incorporação muda com o tempo e por país: antes de apresentar, confira com `python tools/verificar_links.py`.

| Música | Artista | YouTube | Canal | Tipo de vídeo | Incorpora? | Motivo (quando sem YouTube) | Spotify |
|---|---|---|---|---|---|---|---|
| Here Comes the Sun | The Beatles | — | — | — | não | 6 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/6dGnYIeXmHdcikdzNNDMm2 |
| Sweet Child O' Mine | Guns N' Roses | — | — | — | não | 6 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/7snQQk1zcKl8gZ92AnueZW |
| Back in Black | AC/DC | — | — | — | não | 4 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/08mG3Y1vljYA6bvDt4Wqkj |
| Patience | Guns N' Roses | — | — | — | não | 4 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/2uKcU4FPX5eOjmd6RWb9OF |
| Bete Balanço | Barão Vermelho | — | — | — | não | 8 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação (1 que incorporava era de canal pessoal, descartado) | https://open.spotify.com/track/545yUenhKzU5ndLVCtnn7m |
| Tempo Perdido | Legião Urbana | https://www.youtube.com/watch?v=ilybyuWjBGY | A Rádio Rock (89 FM) | regravação ao vivo (89 FM com Dado Villa-Lobos) | sim | — | https://open.spotify.com/track/7B5ZOuMdaxYvn2px1dHUEi |
| Sonífera Ilha | Titãs | https://www.youtube.com/watch?v=aBrEIgQyd9Q | Titãs - Topic | oficial (Topic) | sim | — | https://open.spotify.com/track/5NtT8MYB3S2Vw8ko5NNa6Z |
| Creeping Death | Metallica | — | — | — | não | 7 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação (1 que incorporava era de canal pessoal, descartado) | https://open.spotify.com/track/1Gn1FeIYUMZ2a7PrbaaQhl |
| Sonne | Rammstein | — | — | — | não | 7 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/3gVhsZtseYtY1fMuyYq06F |
| Nightmare | Avenged Sevenfold | — | — | — | não | 3 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/5meaBghEX13kjojRrLmncU |
| Nothing Else Matters | Metallica | — | — | — | não | 3 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/2CtemffYhT0DJWcT1XW047 |
| Trem das Onze | Adoniran Barbosa | https://www.youtube.com/watch?v=4IqD4hK3D_c | Adoniran Barbosa - Topic | oficial (Topic) | sim | — | https://open.spotify.com/track/7vx5AIzcGwFoUwTzeFEMna |
| Mina do Condomínio | Seu Jorge | — | — | — | não | 8 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação (1 que incorporava era de canal pessoal, descartado) | https://open.spotify.com/track/5aGx8GTUwagGMMqt2btrH4 |
| Canta, Canta, Minha Gente | Martinho da Vila | — | — | — | não | 8 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação (3 que incorporavam eram de canais pessoais, descartados) | https://open.spotify.com/track/5VwEjqrI6E5tE7gMtuyflM |
| Evidências | Chitãozinho & Xororó | https://www.youtube.com/watch?v=tMOPMfcW_6Q | Música Multishow | ao vivo (TV Multishow) | sim | — | https://open.spotify.com/track/5FTGXGd1oPB2CRss5FbA4r |
| Boate Azul | Bruno & Marrone | — | — | — | não | 8 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/0Zx6LJJI4o6loyPi8T7ksI |
| É o Amor | Zezé Di Camargo & Luciano | — | — | — | não | 8 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/3oMk1VNl1N7dgibHwHw1j2 |
| Descobridor dos Sete Mares | Tim Maia | — | — | — | não | 8 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/4Mm9qSuCRoMl8H4yByoaNS |
| Construção | Chico Buarque | — | — | — | não | 8 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação | https://open.spotify.com/track/1ECean5dVz7mYQ07mdVGKT |
| Samurai | Djavan | — | — | — | não | 7 candidatos testados; os oficiais e os de canais confiáveis bloqueiam incorporação (1 que incorporava era de canal pessoal, descartado) | https://open.spotify.com/track/3BQAK2pnTpfZvLg2MUUU5i |
