"""Catálogo de fuentes de Los Ángeles · única fuente de verdad.

De aquí salen las fichas catalogo/F*.json y la hoja «1. Fuentes» del diccionario de datos.
Rastreo: 2026-09-27 y 2026-09-28; última prueba de todas las fuentes: 2026-10-05. «probado» es el día en que la fuente respondió de verdad;
si nunca respondió, queda vacío y el intento se dice en la nota.
"""

CAMPOS = ["id", "nombre", "entidad", "tipo", "url", "formato", "acceso", "licencia", "personas",
          "cobertura", "periodo", "frecuencia", "probado", "estado", "hallazgo", "nota"]

FUENTES = [
    ["F01", "LAPD NIBRS Offenses Dataset", "Los Angeles Police Department (portal data.lacity.org)",
     "Entidad pública", "https://data.lacity.org/resource/k7nn-b2ep.json", "JSON", "API sin llave",
     "no declara", "Personas identificables",
     "Ciudad · 21 áreas de LAPD · ubicación por cuadra (hundred block)",
     "Hechos ingresados al RMS desde 2024-03-07; último hecho 2026-09-19", "No se sabe", "2026-10-05",
     "Integrada al lago", "Catálogo del propio portal (API de metadatos), buscando el reemplazo de F02",
     "Una fila por ofensa, no por incidente. Trae dirección por cuadra, hora y marcas de violencia doméstica: "
     "al lago solo llegan conteos por área y por mes. Última carga del portal: 2026-09-29. Carga con rezago: "
     "septiembre llevaba 10.097 ofensas (un mes normal ronda 18.000), por eso la ventana termina en el último "
     "mes completo. Los metadatos no traen licencia (F02 y F03, del mismo portal, sí declaran CC0)."],
    ["F02", "Crime Data from 2020 to 2024", "Los Angeles Police Department (portal data.lacity.org)",
     "Entidad pública", "https://data.lacity.org/resource/2nrs-mtv8.json", "JSON", "API sin llave",
     "Creative Commons 1.0 Universal (Public Domain Dedication)", "Personas identificables",
     "Ciudad · 21 áreas de LAPD · latitud y longitud", "2020-01-01 a 2025-03-28 (fecha de reporte)",
     "Única vez", "2026-10-05", "Descartada", "Se la pedimos a la IA (Claude) en la primera búsqueda",
     "Congelada: LAPD cambió a NIBRS el 2024-03-07 y el último reporte es del 2025-03-28. Además trae edad, "
     "sexo y ascendencia de cada víctima. La reemplaza F01."],
    ["F03", "MyLA311 Cases 2026", "City of Los Angeles · Information Technology Agency", "Entidad pública",
     "https://data.lacity.org/resource/2cy6-i7zn.json", "JSON", "API sin llave",
     "Creative Commons 1.0 Universal (Public Domain Dedication)", "Personas identificables",
     "Ciudad · dirección exacta, latitud y longitud, distrito de consejo, concejo vecinal",
     "2026-01-01 a 2026-10-05", "Diaria", "2026-10-05", "Integrada al lago",
     "Se la pedimos a la IA (Claude); la comprobamos en el portal",
     "No trae nombres, pero sí la dirección exacta de cada solicitud (una recogida de enseres casi siempre es "
     "la casa de quien llama): al lago solo llegan conteos. Hay un conjunto por año: en 2027 cambia el ID. "
     "133.436 solicitudes de 2026 (7,4 %) no traen distrito."],
    ["F04", "Building and Safety - Building Permits Issued from 2020 to Present (N)",
     "Los Angeles Department of Building and Safety (LADBS)", "Entidad pública",
     "https://data.lacity.org/resource/pi9x-tg5x.json", "JSON", "API sin llave", "no declara",
     "Personas identificables", "Ciudad · dirección, número de predio (APN), distrito de consejo, latitud y longitud",
     "2020-01-01 a 2026-10-03", "Diaria", "2026-10-05", "Integrada al lago",
     "Catálogo del propio portal, buscando el reemplazo de F05",
     "El APN se cruza con el registro de propietarios del condado: al lago solo llegan conteos. Los campos "
     "du_changed (cambio en unidades de vivienda) y valuation llegan como texto."],
    ["F05", "LADBS-Permits (vista filtrada)", "LADBS (portal data.lacity.org)", "Entidad pública",
     "https://data.lacity.org/resource/hbkd-qubn.json", "JSON", "API sin llave",
     "Creative Commons Attribution 4.0 International", "Personas identificables", "Ciudad",
     "2013-01-01 a 2023-05-19", "Única vez", "2026-10-05", "Descartada", "Se la pedimos a la IA (Claude)",
     "Vista congelada en mayo de 2023 y con nombre y apellido de solicitantes y contratistas. La reemplaza F04."],
    ["F06", "E-1 Population and Housing Estimates for Cities, Counties, and the State (2026)",
     "California Department of Finance · Demographic Research Unit", "Entidad pública",
     "https://dof.ca.gov/media/docs/forecasting/Demographics/estimates-e1/E-1_2026_InternetVersion.xlsx",
     "XLSX", "Descarga directa", "no declara", "No", "Estado, condados y ciudades de California",
     "Estimaciones al 2025-01-01 y al 2026-01-01", "Anual", "2026-10-05", "Integrada al lago",
     "Búsqueda propia de una fuente sin llave, porque F07 la pide",
     "Publicado el 2026-05-01. Trae dos filas «Los Angeles»: el condado (9.837.286) y la ciudad (3.806.201). "
     "El script exige que sean dos y toma la ciudad; la verificación comprueba el rango."],
    ["F07", "American Community Survey 5-Year Estimates (API)", "U.S. Census Bureau", "Entidad pública",
     "https://api.census.gov/data/2024/acs/acs5?get=NAME,B13016_001E,B13016_002E&for=place:44000&in=state:06",
     "JSON", "API con llave gratuita", 'Census Bureau API Terms of Service (census.gov/data/developers/about/terms-of-service.html): "You may use the Census Bureau API to develop a service or service to search, display, analyze, retrieve, view and otherwise "get" information from Census Bureau data." Atribución exigida: "This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."', "No",
     "Ciudad (place 06-44000), California, EE. UU. y sectores censales del condado de Los Ángeles", "ACS 2020-2024 (serie desde 2006-2010)",
     "Anual", "2026-10-06", "Integrada al lago", "Se la pedimos a la IA (Claude); la probamos con la llave gratuita",
     'Probada el 2026-10-06 con la llave gratuita (en .env, no en el repositorio). Último lanzamiento: ACS 2020-2024; responden los lanzamientos 2010 a 2024 (2009 da 400; 2025 y 2026 dan 404). B13016_001E = mujeres de 15 a 50 años y B13016_002E = las que tuvieron un nacimiento en los últimos 12 meses. Población por distrito: B01003_001E por sector censal del condado 037 (2.498 sectores) y puntos internos del Gazetteer del Censo (www2.census.gov/geo/docs/maps-data/data/gazetteer/2020_Gazetteer/2020_gaz_tracts_06.txt, 200 OK), asignados a distritos con los límites completos de F12; suma 0,23 % por debajo de la ciudad en el ACS. Son estimaciones con margen de error. Los términos exigen mostrar «This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.»; las tasas por 1.000 mujeres y por 10.000 habitantes las calculamos nosotros.'],
    ["F08", "Census Data by Council District", "City of Los Angeles (portal data.lacity.org)", "Entidad pública",
     "https://data.lacity.org/resource/ucyn-ru6w.json", "JSON", "API sin llave",
     "Creative Commons 1.0 Universal (Public Domain Dedication)", "Solo conteos por zona",
     "15 distritos de consejo (límites anteriores a 2021)", "Censo 2010", "Única vez", "2026-10-05", "Descartada",
     "Catálogo del propio portal",
     "Es el censo de 2010 sobre los distritos viejos (última carga: 2017). No sirve para comparar hoy, y por "
     "eso el lago no tiene población por distrito."],
    ["F09", "Metro Bike Share · GBFS station_status",
     "Los Angeles County Metropolitan Transportation Authority (Metro), operado con BCycle", "Entidad pública",
     "https://gbfs.bcycle.com/bcycle_lametro/station_status.json", "JSON", "API sin llave", "no declara", "No",
     "224 estaciones en las regiones City of LA, Westside y Hollywood", "Foto del momento (last_updated)",
     "Tiempo real", "2026-10-05", "Integrada al lago",
     "Se la pedimos a la IA, que dio una URL equivocada; la correcta salió de bikeshare.metro.net/about/data",
     "El feed se renueva cada 60 s. Las regiones del sistema no son los límites de la ciudad. La página de "
     "datos de Metro no publica una licencia."],
    ["F10", "OpenStreetMap vía Overpass API", "Colaboradores de OpenStreetMap", "Plataforma colaborativa",
     "https://overpass-api.de/api/interpreter", "JSON", "API sin llave", "ODbL", "No",
     "Límite administrativo de la ciudad (relación OSM 207359)", "Estado actual del mapa", "Tiempo real",
     "2026-10-05", "Integrada al lago",
     "Se la pedimos a la IA; la primera prueba (2026-09-27) no llegó al servidor y desde el 2026-09-28 responde",
     "ODbL obliga a atribuir y a compartir igual lo derivado. Cobertura voluntaria: complementa, no reemplaza, "
     "los registros oficiales. La etiqueta population de OSM (4.030.904) no coincide con F06 y no se usa."],
    ["F11", "Vistas mensuales del artículo «Los Ángeles» en Wikipedia en español", "Wikimedia Foundation",
     "Plataforma colaborativa",
     "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/es.wikipedia/all-access/user/Los_%C3%81ngeles/monthly/20250201/20260930",
     "JSON", "API sin llave", "CC0", "No", "Ciudad (artículo)", "2025-02 a 2026-09", "Mensual", "2026-10-05",
     "Integrada al lago", "Es el script base del taller, con la ciudad cambiada",
     "Se comprobó que «Los Ángeles» es un artículo y no una desambiguación. Cuenta personas, no bots. "
     "El mes más alto de la serie es junio de 2025 (34.980)."],
    ["F12", "LA City Council Districts (Adopted 2021)", "City of Los Angeles · LA GeoHub (Bureau of Engineering)",
     "Entidad pública", "https://maps.lacity.org/lahub/rest/services/Boundaries/MapServer/13", "GeoJSON",
     "API sin llave", "no declara", "No", "Los 15 distritos de consejo", "Límites adoptados en 2021",
     "No se sabe", "2026-10-05", "Integrada al lago", "Búsqueda web en LA GeoHub, después de descartar F16",
     "El hub marca la licencia como «none». El campo NAME es el nombre del concejal (cargo público). Se "
     "simplifica a ~300 m y 4 decimales: 15,6 KB."],
    ["F13", "AirNow API", "U.S. Environmental Protection Agency (AirNow)", "Entidad pública",
     "https://docs.airnowapi.org/", "JSON", "API con llave gratuita",
     "«should not be used to formulate or support regulation, trends, guidance, or any other government or "
     "public decision making»", "No", "Estaciones de monitoreo de EE. UU., Canadá y México",
     "Tiempo real y pronósticos", "Tiempo real", "2026-10-05", "Descartada", "Se la pedimos a la IA (Claude)",
     "Pide cuenta, y sus propios términos dicen que los datos son preliminares y no deben usarse para "
     "decisiones públicas: justo lo que haría un concejal con este sistema."],
    ["F14", "Google News RSS · búsqueda «Los Angeles»", "Google", "Empresa privada",
     "https://news.google.com/rss/search?q=Los+Angeles&hl=en-US&gl=US&ceid=US:en", "Otro",
     "Bloquea scripts o pide sesión", "no declara", "Texto libre sin revisar", "Titulares en inglés",
     "Tiempo real", "Tiempo real", "", "Descartada", "Se la pedimos a la IA, siguiendo el ejemplo de Lima",
     "Intento del 2026-09-27: el acceso automatizado fue rechazado por robots.txt. No se esquiva: la «escucha» "
     "se hace con F11."],
    ["F15", "«Transport for Los Angeles API» (api.metro.net/bus/stops)", "Ficha de publicapi.dev atribuida a Metro",
     "No se sabe", "https://api.metro.net/bus/stops", "JSON", "API sin llave", "no declara", "No", "", "",
     "No se sabe", "", "No existe (la inventó la IA)",
     "Apareció en la búsqueda web de la IA, en una ficha de publicapi.dev",
     "Intentos del 2026-09-28 y del 2026-10-05: 404. La ficha parece escrita por un generador automático: describe rutas que Metro "
     "no publica. Los datos reales de Metro están en developer.metro.net."],
    ["F16", "«City Council Districts» (872g-cjhh)", "Otro portal Socrata, no el de Los Ángeles", "No se sabe",
     "https://data.lacity.org/resource/872g-cjhh.geojson", "GeoJSON", "API sin llave", "no declara", "No", "", "",
     "No se sabe", "", "Descartada",
     "Lo propuso la IA, tomado del catálogo federado de Socrata sin filtrar por dominio",
     "Intentos del 2026-09-28 y del 2026-10-05: 404 en data.lacity.org. El catálogo mezcla portales de varias ciudades: un título "
     "que coincide no es la cosa. Los límites reales salen de F12."],
    ["F17", "Echo park lake with lotus flowers and Los Angeles skyline in the background (fotografía)",
     "Alaiben (colaborador de Wikimedia Commons)", "Plataforma colaborativa",
     "https://commons.wikimedia.org/wiki/File:Echo_park_lake_with_lotus_flowers_and_Los_Angeles_skyline_in_the_background.jpg",
     "JPEG", "Descarga directa", "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)",
     "Figuras lejanas, sin rostros identificables", "Echo Park, Los Ángeles (34.0753, -118.2615)", "Tomada el 2019-07-12",
     "Única vez", "2026-10-06", "Integrada a la capa web",
     "Búsqueda propia en la API de Wikimedia Commons (palmeras y horizonte del centro); la licencia se confirmó en la página del archivo",
     "Fondo de la página web, no del lago. Autoría: Alaiben, obra propia, CC BY-SA 4.0 (la página del archivo y el autor aparecen en el pie de la web). "
     "Se redujo a 2400 px de ancho y a JPEG (453 KB): esa copia redimensionada es una adaptación y se comparte bajo la misma licencia. "
     "La gradación de color es solo CSS y no modifica el archivo. Se descartaron otras candidatas: «Dodger Stadium and DTLA» (marca de agua y logotipo) "
     "y «Los Angeles with Mount Baldy» (sin palmeras)."],
]

