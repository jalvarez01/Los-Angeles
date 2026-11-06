// Cargador: copia lago/demografia.json al construir; la copia queda como un archivo más del sitio publicado
import {readFileSync} from "node:fs";
process.stdout.write(readFileSync(new URL("../../../../lago/demografia.json", import.meta.url)));
