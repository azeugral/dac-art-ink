"""Gera a "parede" de fundo do site: gotas escorrendo, estrelas desenhadas à mão, palavras espalhadas,
rabiscos e riscos finos, na linguagem do fundo do portfólio antigo da Dani, com a paleta da marca.

Uso:  python tools/gerar_parede.py
Saída: assets/img/parede-desktop.webp (1920x1200) e assets/img/parede-mobile.webp (900x1800), fundo transparente.
Precisa de Pillow e das fontes de grafite em ../_ref/fontes-arte (Sedgwick Ave Display, Permanent Marker, Rock Salt,
todas do Google Fonts, só para desenhar a arte; elas não são carregadas pelo site).

A composição é fixa (semente e posições definidas à mão): denso nas bordas, respirando no centro, onde fica o conteúdo.
A opacidade de cada elemento já vem na arte; a intensidade geral se ajusta no CSS (--parede).
"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
FONTES = RAIZ.parent / "_ref" / "fontes-arte"
S = 2  # superamostragem: desenha em 2x e reduz, para o traço ficar macio

MENTA = (0, 224, 128)
LIMA = (72, 240, 24)
NEON = (208, 112, 255)
MAGENTA = (255, 79, 216)
CIANO = (60, 230, 255)
BRANCO = (232, 232, 226)
AMARELO = (226, 240, 60)
CINZA = (150, 150, 158)


def fonte(nome, tam):
    arq = {"tag": "SedgwickAveDisplay-Regular.ttf", "marker": "PermanentMarker-Regular.ttf", "mao": "RockSalt-Regular.ttf"}[nome]
    return ImageFont.truetype(str(FONTES / arq), int(tam * S))


class Parede:
    def __init__(self, w, h, semente):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        self.r = random.Random(semente)

    # ---------- base: um elemento é desenhado numa camada local, recebe opacidade e rotação, e é colado ----------
    def colar(self, camada, cx, cy, alfa, rot=0):
        if rot:
            camada = camada.rotate(rot, resample=Image.BICUBIC, expand=True)
        a = camada.getchannel("A").point(lambda v: int(v * alfa))
        camada.putalpha(a)
        x, y = int(cx * S - camada.width / 2), int(cy * S - camada.height / 2)
        sx, sy = max(0, -x), max(0, -y)
        dx, dy = max(0, x), max(0, y)
        w = min(camada.width - sx, self.img.width - dx)
        h = min(camada.height - sy, self.img.height - dy)
        if w <= 0 or h <= 0:
            return
        self.img.alpha_composite(camada.crop((sx, sy, sx + w, sy + h)), (dx, dy))

    def local(self, w, h):
        c = Image.new("RGBA", (int(w * S), int(h * S)), (0, 0, 0, 0))
        return c, ImageDraw.Draw(c)

    # ---------- traço de mão livre: suaviza, treme de leve e varia a espessura ----------
    def traco(self, d, pts, larg, cor, tremor=1.2, passos=10):
        r = self.r
        suaves = []
        for i in range(len(pts) - 1):
            p0 = pts[max(i - 1, 0)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(i + 2, len(pts) - 1)]
            for k in range(passos):
                t = k / passos; t2, t3 = t * t, t * t * t
                x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                suaves.append((x, y))
        suaves.append(pts[-1])
        dx = dy = 0.0
        fase = r.random() * 6.28
        n = len(suaves)
        for i in range(n - 1):
            dx = dx * 0.8 + r.uniform(-tremor, tremor) * 0.35
            dy = dy * 0.8 + r.uniform(-tremor, tremor) * 0.35
            pressao = 0.72 + 0.28 * math.sin(fase + i / n * math.pi * 1.6) + (0.12 if 0.1 < i / n < 0.9 else -0.1)
            wv = max(1, larg * pressao * S)
            a = ((suaves[i][0] + dx) * S, (suaves[i][1] + dy) * S)
            b = ((suaves[i + 1][0] + dx) * S, (suaves[i + 1][1] + dy) * S)
            d.line([a, b], fill=cor + (255,), width=int(wv))
            d.ellipse([b[0] - wv / 2, b[1] - wv / 2, b[0] + wv / 2, b[1] + wv / 2], fill=cor + (255,))

    # ---------- motivos ----------
    def estrela(self, cx, cy, tam, cor=BRANCO, alfa=.2, rot=0, larg=5, dupla=True):
        """Pentagrama feito num gesto só, com a ponta final passando do início, como caneta."""
        c, d = self.local(tam * 1.4, tam * 1.4)
        o = tam * 0.7
        pts = []
        for k in range(6):
            ang = math.radians(-90 + 144 * k)
            pts.append((o + math.cos(ang) * tam / 2 + self.r.uniform(-tam * .04, tam * .04), o + math.sin(ang) * tam / 2 + self.r.uniform(-tam * .04, tam * .04)))
        pts[-1] = (pts[-1][0] + tam * .08, pts[-1][1] - tam * .05)
        self.traco(d, pts, larg, cor, tremor=tam * .012, passos=4)
        if dupla:
            self.traco(d, [(x + self.r.uniform(-3, 3), y + self.r.uniform(-3, 3)) for x, y in pts[:4]], larg * .45, cor, tremor=tam * .015, passos=4)
        self.colar(c, cx, cy, alfa, rot)

    def brilho(self, cx, cy, tam, cor, alfa, rot=0):
        """Estrelinha de quatro pontas (✦) com as laterais curvas."""
        c, d = self.local(tam * 1.3, tam * 1.3)
        o = tam * .65; t = tam / 2; m = tam * .09
        pts = [(o, o - t), (o + m, o - m), (o + t, o), (o + m, o + m), (o, o + t), (o - m, o + m), (o - t, o), (o - m, o - m), (o, o - t)]
        d.polygon([(x * S, y * S) for x, y in pts], fill=cor + (255,))
        self.colar(c, cx, cy, alfa, rot)

    def coracao(self, cx, cy, tam, cor=BRANCO, alfa=.2, rot=0, larg=5):
        c, d = self.local(tam * 1.4, tam * 1.4)
        o = tam * .7
        pts = []
        for i in range(0, 34):
            t = i / 32 * 2 * math.pi
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((o + x * tam / 36, o + y * tam / 36))
        pts[-1] = (pts[-1][0] + tam * .1, pts[-1][1] - tam * .12)  # passa do ponto de início, como à mão
        self.traco(d, pts, larg, cor, tremor=tam * .01, passos=3)
        self.colar(c, cx, cy, alfa, rot)

    def xis(self, cx, cy, tam, cor, alfa, rot=0, larg=26):
        c, d = self.local(tam * 1.5, tam * 1.5)
        o = tam * .75; h = tam / 2
        self.traco(d, [(o - h, o - h * .9), (o, o + h * .05), (o + h, o + h)], larg, cor, tremor=2)
        self.traco(d, [(o + h * .9, o - h), (o - h * .05, o + h * .1), (o - h, o + h * .95)], larg * .9, cor, tremor=2)
        self.spray(d, o, o, tam * .6, 60, cor, gota=(1, 3))
        self.colar(c, cx, cy, alfa, rot)

    def zigue(self, x0, y0, comp, amp, n, cor, alfa, rot=0, larg=7):
        c, d = self.local(comp + 40, amp * 2 + 40)
        pts = [(20 + comp * i / n, 20 + amp + (amp if i % 2 else -amp) * self.r.uniform(.7, 1.1)) for i in range(n + 1)]
        self.traco(d, pts, larg, cor, tremor=1.5, passos=5)
        self.colar(c, x0 + comp / 2, y0, alfa, rot)

    def rabisco(self, cx, cy, comp, alt, voltas, cor, alfa, rot=0, larg=2.2):
        """Laçadas contínuas, como assinatura rápida."""
        c, d = self.local(comp + 40, alt * 2 + 40)
        pts = []
        for i in range(voltas * 8 + 1):
            t = i / 8 * 2 * math.pi
            pts.append((20 + comp * i / (voltas * 8) + math.cos(t) * alt * .45, 20 + alt + math.sin(t) * alt * self.r.uniform(.6, 1)))
        self.traco(d, pts, larg, cor, tremor=1, passos=4)
        self.colar(c, cx, cy, alfa, rot)

    def seta(self, x0, y0, x1, y1, cor, alfa, larg=2.5):
        mx, my = min(x0, x1) - 30, min(y0, y1) - 30
        c, d = self.local(abs(x1 - x0) + 60, abs(y1 - y0) + 60)
        a, b = (x0 - mx, y0 - my), (x1 - mx, y1 - my)
        meio = ((a[0] + b[0]) / 2 + self.r.uniform(-20, 20), (a[1] + b[1]) / 2 + self.r.uniform(-20, 20))
        self.traco(d, [a, meio, b], larg, cor, tremor=.8)
        ang = math.atan2(b[1] - meio[1], b[0] - meio[0])
        for s in (-1, 1):
            p = (b[0] - math.cos(ang + s * .5) * 22, b[1] - math.sin(ang + s * .5) * 22)
            self.traco(d, [p, b], larg, cor, tremor=.4, passos=2)
        self.colar(c, (x0 + x1) / 2, (y0 + y1) / 2, alfa)

    def risco(self, x0, y0, x1, y1, cor, alfa, larg=1.1):
        """Risco fino e longo, levemente curvo."""
        mx, my = min(x0, x1) - 20, min(y0, y1) - 20
        c, d = self.local(abs(x1 - x0) + 40, abs(y1 - y0) + 40)
        a, b = (x0 - mx, y0 - my), (x1 - mx, y1 - my)
        curva = ((a[0] + b[0]) / 2 + self.r.uniform(-30, 30), (a[1] + b[1]) / 2 + self.r.uniform(-30, 30))
        self.traco(d, [a, curva, b], larg, cor, tremor=.3, passos=24)
        self.colar(c, (x0 + x1) / 2, (y0 + y1) / 2, alfa)

    def flor(self, cx, cy, tam, cor, alfa, rot=0):
        c, d = self.local(tam * 1.4, tam * 1.4)
        o = tam * .7
        for k in range(5):
            ang = math.radians(k * 72 - 90)
            px, py = o + math.cos(ang) * tam * .28, o + math.sin(ang) * tam * .28
            r = tam * .2
            d.ellipse([(px - r) * S, (py - r) * S, (px + r) * S, (py + r) * S], fill=cor + (255,))
        r = tam * .09
        d.ellipse([(o - r) * S, (o - r) * S, (o + r) * S, (o + r) * S], fill=(0, 0, 0, 0))
        self.colar(c, cx, cy, alfa, rot)

    def olho(self, cx, cy, tam, cor, alfa, rot=0):
        c, d = self.local(tam * 1.3, tam * .9)
        o, p = tam * .65, tam * .45
        topo = [(o - tam / 2 + tam * i / 10, p - math.sin(math.pi * i / 10) * tam * .28) for i in range(11)]
        base = [(o - tam / 2 + tam * i / 10, p + math.sin(math.pi * i / 10) * tam * .24) for i in range(11)]
        self.traco(d, topo, 3, cor, tremor=.6, passos=3)
        self.traco(d, base, 3, cor, tremor=.6, passos=3)
        r = tam * .13
        d.ellipse([(o - r) * S, (p - r) * S, (o + r) * S, (p + r) * S], fill=cor + (255,))
        self.colar(c, cx, cy, alfa, rot)

    def spray(self, d, cx, cy, alcance, n, cor, gota=(1, 3.5)):
        r0, r1 = gota
        for _ in range(n):
            ang = self.r.random() * 6.283
            dist = abs(self.r.gauss(0, alcance / 2))
            x, y = cx + math.cos(ang) * dist, cy + math.sin(ang) * dist
            rr = self.r.uniform(r0, r1) * (1.8 if self.r.random() < .06 else 1)
            d.ellipse([(x - rr) * S, (y - rr) * S, (x + rr) * S, (y + rr) * S], fill=cor + (255,))

    def respingo(self, cx, cy, raio, n, cor, alfa):
        c, d = self.local(raio * 2.6, raio * 2.6)
        self.spray(d, raio * 1.3, raio * 1.3, raio, n, cor, gota=(1, 3.2))
        self.colar(c, cx, cy, alfa)

    def palavra(self, texto, cx, cy, estilo, tam, cor, alfa, rot=0):
        f = fonte(estilo, tam)
        bb = f.getbbox(texto)
        c = Image.new("RGBA", (bb[2] - bb[0] + 40 * S, bb[3] - bb[1] + 40 * S), (0, 0, 0, 0))
        ImageDraw.Draw(c).text((20 * S - bb[0], 20 * S - bb[1]), texto, font=f, fill=cor + (255,))
        self.colar(c, cx, cy, alfa, rot)

    def gotas(self, y_topo, cor, alfa, densidade=1.0):
        """Faixa de tinta irregular no alto e gotas que afinam até uma ponta bojuda, às vezes com acúmulo no meio."""
        r = self.r
        c, d = self.local(self.w, 300)
        # borda de tinta: contorno ondulado com grumos
        x, borda = 0, []
        while x <= self.w + 30:
            borda.append((x, r.uniform(3, 11) + (r.uniform(4, 10) if r.random() < .18 else 0)))
            x += r.uniform(14, 46)
        d.polygon([(0, 0)] + [(px * S, py * S) for px, py in borda] + [(self.w * S, 0)], fill=cor + (255,))
        x = r.uniform(8, 40)
        while x < self.w:
            comp = r.choice([10, 16, 24, 34, 52, 80, 120, 170, 230]) * r.uniform(.8, 1.15)
            topo = r.uniform(7, 13)
            base = r.uniform(5, 12)
            # corpo afinando: trapézio + ponta bojuda
            fino = base * r.uniform(.32, .52)
            d.polygon([((x - base / 2) * S, 2 * S), ((x + base / 2) * S, 2 * S), ((x + fino / 2) * S, (topo + comp) * S), ((x - fino / 2) * S, (topo + comp) * S)], fill=cor + (255,))
            gr = fino * r.uniform(.9, 1.35)
            d.ellipse([(x - gr) * S, (topo + comp - gr * .6) * S, (x + gr) * S, (topo + comp + gr * 1.3) * S], fill=cor + (255,))
            if comp > 60 and r.random() < .45:  # acúmulo no meio do caminho
                m = topo + comp * r.uniform(.3, .6); gm = fino * .95
                d.ellipse([(x - gm) * S, (m - gm) * S, (x + gm) * S, (m + gm * 1.4) * S], fill=cor + (255,))
            x += r.uniform(22, 110) / densidade
        self.colar(c, self.w / 2, y_topo + 150, alfa)

    def glitch(self, motivo, cx, cy, *args, desloc=4, **kw):
        """Repete o motivo em ciano e magenta, deslocado, como o coelho DAC."""
        alfa = kw.pop("alfa")
        motivo(cx - desloc, cy, *args, cor=CIANO, alfa=alfa * .55, **kw)
        motivo(cx + desloc, cy + 1, *args, cor=MAGENTA, alfa=alfa * .55, **kw)
        motivo(cx, cy, *args, cor=BRANCO, alfa=alfa * .9, **kw)

    def contagem(self, cx, cy, cor, alfa, rot=0):
        """Riscos de contagem (||||/) de parede."""
        c, d = self.local(90, 70)
        for i in range(4):
            x = 18 + i * 13
            self.traco(d, [(x, 12 + self.r.uniform(-3, 3)), (x + self.r.uniform(-3, 3), 58)], 2.4, cor, tremor=.5, passos=2)
        self.traco(d, [(8, 50), (78, 18)], 2.2, cor, tremor=.5, passos=2)
        self.colar(c, cx, cy, alfa, rot)

    def cruzinha(self, cx, cy, tam, cor, alfa, rot=0):
        c, d = self.local(tam * 1.5, tam * 1.5)
        o = tam * .75
        self.traco(d, [(o, o - tam / 2), (o, o + tam / 2)], 2.2, cor, tremor=.4, passos=2)
        self.traco(d, [(o - tam / 2, o), (o + tam / 2, o)], 2.2, cor, tremor=.4, passos=2)
        self.colar(c, cx, cy, alfa, rot)

    def pontilhado(self, x0, y0, x1, y1, cor, alfa, passo=14, raio=1.6):
        mx, my = min(x0, x1) - 10, min(y0, y1) - 10
        c, d = self.local(abs(x1 - x0) + 20, abs(y1 - y0) + 20)
        n = int(math.hypot(x1 - x0, y1 - y0) / passo)
        for i in range(n + 1):
            t = i / max(n, 1)
            x, y = x0 + (x1 - x0) * t - mx, y0 + (y1 - y0) * t - my + math.sin(t * 6) * 4
            d.ellipse([(x - raio) * S, (y - raio) * S, (x + raio) * S, (y + raio) * S], fill=cor + (255,))
        self.colar(c, (x0 + x1) / 2, (y0 + y1) / 2, alfa)

    def coroa(self, cx, cy, tam, cor, alfa, rot=0):
        c, d = self.local(tam * 1.4, tam * 1.1)
        o, b = tam * .7, tam * .85
        pts = [(o - tam / 2, b), (o - tam / 2, b - tam * .45), (o - tam / 4, b - tam * .2), (o, b - tam * .6), (o + tam / 4, b - tam * .2), (o + tam / 2, b - tam * .45), (o + tam / 2, b), (o - tam / 2 - 4, b + 2)]
        self.traco(d, pts, 3, cor, tremor=.7, passos=3)
        self.colar(c, cx, cy, alfa, rot)

    def grao(self, n, alfa):
        """Pontinhos finos espalhados (grão de parede), bem de leve."""
        c = Image.new("RGBA", self.img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        for _ in range(n):
            x, y = self.r.uniform(0, self.img.width), self.r.uniform(0, self.img.height)
            rr = self.r.uniform(.6, 1.6) * S
            tom = self.r.choice([BRANCO, BRANCO, CINZA, MENTA])
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=tom + (255,))
        c.putalpha(c.getchannel("A").point(lambda v: int(v * alfa)))
        self.img.alpha_composite(c)

    def salvar(self, nome):
        final = self.img.resize((self.w, self.h), Image.LANCZOS)
        destino = RAIZ / "assets" / "img" / nome
        final.save(destino, "WEBP", quality=86, method=6)
        return destino


def desktop():
    p = Parede(1920, 1200, 27)
    # camada 1: letreiros gigantes cortados pelas bordas, quase invisíveis (pichação antiga por baixo)
    p.palavra("DAC", 150, 1080, "tag", 520, MENTA, .035, rot=-6)
    p.palavra("ART INK", 1760, 150, "tag", 300, NEON, .03, rot=5)
    # camada 2: gotas no alto
    p.gotas(0, LIMA, .15)
    # ---- borda esquerda ----
    p.glitch(p.estrela, 150, 250, 130, alfa=.30, rot=-8, desloc=5)
    p.respingo(265, 215, 90, 260, LIMA, .20)
    p.palavra("subverso", 230, 430, "tag", 96, MENTA, .075, rot=-9)
    p.contagem(430, 330, BRANCO, .12, rot=-4)
    p.xis(380, 660, 150, CIANO, .08, rot=12)
    p.palavra("apenas sentido", 190, 760, "mao", 30, BRANCO, .11, rot=-5)
    p.coracao(110, 900, 96, MAGENTA, .24, rot=-12)
    p.flor(330, 985, 78, AMARELO, .12, rot=15)
    p.zigue(40, 1100, 360, 16, 11, AMARELO, .17, rot=-3)
    p.risco(0, 560, 560, 470, CINZA, .16)
    p.risco(20, 585, 520, 505, CINZA, .10)
    p.pontilhado(40, 1170, 480, 1140, BRANCO, .10)
    p.brilho(470, 150, 26, BRANCO, .22, rot=10)
    p.brilho(60, 640, 18, MENTA, .25)
    p.cruzinha(500, 820, 22, NEON, .22, rot=12)
    p.rabisco(90, 1030, 170, 14, 5, BRANCO, .09, rot=-6)
    p.palavra("fora do comum", 400, 1060, "mao", 18, CINZA, .14, rot=6)
    # ---- borda direita ----
    p.glitch(p.coracao, 1610, 175, 104, alfa=.26, rot=10, desloc=4)
    p.coroa(1790, 250, 60, AMARELO, .16, rot=-8)
    p.palavra("neøkid", 1680, 360, "tag", 118, MENTA, .075, rot=7)
    p.seta(1820, 470, 1640, 600, CINZA, .20)
    p.estrela(1440, 470, 70, AMARELO, .20, rot=14, larg=3.5, dupla=False)
    p.respingo(1810, 700, 110, 300, LIMA, .16)
    p.rabisco(1560, 790, 260, 22, 7, BRANCO, .10, rot=-10)
    p.xis(1760, 930, 130, NEON, .10, rot=-8)
    p.palavra("arte autoral", 1600, 1075, "marker", 36, BRANCO, .09, rot=-5)
    p.olho(1450, 960, 70, CIANO, .18, rot=-6)
    p.contagem(1880, 820, BRANCO, .10, rot=6)
    p.risco(1360, 250, 1920, 330, CINZA, .14)
    p.risco(1370, 272, 1920, 356, CINZA, .08)
    p.risco(1380, 1140, 1920, 1060, CINZA, .12)
    p.pontilhado(1400, 620, 1560, 700, BRANCO, .09)
    p.brilho(1880, 130, 22, MENTA, .26)
    p.brilho(1500, 640, 16, BRANCO, .22)
    p.cruzinha(1420, 820, 20, LIMA, .2)
    p.zigue(1690, 1165, 200, 10, 8, MAGENTA, .14, rot=4)
    p.palavra("totem 26", 1850, 560, "mao", 16, CINZA, .14, rot=-80)
    # ---- centro: quase nada, só o que liga as bordas ----
    p.risco(520, 880, 1400, 760, CINZA, .07, larg=.9)
    p.risco(600, 60, 1300, 40, CINZA, .06, larg=.9)
    p.brilho(820, 90, 16, NEON, .24, rot=20)
    p.brilho(1130, 1140, 14, LIMA, .24)
    p.palavra("DAC", 960, 1150, "tag", 64, NEON, .07, rot=-3)
    p.estrela(1060, 170, 44, BRANCO, .10, rot=-20, larg=2.5, dupla=False)
    p.palavra("handpoke", 700, 1110, "mao", 20, BRANCO, .08, rot=4)
    p.cruzinha(1240, 1010, 16, BRANCO, .14)
    return p.salvar("parede-desktop.webp")


def mobile():
    p = Parede(900, 1800, 12)
    p.palavra("DAC", 120, 1560, "tag", 380, MENTA, .035, rot=-6)
    p.palavra("ART INK", 700, 900, "tag", 190, NEON, .03, rot=6)
    p.gotas(0, LIMA, .15, densidade=.8)
    p.glitch(p.estrela, 100, 560, 100, alfa=.28, rot=-8, desloc=4)
    p.respingo(200, 520, 80, 200, LIMA, .16)
    p.glitch(p.coracao, 800, 610, 84, alfa=.24, rot=10, desloc=4)
    p.contagem(830, 760, BRANCO, .12, rot=-4)
    p.palavra("subverso", 190, 470, "tag", 84, MENTA, .075, rot=-9)
    p.seta(860, 470, 690, 580, CINZA, .18)
    p.risco(0, 640, 900, 560, CINZA, .12)
    p.risco(0, 662, 900, 590, CINZA, .07)
    p.palavra("apenas sentido", 640, 700, "mao", 26, BRANCO, .11, rot=-5)
    p.xis(120, 860, 120, CIANO, .08, rot=12)
    p.rabisco(700, 900, 200, 18, 6, BRANCO, .10, rot=-10)
    p.coroa(250, 1000, 54, AMARELO, .16, rot=-8)
    p.palavra("neøkid", 700, 1080, "tag", 100, MENTA, .075, rot=7)
    p.coracao(110, 1130, 80, MAGENTA, .24, rot=-12)
    p.olho(560, 1240, 60, CIANO, .18, rot=-6)
    p.respingo(820, 1300, 90, 220, LIMA, .15)
    p.flor(170, 1380, 70, AMARELO, .12, rot=15)
    p.pontilhado(560, 1380, 860, 1420, BRANCO, .09)
    p.palavra("arte autoral", 470, 1500, "marker", 32, BRANCO, .09, rot=-5)
    p.risco(0, 1580, 900, 1660, CINZA, .12)
    p.zigue(40, 1720, 330, 14, 10, AMARELO, .16, rot=-3)
    p.xis(770, 1680, 110, NEON, .10, rot=-8)
    p.estrela(620, 1760, 50, BRANCO, .12, rot=-20, larg=2.5, dupla=False)
    p.palavra("fora do comum", 690, 1590, "mao", 16, CINZA, .14, rot=6)
    for x, y, t, cor in [(430, 470, 20, BRANCO), (60, 640, 16, MENTA), (840, 820, 18, BRANCO), (330, 1040, 14, NEON), (860, 1450, 18, MENTA), (300, 1700, 14, LIMA)]:
        p.brilho(x, y, t, cor, .24)
    for x, y, cor in [(480, 830, NEON), (80, 1250, BRANCO), (820, 1120, LIMA)]:
        p.cruzinha(x, y, 18, cor, .18)
    return p.salvar("parede-mobile.webp")


if __name__ == "__main__":
    for f in (desktop(), mobile()):
        print(f.name, f.stat().st_size // 1024, "KB")
