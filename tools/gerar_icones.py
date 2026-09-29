"""Gera favicon e ícones a partir do coelho (traço preto, fundo transparente).

Uso: python tools/gerar_icones.py caminho/do/logo.png
O coelho vai em preto sobre um quadrado claro de cantos arredondados, que aparece bem em aba clara e escura.
Nos tamanhos pequenos o traço é engrossado para não sumir.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
FUNDO = (245, 243, 238, 255)


def icone(logo, lado, arredondar=True, engrossar=0, margem=0.14):
    alfa = logo.split()[-1]
    if engrossar:
        alfa = alfa.filter(ImageFilter.MaxFilter(engrossar))
    alfa = alfa.crop(alfa.getbbox())
    area = int(lado * (1 - 2 * margem))
    alfa.thumbnail((area, area), Image.LANCZOS)
    base = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, lado - 1, lado - 1), radius=int(lado * 0.22) if arredondar else 0, fill=255)
    base.paste(Image.new("RGBA", (lado, lado), FUNDO), (0, 0), mascara)
    preto = Image.new("RGBA", alfa.size, (5, 5, 5, 255))
    base.paste(preto, ((lado - alfa.width) // 2, (lado - alfa.height) // 2), alfa)
    return base


def main():
    logo = Image.open(sys.argv[1]).convert("RGBA")
    icone(logo, 512).save(RAIZ / "assets/img/icone-512.png")
    icone(logo, 192, engrossar=9).save(RAIZ / "assets/img/icone-192.png")
    icone(logo, 180, arredondar=False, engrossar=9).save(RAIZ / "apple-touch-icon.png")
    icone(logo, 32, engrossar=41, margem=0.08).save(RAIZ / "favicon.png")
    grandes = icone(logo, 48, engrossar=31, margem=0.08)
    pequeno = icone(logo, 16, engrossar=61, margem=0.06)
    grandes.save(RAIZ / "favicon.ico", sizes=[(48, 48), (32, 32), (16, 16)], append_images=[icone(logo, 32, engrossar=41, margem=0.08), pequeno])
    print("ícones gerados")


if __name__ == "__main__":
    main()
