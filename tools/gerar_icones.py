"""Gera favicon e ícones a partir do coelho (traço preto, fundo transparente), igual ao da DAC Galeria.

Uso: python tools/gerar_icones.py caminho/do/logo.png
Favicon e ícones do manifesto: só o contorno, sem fundo.
apple-touch-icon: o iPhone não aceita transparência (pinta de preto e o traço sumiria), então leva fundo branco.
"""
import sys
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent


def icone(logo, lado, margem=0.04, fundo=None):
    coelho = logo.crop(logo.split()[-1].getbbox())
    area = round(lado * (1 - 2 * margem))
    coelho.thumbnail((area, area), Image.LANCZOS)
    base = Image.new("RGBA", (lado, lado), fundo or (0, 0, 0, 0))
    base.alpha_composite(coelho, ((lado - coelho.width) // 2, (lado - coelho.height) // 2))
    return base


def main():
    logo = Image.open(sys.argv[1]).convert("RGBA")
    logo = Image.merge("RGBA", (*Image.new("RGB", logo.size, (0, 0, 0)).split(), logo.split()[-1]))  # traço preto puro
    icone(logo, 512).save(RAIZ / "assets/img/icone-512.png")
    icone(logo, 192).save(RAIZ / "assets/img/icone-192.png")
    icone(logo, 180, margem=0.12, fundo=(255, 255, 255, 255)).save(RAIZ / "apple-touch-icon.png")
    icone(logo, 32).save(RAIZ / "favicon.png")
    icone(logo, 128).save(RAIZ / "favicon.ico", sizes=[(128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("ícones gerados")


if __name__ == "__main__":
    main()
