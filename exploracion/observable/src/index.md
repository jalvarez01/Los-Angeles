# Solicitudes 311 y natalidad por distrito de consejo

Prototipo de exploración con los mismos datos del sitio: `territorio/distritos_consejo.geojson` (F12), `lago/municipio.json` (F03, F07) y `lago/demografia.json` (F07). Las tasas por distrito son PROXY: la población viene del ACS asignada por sectores censales.

```js
const geo0 = FileAttachment("data/distritos.json").json();
const mu = FileAttachment("data/municipio.json").json();
const dem = FileAttachment("data/demografia.json").json();
```

```js
// d3-geo (y por tanto Plot) lee los anillos según su sentido sobre la esfera; la capa de GeoHub viene al revés y
// sin esto cada distrito se dibuja como «todo el planeta menos el distrito» (un cuadrado negro)
const gira = (g) => g.type === "Polygon" ? g.coordinates.map((r) => [...r].reverse()) : g.coordinates.map((p) => p.map((r) => [...r].reverse()));
const geo = {...geo0, features: geo0.features.map((f) => ({...f, geometry: {...f.geometry, coordinates: gira(f.geometry)}}))};
const t = mu.tablas.solicitudes_por_distrito, c = (n) => t.columnas.indexOf(n);
const tasas = new Map(t.filas.map((f) => [f[0], {tasa: f[c("solicitudes_por_10mil")], moe: f[c("solicitudes_por_10mil_moe")]}]));
const n = dem.tablas.natalidad_por_distrito, cn = (x) => n.columnas.indexOf(x);
const nat = n.filas.map((f) => ({cd: `D${f[0]}`, tasa: f[cn("nacimientos_por_1000")], moe: f[cn("nacimientos_por_1000_moe")], sig: f[cn("nacimientos_por_1000_dif_significativa")]}));
const ciudad = n.referencia_ciudad.nacimientos_por_1000;
```

## Solicitudes 311 por 10.000 habitantes · ${t.vigencia}

```js
display(Plot.plot({
  projection: {type: "mercator", domain: geo}, width: 640, height: 520,
  color: {type: "quantile", n: 5, scheme: "magma", legend: true, label: "solicitudes por 10.000 hab.", tickFormat: ",.0f", width: 420},
  marks: [Plot.geo(geo, {fill: (d) => tasas.get(d.properties.cd).tasa, stroke: "white", strokeWidth: 0.8,
    title: (d) => `Distrito ${d.properties.cd}: ${tasas.get(d.properties.cd).tasa} ± ${tasas.get(d.properties.cd).moe}`, tip: true})]
}))
```

## Natalidad por distrito ± margen de error (90 %) · ${n.vigencia}

La línea punteada es la ciudad (${ciudad[0]} ± ${ciudad[1]}). Si dos barras de error se traslapan, la diferencia no es significativa.

```js
display(Plot.plot({
  width: 640, height: 320, y: {label: "nacimientos por 1.000 mujeres de 15 a 50", grid: true, domain: [0, 65]}, x: {label: null},
  marks: [
    Plot.barY(nat, {x: "cd", y: "tasa", fill: (d) => (d.sig ? "#c4266a" : "#9aa1b0"), sort: {x: null}}),
    Plot.ruleX(nat, {x: "cd", y1: (d) => d.tasa - d.moe, y2: (d) => d.tasa + d.moe, stroke: "black", strokeWidth: 1.5}),
    Plot.ruleY([ciudad[0]], {stroke: "black", strokeDasharray: "4 3"})
  ]
}))
```

Rosado: difiere de la ciudad a 90 %. Gris: no difiere. Fuente F07 · lago probado ${dem.probado}.
