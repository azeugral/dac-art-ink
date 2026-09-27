"""Monta trabalhos, orcamento, cuidados, sobre e 404 usando o index.html como modelo.

Uso:  python tools/montar_paginas.py
O cabeçalho, o rodapé e o <head> vêm do index.html. O conteúdo de cada página vem de tools/paginas/<nome>.html,
que começa com um comentário com titulo, descricao e ativo (o item do menu que fica aceso).
Para mudar menu, rodapé ou contatos: edite o index.html e rode este script.
"""
import html, re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
modelo = (RAIZ / "index.html").read_text(encoding="utf-8")
antes, resto = modelo.split('<main id="conteudo">', 1)
_, depois = resto.split("</main>", 1)

for frag in sorted((RAIZ / "tools" / "paginas").glob("*.html")):
    bruto = frag.read_text(encoding="utf-8")
    meta = dict(re.findall(r"^(\w+):[ \t]*(.*)$", re.search(r"<!--(.*?)-->", bruto, re.S).group(1), re.M))
    corpo = re.sub(r"^<!--.*?-->\s*", "", bruto, flags=re.S)
    cab = antes
    cab = re.sub(r"<title>.*?</title>", f"<title>{html.escape(meta['titulo'])}</title>", cab)
    cab = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + html.escape(meta["descricao"], quote=True), cab)
    cab = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + html.escape(meta["titulo"], quote=True), cab)
    cab = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + html.escape(meta["descricao"], quote=True), cab)
    cab = cab.replace('<link rel="preload" as="image" href="assets/img/logo.webp">\n', "")
    if meta.get("ativo"):
        cab = cab.replace(f'<a href="{meta["ativo"]}">', f'<a href="{meta["ativo"]}" aria-current="page">', 1)
    (RAIZ / frag.name).write_text(f'{cab}<main id="conteudo">\n{corpo}  </main>{depois}', encoding="utf-8")
    print("ok", frag.name)
