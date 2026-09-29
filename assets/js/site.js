/* DAC ART INK: grade de obras, visualização ampliada e orçamento pelo WhatsApp. */
(() => {
  const WHATSAPP = "5512996436334";

  const topo = document.querySelector(".barra");
  const medir = () => topo && document.documentElement.style.setProperty("--altura-topo", topo.offsetHeight + "px");
  medir();
  addEventListener("resize", medir);

  /* ---------- movimento ----------
     Tudo curto e suave; quem pediu "reduzir movimento" no aparelho não vê nada disso. */
  const calmo = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const suave = "cubic-bezier(.2,.7,.2,1)";

  // Troca de página: se o menu já está grudado no topo (página rolada), logo, menu e conteúdo antigo
  // não deslizam de fora da tela; eles só desbotam com o resto. No topo, o logo e o menu deslizam.
  addEventListener("pageswap", (e) => {
    if (!e.viewTransition || !topo) return;
    if (scrollY > 8 && topo.getBoundingClientRect().top <= 1) {
      [".topo-logo", ".barra", "main"].forEach((s) => { const el = document.querySelector(s); if (el) el.style.viewTransitionName = "none"; });
    }
  });
  addEventListener("pageshow", () => {
    [".topo-logo", ".barra", "main"].forEach((s) => { const el = document.querySelector(s); if (el) el.style.viewTransitionName = ""; });
  });

  // Clique fofo: o elemento afunda ao toque e volta com um quique leve.
  // O menu e o logo ficam de fora: eles participam da transição de página e não podem ser fotografados no meio do quique.
  const TOCAVEIS = ".botao, .filtro, .obra, .produto-foto, .caixa-btn, .zap, .opcoes span, .faixa-cab > a";
  // No toque (celular), o aperto só começa depois de 90 ms e é cancelado se o dedo se mover:
  // assim, rolar a página por cima de uma imagem não faz ela encolher.
  if (!calmo) {
    let apertado = null, pendente = null;
    const afundar = (el) => {
      apertado = el;
      const a = el.animate([{ transform: "scale(1)" }, { transform: "scale(.95)" }], { duration: 110, easing: "ease-out", fill: "forwards" });
      a.id = "aperto";
    };
    const largar = (quique) => {
      if (!apertado) return;
      const el = apertado;
      apertado = null;
      el.getAnimations().forEach((a) => a.id === "aperto" && a.cancel());
      if (quique) el.animate([{ transform: "scale(.95)" }, { transform: "scale(1.025)", offset: 0.55 }, { transform: "scale(1)" }], { duration: 420, easing: suave });
    };
    const limpar = () => { if (pendente) { clearTimeout(pendente.t); pendente = null; } };
    addEventListener("pointerdown", (e) => {
      const el = e.target.closest(TOCAVEIS);
      if (!el || e.button > 0) return;
      limpar();
      if (e.pointerType === "touch") pendente = { el, x: e.clientX, y: e.clientY, t: setTimeout(() => { afundar(el); pendente = null; }, 90) };
      else afundar(el);
    });
    addEventListener("pointermove", (e) => {
      if (pendente && Math.hypot(e.clientX - pendente.x, e.clientY - pendente.y) > 8) limpar();
    }, { passive: true });
    addEventListener("pointerup", () => {
      if (pendente) { const el = pendente.el; limpar(); afundar(el); } // toque rápido: aperta e já solta com o quique
      largar(true);
    });
    addEventListener("pointercancel", () => { limpar(); largar(false); }); // virou rolagem: volta sem quique
    addEventListener("dragstart", () => { limpar(); largar(false); });
  }

  // Seções aparecem ao entrar na tela. Só o que ainda está abaixo da dobra é escondido,
  // então nada pisca no carregamento e, sem JavaScript, tudo aparece normalmente.
  const observador = !calmo && "IntersectionObserver" in window
    ? new IntersectionObserver((entradas) => {
        entradas.forEach((e) => {
          if (!e.isIntersecting) return;
          e.target.classList.add("visivel");
          observador.unobserve(e.target);
        });
      }, { rootMargin: "0px 0px -6% 0px", threshold: 0.06 })
    : null;
  function revelar(els) {
    if (!observador) return;
    const porPai = new Map();
    const novos = els.filter((el) => el.getBoundingClientRect().top >= innerHeight * 0.94);
    // esconde de uma vez (sem transição); a transição só vale para o aparecer
    novos.forEach((el) => {
      const i = porPai.get(el.parentElement) || 0;
      porPai.set(el.parentElement, i + 1);
      el.style.setProperty("--i", i % 4); // escalona até 4 itens lado a lado
      el.style.transition = "none";
      el.classList.add("revela");
    });
    if (novos.length) void novos[0].offsetHeight;
    novos.forEach((el) => {
      el.style.transition = "";
      observador.observe(el);
    });
  }
  const REVELAVEIS = [
    ".vitrine .faixa-cab", ".produto", ".vitrine-cta", ".secao > .faixa-cab", "[data-faixa] > .obra",
    ".como-cab > *", ".passos > li", ".como-fim",
    ".cabeca-pagina", ".cartao", ".bloco", ".regras > li", ".nao-faco", ".form", ".aviso", ".locais + .intro",
    ".retrato", ".texto", ".fatos", ".secao .duas > img", ".processo-txt", ".video", ".historia > h2", ".historia-card", ".coelho-dac",
    ".rodape-cols > *", ".rodape-fim",
  ].join(",");

  const obras = window.OBRAS ? window.OBRAS.series : [];
  const porSlug = Object.fromEntries(obras.map((s) => [s.slug, s]));

  function legendaDe(s, it) {
    const partes = [];
    if (it.legenda) partes.push(it.legenda + (it.ano ? ` · ${it.ano}` : ""));
    if (s.slug === "tattoos" && it.grupo) partes.push(it.grupo.toLowerCase() + (it.cicatrizada ? " · cicatrizada" : ""));
    else if (it.grupo && !it.legenda) partes.push(it.grupo);
    return partes.join(" · ");
  }

  function botaoObra(s, it, i, lista, galeria = false) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = galeria ? "obra solta" : "obra";
    const leg = legendaDe(s, it);
    b.setAttribute("aria-label", `Ampliar: ${s.titulo}${leg ? ", " + leg : ""}`);
    const img = galeria ? new Image(it.w, it.h) : new Image(800, 1000);
    img.alt = "";
    img.loading = i < 8 ? "eager" : "lazy";
    img.decoding = "async";
    img.addEventListener("load", () => b.classList.add("pronta"), { once: true });
    img.src = galeria ? it.m : it.t;
    if (img.complete) b.classList.add("pronta");
    b.append(img);
    if (leg) {
      const e = document.createElement("span");
      e.className = "etq";
      e.textContent = leg;
      b.append(e);
    }
    b.addEventListener("click", () => abrir(lista, i));
    return b;
  }

  /* ---------- visualização ampliada ---------- */
  let caixa, atual = [], pos = 0, arrastou = false;
  function montarCaixa() {
    caixa = document.createElement("dialog");
    caixa.className = "caixa";
    caixa.setAttribute("aria-label", "Obra ampliada");
    caixa.innerHTML = `
      <div class="caixa-topo"><span class="caixa-cont" aria-live="polite"></span>
        <button class="caixa-btn" data-fechar aria-label="Fechar">✕</button></div>
      <div class="caixa-palco">
        <button class="caixa-btn caixa-nav ant" aria-label="Anterior">←</button>
        <img alt="">
        <button class="caixa-btn caixa-nav prox" aria-label="Próxima">→</button>
      </div>
      <div class="caixa-rodape"><p class="caixa-legenda"></p></div>`;
    document.body.append(caixa);
    caixa.querySelector("[data-fechar]").onclick = fechar;
    caixa.addEventListener("cancel", (e) => { e.preventDefault(); fechar(); }); // tecla Esc
    caixa.querySelector(".caixa-palco img").addEventListener("load", (e) => e.target.classList.remove("trocando"));
    caixa.querySelector(".ant").onclick = () => ir(-1);
    caixa.querySelector(".prox").onclick = () => ir(1);
    caixa.addEventListener("click", (e) => {
      if (arrastou) { arrastou = false; return; } // o arrasto não conta como toque para fechar
      if (e.target === caixa || e.target.classList.contains("caixa-palco")) fechar();
    });
    caixa.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") ir(-1);
      if (e.key === "ArrowRight") ir(1);
    });
    // Arrastar: a imagem acompanha o dedo; soltando longe (ou rápido) troca, perto volta para o lugar.
    const palco = caixa.querySelector(".caixa-palco");
    const foto = palco.querySelector("img");
    let x0 = null, y0 = 0, t0 = 0, dx = 0;
    palco.addEventListener("pointerdown", (e) => {
      if (e.target.closest(".caixa-btn") || atual.length < 2) return;
      x0 = e.clientX; y0 = e.clientY; t0 = performance.now(); dx = 0; arrastou = false;
    });
    palco.addEventListener("pointermove", (e) => {
      if (x0 === null) return;
      dx = e.clientX - x0;
      if (!arrastou && Math.abs(dx) > 8 && Math.abs(dx) > Math.abs(e.clientY - y0)) {
        arrastou = true;
        try { palco.setPointerCapture(e.pointerId); } catch {}
        foto.getAnimations().forEach((a) => a.cancel());
      }
      if (arrastou) {
        foto.style.transform = `translateX(${dx}px)`;
        foto.style.opacity = String(1 - Math.min(Math.abs(dx) / 700, 0.35));
      }
    });
    const soltarFoto = (e) => {
      if (x0 === null) return;
      x0 = null;
      if (!arrastou) return;
      const rapido = Math.abs(dx) / Math.max(performance.now() - t0, 1) > 0.45;
      if (Math.abs(dx) > 70 || (rapido && Math.abs(dx) > 24)) ir(dx < 0 ? 1 : -1, dx);
      else {
        const de = foto.style.transform;
        foto.style.transform = ""; foto.style.opacity = "";
        if (!calmo) foto.animate([{ transform: de }, { transform: "none" }], { duration: 260, easing: suave });
      }
    };
    palco.addEventListener("pointerup", soltarFoto);
    palco.addEventListener("pointercancel", soltarFoto);
    caixa.addEventListener("close", () => { document.documentElement.style.overflow = ""; });
  }
  function fechar() {
    if (!caixa.open) return;
    if (calmo) return caixa.close();
    caixa.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 160, easing: "ease-in" }).finished.then(() => caixa.close());
  }
  function mostrar() {
    const { s, it } = atual[pos];
    const img = caixa.querySelector(".caixa-palco img");
    if (img.getAttribute("src") !== it.g) img.classList.add("trocando");
    img.src = it.g;
    if (img.complete) img.classList.remove("trocando");
    img.width = it.w || 1600;
    img.height = it.h || 2000;
    img.alt = `${s.titulo}${it.legenda ? ": " + it.legenda : ""}`;
    caixa.querySelector(".caixa-cont").textContent = `${pos + 1} / ${atual.length}`;
    const leg = legendaDe(s, it);
    caixa.querySelector(".caixa-legenda").innerHTML = "";
    const t = document.createElement("span");
    t.textContent = leg || s.titulo;
    const sm = document.createElement("small");
    sm.textContent = leg ? s.titulo : "";
    caixa.querySelector(".caixa-legenda").append(t, sm);
    // pré-carrega as vizinhas nos dois sentidos
    [1, -1].forEach((k) => { const v = atual[(pos + k + atual.length) % atual.length]; if (v) new Image().src = v.it.g; });
  }
  // Troca com deslize: a nova entra pelo lado de onde o dedo "puxou" (ou da seta).
  function ir(d, deArrasto = 0) {
    pos = (pos + d + atual.length) % atual.length;
    const foto = caixa.querySelector(".caixa-palco img");
    foto.style.transform = ""; foto.style.opacity = "";
    mostrar();
    if (calmo) return;
    foto.getAnimations().forEach((a) => a.cancel());
    const inicio = d * Math.max(60, Math.min(Math.abs(deArrasto) * 0.6, 140));
    foto.animate([{ transform: `translateX(${inicio}px)`, opacity: 0 }, { transform: "none", opacity: 1 }], { duration: 340, easing: suave });
  }
  function abrir(lista, i) {
    if (!caixa) montarCaixa();
    atual = lista;
    pos = i;
    mostrar();
    document.documentElement.style.overflow = "hidden";
    caixa.showModal();
  }

  /* ---------- página Trabalhos ---------- */
  const alvo = document.querySelector("[data-trabalhos]");
  if (alvo && obras.length) {
    const visiveis = obras.filter((s) => !s.oculta);
    const filtros = document.querySelector("[data-filtros]");
    visiveis.forEach((s) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "filtro";
      b.dataset.slug = s.slug;
      b.textContent = s.titulo;
      b.onclick = () => {
        if (b.getAttribute("aria-pressed") === "true") return;
        history.replaceState(null, "", "#" + s.slug);
        trocar(s.slug);
      };
      filtros.append(b);
    });

    /* Linhas justificadas, como no portfólio: a obra aparece inteira, todas as imagens de uma linha têm a
       mesma altura e a linha fecha exatamente na largura da coluna. A altura-alvo acompanha a tela. */
    function alturaAlvo(largura) {
      if (largura < 420) return 168;
      if (largura < 640) return 190;
      if (largura < 900) return 210;
      if (largura < 1200) return 250;
      return 290;
    }
    function justificar(galeria) {
      const largura = galeria.clientWidth;
      if (!largura) return;
      const vao = largura < 640 ? 6 : 10;
      const alvoH = alturaAlvo(largura);
      const obrasEl = [...galeria.querySelectorAll(".obra")];
      // proporção limitada para panoramas e verticais extremas não virarem tiras
      const razao = (el) => Math.min(2.4, Math.max(0.45, Number(el.dataset.razao)));
      const alturaDe = (els) => (largura - vao * (els.length - 1)) / els.reduce((s, el) => s + razao(el), 0);

      // 1. Monta as linhas. Cada uma quebra no ponto em que a altura fica mais perto do alvo:
      //    com a obra atual (linha mais baixa) ou sem ela (linha mais alta, e a obra abre a próxima).
      const linhas = [];
      let linha = [];
      obrasEl.forEach((el) => {
        linha.push(el);
        const soma = linha.reduce((s, e) => s + razao(e), 0);
        if (soma * alvoH + vao * (linha.length - 1) < largura) return;
        const hSem = linha.length > 1 ? alturaDe(linha.slice(0, -1)) : Infinity;
        if (Math.abs(hSem - alvoH) < Math.abs(alturaDe(linha) - alvoH)) {
          linhas.push(linha.slice(0, -1));
          linha = [el];
        } else {
          linhas.push(linha);
          linha = [];
        }
      });

      // 2. Sobra no fim: se esticada ficaria desproporcional, tenta juntar à linha anterior;
      //    se nem assim ficar bom, mantém a altura-alvo e centraliza.
      let alturaUltima = null;
      if (linha.length) {
        const hSozinha = alturaDe(linha);
        if (hSozinha <= alvoH * 1.6) linhas.push(linha);
        else if (linhas.length && alturaDe([...linhas[linhas.length - 1], ...linha]) >= alvoH * 0.62) {
          linhas[linhas.length - 1].push(...linha);
        } else {
          linhas.push(linha);
          alturaUltima = alvoH;
        }
      }

      // 3. Desenha
      galeria.replaceChildren();
      linhas.forEach((els, i) => {
        const h = i === linhas.length - 1 && alturaUltima ? alturaUltima : alturaDe(els);
        const div = document.createElement("div");
        div.className = i === linhas.length - 1 && alturaUltima ? "galeria-linha curta" : "galeria-linha";
        div.style.gap = vao + "px";
        els.forEach((el) => {
          el.style.width = (razao(el) * h).toFixed(2) + "px";
          el.style.height = h.toFixed(2) + "px";
          div.append(el);
        });
        galeria.append(div);
      });
      galeria.style.setProperty("--vao", vao + "px");
    }
    const galerias = new Set();
    let ultimaLargura = 0;
    new ResizeObserver(() => {
      const w = alvo.clientWidth;
      if (Math.abs(w - ultimaLargura) < 2) return;
      ultimaLargura = w;
      galerias.forEach(justificar);
    }).observe(alvo);

    // Arquivo de acervo: peças escritas à mão no <template id="acervo"> de trabalhos.html
    const modeloAcervo = document.getElementById("acervo");
    if (modeloAcervo) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "filtro";
      b.dataset.slug = "acervo";
      b.textContent = "Arquivo de acervo";
      b.onclick = () => {
        if (b.getAttribute("aria-pressed") === "true") return;
        history.replaceState(null, "", "#acervo");
        trocar("acervo");
      };
      filtros.append(b);
    }
    function renderAcervo(rolar) {
      filtros.querySelectorAll(".filtro").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.slug === "acervo")));
      const ativo = filtros.querySelector('[data-slug="acervo"]');
      filtros.scrollTo({ left: ativo.offsetLeft - (filtros.clientWidth - ativo.offsetWidth) / 2, behavior: rolar ? "smooth" : "auto" });
      alvo.replaceChildren();
      galerias.clear();
      const cab = document.createElement("header");
      cab.className = "serie-cab";
      cab.innerHTML = "<h2>Arquivo de acervo</h2><p>Registro das peças que fazem parte do acervo para exposição.</p>";
      alvo.append(cab, modeloAcervo.content.cloneNode(true));
      // cada peça amplia as próprias fotos (capa + galeria) na visualização ampliada
      alvo.querySelectorAll(".peca").forEach((peca) => {
        const titulo = peca.querySelector(".peca-titulo")?.textContent.trim() || "Arquivo de acervo";
        const botoes = [...peca.querySelectorAll("[data-ampliar]")];
        const lista = botoes.map((btn) => {
          const img = btn.querySelector("img");
          return { s: { slug: "acervo", titulo }, it: { g: btn.dataset.ampliar, w: img?.width, h: img?.height } };
        });
        botoes.forEach((btn, i) => btn.addEventListener("click", () => abrir(lista, i)));
      });
      document.title = "Arquivo de acervo · Trabalhos · DAC ART INK";
      if (rolar) {
        const y = alvo.getBoundingClientRect().top + scrollY - (parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--altura-topo")) || 64) - filtros.offsetHeight - 8;
        if (y < scrollY) scrollTo({ top: y, behavior: calmo ? "auto" : "smooth" });
      }
      revelar([...alvo.querySelectorAll(".peca")]);
    }

    function render(slug, rolar) {
      if (slug === "acervo" && modeloAcervo) return renderAcervo(rolar);
      const s = porSlug[slug] && !porSlug[slug].oculta ? porSlug[slug] : visiveis[0];
      filtros.querySelectorAll(".filtro").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.slug === s.slug)));
      const ativo = filtros.querySelector(`[data-slug="${s.slug}"]`);
      filtros.scrollTo({ left: ativo.offsetLeft - (filtros.clientWidth - ativo.offsetWidth) / 2, behavior: rolar ? "smooth" : "auto" });
      alvo.replaceChildren();
      galerias.clear();

      const cab = document.createElement("header");
      cab.className = "serie-cab";
      const h = document.createElement("h2");
      h.textContent = s.titulo;
      cab.append(h);
      if (s.texto) {
        const p = document.createElement("p");
        p.textContent = s.texto;
        cab.append(p);
      }
      alvo.append(cab);

      // Nas tattoos o grupo é a técnica e aparece na legenda; nas outras séries cada grupo vira um bloco com título.
      const usaGrupos = s.slug !== "tattoos" && s.itens.some((i) => i.grupo);
      const grupos = usaGrupos ? [...new Set(s.itens.map((i) => i.grupo || ""))] : [""];
      const blocos = grupos.map((g) => ({ g, itens: usaGrupos ? s.itens.filter((i) => (i.grupo || "") === g) : s.itens }));
      const lista = blocos.flatMap((b) => b.itens.map((it) => ({ s, it })));
      let n = 0;
      blocos.forEach(({ g, itens }) => {
        const bloco = document.createElement("section");
        bloco.className = "grupo";
        if (g) {
          const gt = document.createElement("h3");
          gt.className = "grupo-titulo";
          gt.textContent = g;
          bloco.append(gt);
          bloco.setAttribute("aria-label", g);
        }
        const galeria = document.createElement("div");
        galeria.className = "galeria";
        itens.forEach((it) => {
          const el = botaoObra(s, it, n++, lista, true);
          el.dataset.razao = (it.w / it.h).toFixed(4);
          galeria.append(el);
        });
        bloco.append(galeria);
        alvo.append(bloco);
        galerias.add(galeria);
        justificar(galeria);
      });

      document.title = `${s.titulo} · Trabalhos · DAC ART INK`;
      if (rolar) {
        const y = alvo.getBoundingClientRect().top + scrollY - (parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--altura-topo")) || 64) - filtros.offsetHeight - 8;
        if (y < scrollY) scrollTo({ top: y, behavior: calmo ? "auto" : "smooth" });
      }
      revelar([...alvo.querySelectorAll(".grupo")]);
    }
    // Troca de série: a atual sai num fade rápido e a nova entra subindo de leve.
    let trocando = null;
    function trocar(slug) {
      if (calmo || !alvo.animate) return render(slug, true);
      trocando?.cancel();
      trocando = alvo.animate([{ opacity: 1 }, { opacity: 0, transform: "translateY(6px)" }], { duration: 140, easing: "ease-in", fill: "forwards" });
      trocando.finished.then(() => {
        render(slug, true);
        trocando.cancel();
        trocando = null;
        alvo.animate([{ opacity: 0, transform: "translateY(12px)" }, { opacity: 1, transform: "none" }], { duration: 420, easing: suave });
      }).catch(() => {});
    }
    render(location.hash.slice(1), false);
    addEventListener("hashchange", () => trocar(location.hash.slice(1)));
  }

  /* ---------- faixas de destaque (home e orçamento) ---------- */
  document.querySelectorAll("[data-faixa]").forEach((el) => {
    const [slug, qtd] = el.dataset.faixa.split(":");
    const s = porSlug[slug];
    if (!s) return;
    const itens = s.itens.slice(0, Number(qtd) || s.itens.length);
    const lista = itens.map((it) => ({ s, it }));
    itens.forEach((it, i) => el.append(botaoObra(s, it, i + 8, lista)));
  });

  /* ---------- orçamento ---------- */
  const form = document.querySelector("[data-orcamento]");
  if (form) {
    const erro = form.querySelector(".erro");
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const d = new FormData(form);
      const faltando = [];
      if (!d.get("nome")?.trim()) faltando.push("seu nome");
      if (!d.get("ideia")?.trim()) faltando.push("a ideia");
      if (!d.get("aceite")) faltando.push("a confirmação sobre o sinal");
      if (faltando.length) {
        erro.textContent = "Falta preencher: " + faltando.join(", ") + ".";
        form.querySelector(!d.get("nome")?.trim() ? "#nome" : !d.get("ideia")?.trim() ? "#ideia" : "#aceite").focus();
        return;
      }
      erro.textContent = "";
      const campo = (nome, rotulo) => {
        const v = (d.get(nome) || "").trim();
        return v ? [`*${rotulo}:* ${v}`] : [];
      };
      const linhas = [
        "Oi, Dani! Quero um orçamento de tattoo.",
        "",
        ...campo("nome", "Nome"),
        ...campo("ideia", "Ideia"),
        ...campo("tipo", "Tipo"),
        ...campo("local", "Local do corpo"),
        ...campo("cor", "Cor"),
        ...campo("cidade", "Cidade"),
        "",
        "Li as regras do sinal e os cuidados.",
      ];
      const url = `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(linhas.join("\n"))}`;
      window.open(url, "_blank", "noopener");
    });
  }

  /* ---------- vídeos do processo: tocam mudos só enquanto estão na tela ---------- */
  document.querySelectorAll("video[data-video]").forEach((v) => {
    if (calmo || !("IntersectionObserver" in window)) { v.controls = true; v.preload = "metadata"; return; }
    new IntersectionObserver(([e]) => {
      if (e.isIntersecting) v.play().catch(() => { v.controls = true; });
      else v.pause();
    }, { threshold: 0.35 }).observe(v);
  });

  document.querySelectorAll("[data-ano]").forEach((el) => { el.textContent = new Date().getFullYear(); });

  // Depois que as faixas foram montadas: prepara o aparecimento de tudo o que está abaixo da dobra.
  // Ao voltar para uma página (bfcache), mostra tudo de uma vez.
  revelar([...document.querySelectorAll(REVELAVEIS)]);
  addEventListener("pageshow", (e) => { if (e.persisted) document.querySelectorAll(".revela").forEach((el) => el.classList.add("visivel")); });
})();
