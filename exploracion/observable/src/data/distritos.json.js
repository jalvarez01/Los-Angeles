// Cargador: copia territorio/distritos_consejo.geojson al construir
import {readFileSync} from "node:fs";
process.stdout.write(readFileSync(new URL("../../../../territorio/distritos_consejo.geojson", import.meta.url)));