# Nivel de protección y uso en el sistema, para las fichas del catálogo
USO = {
    "F01": ("solo agregados", "Seguridad: ofensas por área de LAPD y por mes"),
    "F03": ("solo agregados", "Municipio: solicitudes 311 por tipo, distrito y mes"),
    "F04": ("solo agregados", "Vivienda: permisos y unidades netas por distrito y mes"),
    "F06": ("abierto", "Gente: población y viviendas de la ciudad"),
    "F07": ("solo agregados", "Gente: natalidad y población por distrito (tasas per cápita)"),
    "F09": ("abierto", "Movilidad: bicicleta compartida en tiempo real"),
    "F10": ("abierto", "Territorio: equipamientos de la ciudad"),
    "F11": ("abierto", "Escucha: interés en la ciudad desde fuera"),
    "F12": ("abierto", "Territorio: capa de los 15 distritos de consejo"),
    "F17": ("abierto", "Capa web: fotografía de fondo (atribución exigida y compartir igual)"),
}

if __name__ == "__main__":
    import json
    import pathlib
    aqui = pathlib.Path(__file__).parent
    for f in aqui.glob("F*.json"):
        f.unlink()
    for fila in FUENTES:
        d = dict(zip(CAMPOS, fila))
        prot, uso = USO.get(d["id"], ("no se publica", ""))
        ficha = {"id": d["id"], "nombre": d["nombre"], "entidad": d["entidad"], "url": d["url"],
                 "cobertura": d["cobertura"], "vigencia": d["periodo"], "probado": d["probado"] or None,
                 "estado": d["estado"], "licencia": d["licencia"], "personas": d["personas"],
                 "proteccion": prot, "uso": uso, "nota": d["nota"]}
        (aqui / f"{d['id']}.json").write_text(json.dumps(ficha, ensure_ascii=False, indent=1) + "\n",
                                              encoding="utf-8")
    print(f"{len(FUENTES)} fichas en catalogo/")
