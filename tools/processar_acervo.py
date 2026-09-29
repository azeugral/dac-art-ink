"""Gera as imagens do Arquivo de acervo a partir de originais/acervo/<codigo>/.

Uso: python tools/processar_acervo.py
Em cada pasta: principal.<ext> (foto principal) e galeria/ (fotos inéditas, em ordem de nome).
Saída em assets/acervo/<codigo>/: principal-m.webp (ficha), principal-g.webp (ampliada) e galeria/NN.webp (miniaturas) e galeria/NN-g.webp (ampliadas).
"""
from pathlib import Path
from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
ORIG, SAIDA = RAIZ / "originais" / "acervo", RAIZ / "assets" / "acervo"
EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def abrir(p):
    im = ImageOps.exif_transpose(Image.open(p))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA"); base = Image.new("RGB", im.size, (255, 255, 255)); base.paste(im, mask=im.split()[-1]); return base
    return im.convert("RGB")


def salvar(im, destino, lado, q):
    im = im.copy(); im.thumbnail((lado, lado), Image.LANCZOS); destino.parent.mkdir(parents=True, exist_ok=True)
    im.save(destino, "WEBP", quality=q, method=6); return im.size


for pasta in sorted(p for p in ORIG.iterdir() if p.is_dir()):
    out = SAIDA / pasta.name
    principal = next(p for p in pasta.iterdir() if p.stem == "principal")
    im = abrir(principal)
    print(pasta.name, "principal", salvar(im, out / "principal-m.webp", 1100, 80), salvar(im, out / "principal-g.webp", 2000, 82))
    for n, f in enumerate(sorted(p for p in (pasta / "galeria").iterdir() if p.suffix.lower() in EXTS), 1):
        im = abrir(f)
        print("  ", f.name, "->", f"{n:02}", salvar(im, out / "galeria" / f"{n:02}.webp", 520, 76), salvar(im, out / "galeria" / f"{n:02}-g.webp", 1800, 82))
