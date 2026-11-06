// Cargador: copia lago/municipio.json al construir; la copia queda como un archivo más del sitio publicado
import {readFileSync} from "node:fs";
process.stdout.write(readFileSync(new URL("../../../../lago/municipio.json", import.meta.url)));
