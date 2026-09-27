# DAC ART INK: site

Site da Dani Coelho (@dac.artink): tattoo, arte autoral e atalho para a loja. Substitui o Linktree e o Adobe Portfolio.
HTML, CSS e JS puros, sem build. Publicado no GitHub Pages.

**Status: prévia.** As páginas têm `noindex` até o domínio definitivo ser publicado.

## Páginas
| Arquivo | O que é |
|---|---|
| `index.html` | Home. No celular a primeira tela funciona como link da bio (Trabalhos · Orçamento · Loja · Sobre). **É o modelo do cabeçalho e do rodapé.** |
| `trabalhos.html` | Grade 4:5 com filtro por série (`trabalhos.html#miksang` abre direto na série) e visualização ampliada |
| `orcamento.html` | Formulário que monta a mensagem e abre o WhatsApp, regras do sinal, técnicas, flash, locais |
| `cuidados.html` | Cuidados pré e pós tattoo |
| `sobre.html` | Dani e DAC Galeria |
| `404.html` | Página não encontrada |

## Como atualizar

### Trabalhos novos
1. Coloque o arquivo original em `originais/<serie>/` (tattoos, digital, mao, paineis, miksang, tecido, papel, flash).
2. Rode `python tools/processar_imagens.py`.
   - Gera a miniatura 4:5 (800×1000) e a versão ampliada (até 2000 px), as duas em WebP.
   - Obras que ainda não estavam no `conteudo/obras.json` entram no fim da série.
3. Para dar legenda, grupo ou ordem, edite `conteudo/obras.json` e rode o script de novo.
   - `"legenda"`, `"ano"` e `"grupo"` (vira subtítulo na grade; nas tattoos, é a técnica).
   - `"enquadrar": "inteira"` mostra a obra sem corte. `"foco": "topo"` ou `"base"` ajusta o corte.

Os originais ficam **fora do Git** (`.gitignore`). Só as versões otimizadas sobem.

### Menu, rodapé e contatos
Edite `index.html` e rode `python tools/montar_paginas.py`, que replica o cabeçalho e o rodapé nas outras páginas.
O conteúdo de cada página fica em `tools/paginas/<pagina>.html`.

Precisa de Python 3 e Pillow (`pip install pillow`).

## Identidade
Preto, verde-menta do logo `#00e080`, lima das gotas `#48f018`, roxo neon `#d070ff`. Os tokens estão no topo de `assets/css/site.css`.
Fontes provisórias: Big Shoulders Display, Space Mono e Instrument Sans (CONFIRMAR as fontes originais da Dani).

## CONFIRMAR antes de publicar no domínio
- Nome público (Dani Coelho), e-mail (`dac.artink@gmail.com`), locais de atendimento
- Fontes originais e logo em vetor
- Originais das imagens (as atuais vieram do Portfolio e do Instagram)
- Flash ainda disponíveis
- Domínio. Depois: tirar o `noindex` das páginas e o bloqueio do `robots.txt`, ajustar `og:image` e criar `sitemap.xml`
