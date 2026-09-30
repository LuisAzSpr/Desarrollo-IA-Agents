# Datos

## Procedencia

- **Fuente:** registros OCDS del SEACE (Sistema Electrónico de Contrataciones del Estado, Perú), publicados en formato CSV aplanado (21 tablas, carpeta `2026`, ~1,4 GB). El prefijo de los `ocid` (`ocds-dgv273-seacev3-…`) identifica la publicación OCDS del Estado peruano; `sources.csv` apunta al buscador público del SEACE v3.
- **No se versionan los CSV crudos** (superan el límite de GitHub). Para regenerar los casos, coloca la carpeta en `../claudego/2026` o define la variable `OCDS_DIR` y ejecuta `python src/construir_casos.py`.
- La estructura de las tablas y sus relaciones está en [`docs/esquema_ocds.md`](../docs/esquema_ocds.md).

## Qué es un caso

Un caso es **un requerimiento real** (`tender_items.description`) de un proceso del SEACE, acompañado de:

| Campo | Origen |
|---|---|
| `requerimiento` | `tender_items.description` (texto publicado por la entidad; se normalizan espacios y `\n`) |
| `contexto_C0` | `main` + `tender_items`: entidad, procedimiento, nomenclatura, categoría, CUBSO, valor referencial del ítem, fecha |
| `contexto_C1` | C0 + resultado del proceso: número de postores (`main.tender_numberOfTenderers`), ganador (`awards_suppliers`) y monto adjudicado del ítem (`awards_items`) |
| `url_bases` | URL de las *Bases Administrativas/Integradas* en `tender_documents` |
| `gold_riesgo`, `gold_senales` | **Asignados por el autor** con la rúbrica de abajo (no vienen en los datos) |
| `fichas/<id>.json` | Ficha 360° del proceso: bases, ítems, postores, ganador, lo adjudicado y contrato |

¿Por qué `tender_items.description` y no las bases? Porque el texto de los requisitos solo está dentro del PDF de las bases, que los CSV enlazan por URL. La descripción del ítem es la parte del requerimiento que sí está en los datos, y es justamente donde aparece la señal más clásica de direccionamiento: la mención de una marca o modelo.

## Rúbrica de etiquetado (la misma que se escribe en P1)

La normativa peruana prohíbe que el requerimiento haga referencia a marcas, modelos o fabricantes que orienten la contratación hacia un proveedor, salvo estandarización aprobada o que no exista otra forma de describir el objeto; en ese caso se agrega "o equivalente" (TUO de la Ley 30225, art. 16, y su reglamento; el principio se mantiene en la Ley 32069).

| Riesgo | Señal | Cuándo |
|---|---|---|
| **alto** | `marca_sin_equivalente` | Exige marca/modelo/fabricante para el bien o servicio que se contrata, sin "o equivalente" y sin decir que es para un equipo que la entidad ya tiene |
| **medio** | `marca_con_equivalente` | Menciona marca/modelo pero admite "o equivalente"/"o similar" |
| **medio** | `compatibilidad_equipo_existente` | La marca aparece porque se compran insumos, repuestos o soporte para un equipo o sistema que la entidad ya posee |
| **bajo** | `ninguna` | Descripción genérica o funcional, sin marcas ni modelos |

La etiqueta evalúa **solo el texto del requerimiento**. Que un proceso haya tenido un solo postor es una bandera roja distinta (de resultado, no de redacción) y por eso se usa como contexto conflictivo en el Experimento 2, no como parte del gold.

## Los 10 casos

| Id | Requerimiento (resumido) | Entidad | Postores | Gold | Dificultad |
|---|---|---|---:|---|---|
| C01 | Switches y access point **de la marca Cisco** | Agencia de Compras de las FF.AA. | 28 | alto | clara |
| C02 | Licencias **Microsoft Office LTSC** Professional Plus 2024 | Escuela de Bellas Artes Diego Quispe Tito (GORE Cusco) | 9 | alto | clara |
| C03 | Licencias de software **Autodesk Autocad** en su última versión | Autoridad Portuaria Nacional | 11 | alto | ambigua |
| C04 | Suscripción Microsoft Office 365 **o equivalente** | FONDEPES | 16 | medio | clara |
| C05 | Soporte de servidores **Oracle o equivalente** | SBS | 1 | medio | clara |
| C06 | Reactivos para **equipo propio Mindray** modelo CL2000i | Hospital General de Jaén | 1 | medio | clara |
| C07 | Tintas **para impresora Epson** WorkForce Pro EM-C800 | Red de Salud Pachitea | 23 | medio | clara |
| C08 | Combustible diésel B5 S50 para unidades vehiculares | Municipalidad Distrital de Florida | 1 | bajo | clara |
| C09 | Hojuela de avena, quinua y kiwicha enriquecida (Vaso de Leche) | Municipalidad Distrital de Rondos | 1 | bajo | clara |
| C10 | 150 kg de flejes de plata con ley de fineza 0,925 | Banco Central de Reserva del Perú | 1 | bajo | ambigua |

**Por qué son adecuados:** son textos reales y recientes (convocatorias de 2025 y 2026), cubren las cuatro señales de la rúbrica y los tres niveles de riesgo, mezclan bienes y servicios de sectores distintos (TI, salud, combustible, alimentos, banca central) e incluyen dos "trampas" (C03: software de marca que podría justificarse por compatibilidad; C10: especificación técnica muy precisa pero estándar y sin marca).

**Diseño del contexto conflictivo (C1):** los casos se eligieron para que el resultado real del proceso apunte **en contra** de la etiqueta: los casos `alto` tuvieron muchos postores (9 a 28), que sugieren competencia; los casos `bajo` tuvieron **un solo postor**, que sugiere direccionamiento; los casos `medio` tienen uno de los dos extremos. `src/construir_casos.py` verifica esta condición con una aserción.

## Ejemplos para el few-shot (Experimento 4, opcional)

No forman parte de los 10 casos evaluados:

- E1 (alto): *ADQUISICIÓN DE COMPUTADORAS MARCA APPLE PARA LA OFICINA DE COMUNICACIONES DE PROMPERÚ*
- E2 (medio, compatibilidad): *ADQUISICION DE 80 ZAPATAS PARA EL TRACTOR ORUGA BULLDOZER D375A B086 KOMATSU…*
