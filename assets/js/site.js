/* DAC ART INK: grade de obras, visualização ampliada e orçamento pelo WhatsApp. */
(() => {
  const WHATSAPP = "5512996436334";

  const topo = document.querySelector(".topo");
  const medir = () => topo && document.documentElement.style.setProperty("--altura-topo", topo.offsetHeight + "px");
  medir();
  addEventListener("resize", medir);

  const obras = window.OBRAS ? window.OBRAS.series : [];
  const porSlug = Object.fromEntries(obras.map((s) => [s.slug, s]));

  function legendaDe(s, it) {
    const partes = [];
    if (it.legenda) partes.push(it.legenda + (it.ano ? ` · ${it.ano}` : ""));
    if (s.slug === "tattoos" && it.grupo) partes.push(it.grupo.toLowerCase() + (it.cicatrizada ? " · cicatrizada" : ""));
    else if (it.grupo && !it.legenda) partes.push(it.grupo);
    return partes.join(" · ");
  }

  function botaoObra(s, it, i, lista) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "obra";
    const leg = legendaDe(s, it);
    b.setAttribute("aria-label", `Ampliar: ${s.titulo}${leg ? ", " + leg : ""}`);
    const img = new Image(800, 1000);
    img.src = it.t;
    img.alt = "";
    img.loading = i < 8 ? "eager" : "lazy";
    img.decoding = "async";
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
  let caixa, atual = [], pos = 0;
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
    caixa.querySelector("[data-fechar]").onclick = () => caixa.close();
    caixa.querySelector(".ant").onclick = () => ir(-1);
    caixa.querySelector(".prox").onclick = () => ir(1);
    caixa.addEventListener("click", (e) => { if (e.target === caixa || e.target.classList.contains("caixa-palco")) caixa.close(); });
    caixa.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") ir(-1);
      if (e.key === "ArrowRight") ir(1);
    });
    let x0 = null;
    const palco = caixa.querySelector(".caixa-palco");
    palco.addEventListener("pointerdown", (e) => { x0 = e.clientX; });
    palco.addEventListener("pointerup", (e) => {
      if (x0 === null) return;
      const dx = e.clientX - x0;
      x0 = null;
      if (Math.abs(dx) > 50) ir(dx < 0 ? 1 : -1);
    });
    caixa.addEventListener("close", () => { document.documentElement.style.overflow = ""; });
  }
  function mostrar() {
    const { s, it } = atual[pos];
    const img = caixa.querySelector(".caixa-palco img");
    img.src = it.g;
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
    const prox = atual[(pos + 1) % atual.length];
    if (prox) new Image().src = prox.it.g;
  }
  function ir(d) { pos = (pos + d + atual.length) % atual.length; mostrar(); }
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
      b.innerHTML = `${s.titulo}<small>${s.itens.length}</small>`;
      b.onclick = () => { history.replaceState(null, "", "#" + s.slug); render(s.slug, true); };
      filtros.append(b);
    });
    function render(slug, rolar) {
      const s = porSlug[slug] && !porSlug[slug].oculta ? porSlug[slug] : visiveis[0];
      filtros.querySelectorAll(".filtro").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.slug === s.slug)));
      filtros.querySelector(`[data-slug="${s.slug}"]`).scrollIntoView({ block: "nearest", inline: "center" });
      alvo.innerHTML = "";
      const cab = document.createElement("header");
      cab.className = "serie-cab";
      const h = document.createElement("h2");
      h.textContent = s.titulo;
      const p = document.createElement("p");
      p.textContent = s.texto || "";
      cab.append(h, p);
      const grade = document.createElement("div");
      grade.className = "grade";
      // Nas tattoos o grupo é a técnica e aparece na legenda; nas outras séries vira subtítulo na grade.
      const usaGrupos = s.slug !== "tattoos" && s.itens.some((i) => i.grupo);
      const grupos = usaGrupos ? [...new Set(s.itens.map((i) => i.grupo || ""))] : [""];
      const ordenados = grupos.flatMap((g) => (usaGrupos ? s.itens.filter((i) => (i.grupo || "") === g) : s.itens));
      const lista = ordenados.map((it) => ({ s, it }));
      let ultimo = null;
      ordenados.forEach((it, n) => {
        if (usaGrupos && it.grupo && it.grupo !== ultimo) {
          const gt = document.createElement("h3");
          gt.className = "grupo-titulo";
          gt.textContent = it.grupo;
          grade.append(gt);
        }
        ultimo = it.grupo;
        grade.append(botaoObra(s, it, n, lista));
      });
      alvo.append(cab, grade);
      document.title = `${s.titulo} · Trabalhos · DAC ART INK`;
      if (rolar) alvo.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    }
    render(location.hash.slice(1), false);
    addEventListener("hashchange", () => render(location.hash.slice(1), true));
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
        ...campo("tamanho", "Tamanho aproximado"),
        ...campo("cor", "Cor"),
        ...campo("tecnica", "Técnica"),
        ...campo("cidade", "Cidade"),
        "",
        "Li as regras do sinal e os cuidados.",
      ];
      const url = `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(linhas.join("\n"))}`;
      window.open(url, "_blank", "noopener");
    });
  }

  document.querySelectorAll("[data-ano]").forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
