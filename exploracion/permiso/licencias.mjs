// Exploración del tramo «Permiso»: leer la licencia en la página pública de cada fuente integrada, como la ve una persona
// (Chrome sin interfaz, porque las fichas de data.lacity.org y de GeoHub se arman con JavaScript), y compararla con la
// licencia que tomamos de los metadatos de la API (catalogo/F*.json).
// Correr: cd exploracion/permiso && npm install --ignore-scripts && node licencias.mjs
import fs from "node:fs";
import puppeteer from "puppeteer-core";

const RAIZ = new URL("../../", import.meta.url);
const cat = id => JSON.parse(fs.readFileSync(new URL(`catalogo/${id}.json`, RAIZ), "utf8"));
const PAGINAS = {
  F01: "https://data.lacity.org/d/k7nn-b2ep", F03: "https://data.lacity.org/d/2cy6-i7zn", F04: "https://data.lacity.org/d/pi9x-tg5x",
  F06: "https://dof.ca.gov/forecasting/demographics/estimates-e1/", F07: "https://www.census.gov/data/developers/about/terms-of-service.html",
  F09: "https://bikeshare.metro.net/about/data/", F10: "https://www.openstreetmap.org/copyright",
  F11: "https://dumps.wikimedia.org/other/pageviews/readme.html",
  F12: "https://geohub.lacity.org/datasets/76104f230e384f38871eb3c4782f903d/about",
  F18: "https://geohub.lacity.org/datasets/031d488e158144d0b3aecaa9c888b7b3/about",
  F19: "https://geohub.lacity.org/datasets/924f1b2e8df642f38a6dcbcf3c7b1709/about",
};
// Frases de licencia que buscamos en el texto visible de la página
const PATRON = /[^.\n]{0,90}(licen[cs]e|licencia|creative commons|\bCC0\b|\bCC BY\b|ODbL|public domain|terms of (use|service))[^.\n]{0,110}/gi;
const norm = s => s.toLowerCase().replace(/\s+/g, " ").trim();
const salida = [];
const di = s => { console.log(s); salida.push(s); };

const b = await puppeteer.launch({ executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless: true });
for (const [id, url] of Object.entries(PAGINAS)) {
  const api = cat(id).licencia;
  const p = await b.newPage();
  let texto = "", estado = "", largo = 0;
  try {
    const r = await p.goto(url, { waitUntil: "networkidle2", timeout: 60000 });
    await new Promise(r => setTimeout(r, url.includes("geohub") ? 12000 : 2500));  // Hub tarda más en pintar la ficha
    estado = String(r.status());
    // GeoHub pinta la ficha dentro de shadow DOM: se recorre también el texto de cada shadowRoot
    texto = await p.evaluate(() => { const partes = [];
      const recorre = n => { if (n.shadowRoot) recorre(n.shadowRoot); for (const h of n.children || []) recorre(h); };
      const junta = r => { partes.push(r.innerText || [...r.childNodes].map(x => x.innerText || x.textContent || "").join("\n")); };
      junta(document.body); const pila = [document.body];
      while (pila.length) { const n = pila.pop(); if (n.shadowRoot) { junta(n.shadowRoot); pila.push(...n.shadowRoot.querySelectorAll("*")); } pila.push(...(n.children || [])); }
      // una licencia también puede verse como ícono: se suma el texto alternativo de imágenes y etiquetas aria
      document.querySelectorAll("img[alt], [aria-label]").forEach(e => partes.push(e.getAttribute("alt") || e.getAttribute("aria-label")));
      return partes.join("\n"); });
    largo = texto.length;
  } catch (e) { estado = "error: " + e.message.slice(0, 80); }
  await p.close();
  // «License» como rótulo con el valor en la línea siguiente (fichas de Socrata y de Hub)
  const rotulo = [...texto.matchAll(/(?:^|\n)\s*Licen[cs]e\s*\n+\s*([^\n]{3,160})/gi)].map(m => "License: " + m[1].trim());
  const frases = [...new Set([...rotulo, ...(texto.match(PATRON) || []).map(x => x.replace(/\s+/g, " ").trim())])].slice(0, 4);
  const conLicencia = api !== "no declara";
  // si los metadatos citan frases entre comillas (F07), se comparan esas frases; si no, el texto de la licencia
  const citas = [...api.matchAll(/"([^"]{20,})"/g)].map(m => norm(m[1]).replace(/^this product uses/, "this product uses"));
  const recortada = norm(api.replace(/^This data is provided as is with no warranty of any kind\. /, "")).slice(0, 60);
  const hallada = citas.length ? citas.every(c => norm(texto).includes(c.slice(0, 60))) : norm(texto).includes(recortada);
  let veredicto;
  if (!texto) veredicto = "no se pudo leer la página";
  else if (conLicencia) veredicto = hallada ? "coincide: la página trae el mismo texto que los metadatos" : "DISCREPA: los metadatos traen una licencia que la página no muestra igual";
  else veredicto = frases.some(f => /creative commons|\bCC0\b|\bCC BY\b|ODbL|public domain/i.test(f)) ? "DISCREPA: los metadatos no declaran, pero la página nombra una licencia" : "coincide: ninguna de las dos declara licencia";
  di(`${id} · HTTP ${estado} · ${largo} caracteres leídos · ${url}`);
  di(`   metadatos (API): ${api.slice(0, 120)}`);
  di(`   página: ${frases.length ? frases.join(" | ").slice(0, 300) : "(ninguna frase de licencia en el texto visible)"}`);
  di(`   → ${veredicto}`);
}
await b.close();
fs.writeFileSync(new URL("salida.txt", import.meta.url), salida.join("\n") + "\n");
