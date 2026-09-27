"""Gera as imagens do site a partir de originais/.

Uso:  python tools/processar_imagens.py

- Lê conteudo/obras.json (séries, ordem, legendas).
- Arquivos novos em originais/<serie>/ que ainda não estão no JSON entram no fim da série.
- Para cada obra gera, em assets/obras/<serie>/:
    <nome>-t.webp  miniatura 4:5, 800x1000 (faixas da home e do orçamento)
    <nome>-m.webp  galeria da página Trabalhos, proporção original, altura até 720 px
    <nome>-g.webp  visualização ampliada, proporção original, lado maior até 2000 px
- Escreve assets/js/obras.js, que o site lê.
Só reprocessa o que mudou. Precisa de Python 3 e Pillow (pip install pillow).
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
ORIG = RAIZ / "originais"
SAIDA = RAIZ / "assets" / "obras"
CONTEUDO = RAIZ / "conteudo" / "obras.json"
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}

GRADE = (800, 1000)          # 4:5, faixas da home e do orçamento
GALERIA = (1400, 720)        # página Trabalhos: proporção original, altura até 720 px (linhas de até 360 px em tela retina)
AMPLIADA = 2000              # lado maior
QUAL_GRADE, QUAL_AMPLIADA = 78, 82
FUNDO = (5, 5, 5)
# Séries de arte: se a proporção fugir muito de 4:5, a obra entra inteira (com respiro) em vez de cortada
SEM_CORTE = {"digital", "mao", "paineis", "papel", "flash"}


def enquadrar(im, serie, item):
    modo = item.get("enquadrar")
    ratio = im.width / im.height
    if not modo:
        modo = "inteira" if serie in SEM_CORTE and not (0.7 <= ratio <= 0.9) else "cortar"
    if modo == "inteira":
        fundo = Image.new("RGB", GRADE, FUNDO)
        pad = 48
        obra = ImageOps.contain(im, (GRADE[0] - pad * 2, GRADE[1] - pad * 2), Image.LANCZOS)
        fundo.paste(obra, ((GRADE[0] - obra.width) // 2, (GRADE[1] - obra.height) // 2))
        return fundo
    foco = {"topo": (0.5, 0.2), "base": (0.5, 0.8)}.get(item.get("foco"), (0.5, 0.5))
    return ImageOps.fit(im, GRADE, Image.LANCZOS, centering=foco)


def abrir(path):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        base = Image.new("RGB", im.size, FUNDO)
        base.paste(im, mask=im.split()[-1])
        return base
    return im.convert("RGB")


def main():
    dados = json.loads(CONTEUDO.read_text(encoding="utf-8"))
    total, feitos = 0, 0
    for serie in dados["series"]:
        pasta = ORIG / serie["slug"]
        conhecidos = {i["arquivo"] for i in serie["itens"]}
        if pasta.exists():
            for f in sorted(pasta.iterdir()):
                if f.suffix.lower() in EXTS and f.name not in conhecidos:
                    serie["itens"].append({"arquivo": f.name, "legenda": "", "grupo": None})
                    print(f"  + novo em {serie['slug']}: {f.name}")
        destino = SAIDA / serie["slug"]
        destino.mkdir(parents=True, exist_ok=True)
        for item in serie["itens"]:
            src = pasta / item["arquivo"]
            if not src.exists():
                print(f"  ! não encontrado: {src.relative_to(RAIZ)}")
                continue
            stem = Path(item["arquivo"]).stem
            t, m, g = (destino / f"{stem}-{s}.webp" for s in ("t", "m", "g"))
            total += 1
            saidas = (t, m, g)
            novo = not all(f.exists() for f in saidas) or min(f.stat().st_mtime for f in saidas) < src.stat().st_mtime
            if novo or "w" not in item:
                im = abrir(src)
                if novo:
                    enquadrar(im, serie["slug"], item).save(t, "WEBP", quality=QUAL_GRADE, method=6)
                    med = im.copy()
                    med.thumbnail(GALERIA, Image.LANCZOS)
                    med.save(m, "WEBP", quality=QUAL_GRADE, method=6)
                    amp = im.copy()
                    amp.thumbnail((AMPLIADA, AMPLIADA), Image.LANCZOS)
                    amp.save(g, "WEBP", quality=QUAL_AMPLIADA, method=6)
                    feitos += 1
                with Image.open(g) as gi:
                    item["w"], item["h"] = gi.size
            item["t"] = f"assets/obras/{serie['slug']}/{stem}-t.webp"
            item["m"] = f"assets/obras/{serie['slug']}/{stem}-m.webp"
            item["g"] = f"assets/obras/{serie['slug']}/{stem}-g.webp"

    CONTEUDO.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    publico = {"series": [{k: v for k, v in s.items()} | {"itens": [
        {k: i[k] for k in ("t", "m", "g", "w", "h", "legenda", "grupo", "ano", "cicatrizada") if i.get(k) not in (None, "")}
        for i in s["itens"] if "t" in i]} for s in dados["series"]]}
    js = RAIZ / "assets" / "js" / "obras.js"
    js.parent.mkdir(parents=True, exist_ok=True)
    js.write_text("// Gerado por tools/processar_imagens.py. Não editar à mão: edite conteudo/obras.json.\nwindow.OBRAS = "
                  + json.dumps(publico, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    peso = sum(f.stat().st_size for f in SAIDA.rglob("*.webp")) / 1048576
    print(f"{total} obras, {feitos} processadas agora, {peso:.1f} MB em assets/obras")


if __name__ == "__main__":
    sys.exit(main())
