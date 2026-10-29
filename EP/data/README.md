# Datos del examen parcial

| Archivo | Qué es |
|---|---|
| `corpus.jsonl` | 55 documentos (uno por proceso real del SEACE) y 426 pasajes |
| `consultas.jsonl` | 22 consultas: 20 con evidencia y 2 de control sin evidencia |
| `qrels.json` | pasajes relevantes de cada consulta (`passage_id`) |
| `referencias.jsonl` | respuesta de referencia de las 12 consultas del experimento 2 |
| `congelamiento.json` | SHA-256 de los cuatro archivos anteriores, guardado antes de correr los experimentos |
| `indice_procesos.jsonl` | datos estructurados de los mismos 55 procesos, para la herramienta del experimento 3 |

## Procedencia

Los documentos salen de los **registros OCDS del SEACE** (Perú) que usamos desde la PC1: CSV aplanados en las carpetas `2024/`, `2025/` y `2026/` de CC-0F4. Cada carpeta agrupa los procesos por el año de su última versión publicada, así que las convocatorias van de 2014 a 2026 aunque las carpetas sean de 2024-2026. Cada documento se identifica por su `ocid` (`ocds-dgv273-seacev3-…`), que se puede buscar en el buscador público del SEACE. La estructura de las tablas está en [`docs/esquema_ocds.md`](../../docs/esquema_ocds.md).

Son datos públicos que el Estado publica como datos abiertos de contrataciones. No encontramos una licencia explícita en los archivos descargados; los usamos solo con fines académicos y citamos la fuente. Los CSV crudos no se versionan (pesan ~1,4 GB por año). El corpus y el índice ya generados sí están en el repositorio, así que los experimentos corren sin los CSV.

## Cómo se arma cada documento

`EP/src/armar_corpus.py` llama a `passages_de` de la PC2 (`pc2/src/construir_corpus.py`), que divide el expediente OCDS de un proceso en pasajes con una plantilla fija:

| Pasaje | Tabla OCDS |
|---|---|
| convocatoria | `main` (entidad, procedimiento, objeto, fecha, valor referencial) |
| ítem (uno por ítem, máximo 8) | `tender_items` (descripción, cantidad, valor, estado) |
| cronograma | `main` (periodos de consultas y de ofertas) |
| documentos | `tender_documents` (títulos) |
| postores | `main.tender_numberOfTenderers` + `tender_tenderers` (5 nombres como máximo) |
| resultado | `awards` + `awards_suppliers` (4 adjudicaciones como máximo, % del valor referencial si hay una sola) |
| contrato | `contracts` (3 como máximo) |

Lo que escribió la entidad (objeto, descripción del ítem) y los nombres de entidades y empresas se copian **tal cual**. Las frases que los rodean ("Número de postores registrados: …", "Buena pro otorgada a …") son de la plantilla, y los montos y fechas se formatean. No hay texto escrito a mano ni generado por un modelo. Limitación: los requisitos completos están en el PDF de las bases, que OCDS solo enlaza, así que el corpus no los tiene (por eso Q22 no tiene evidencia).

## Selección de los 55 procesos

- **E01-E10:** los 10 documentos del corpus de la PC2, para que el examen continúe sobre la misma base. Para E02 (104 ítems) y E08 (27 ítems) se mantiene el ítem objetivo de la PC2.
- **E11-E55:** los demás procesos del benchmark v2 de la PC1 (`data/casos_v2.jsonl`), sin repetir `ocid`. Fueron elegidos en la PC1 por su señal: marca sin equivalente, marca con "o equivalente", compatibilidad con un equipo que la entidad ya tiene o sin marca, con distintos números de postores.

Hay varios pares parecidos a propósito (cuatro compras de Microsoft Office, dos de Adobe, dos procesos con Oracle, dos del mismo hospital de Jaén). Sirven como distractores reales: comparten marca o entidad pero no responden la consulta.

| Doc | ocid (`…seacev3-`) | Nomenclatura | Entidad | Ítems incluidos | Pasajes | Origen |
|---|---|---|---|---|---:|---|
| E01 | 1216035 | LP-ABR-1-2026-OGA-ACFFAA-1 | Agencia De Compras De Las Fuerzas Armadas | 1 de 1 | 7 | pc2:D01, v2:C01 |
| E02 | 1184513 | CONV-PROC-2-2026-UNTRM/PROCIENCI-1 | Universidad Nacional Toribio Rodriguez De Mendoza | 8 de 104 | 14 | pc2:D02, v2:T11 |
| E03 | 1095541 | DIRECTA-PROC-2-2025-SBS-S-1 | Superintendencia De Banca, Seguros Y Afp | 1 de 1 | 7 | pc2:D03, v2:C05 |
| E04 | 2024-1945-10 | AS-SM-2-2024-COFOPRI-1 | Organismo De Formalizacion De La Propiedad Informal | 1 de 1 | 7 | pc2:D04, v2:T19 |
| E05 | 1183945 | DIRECTA-DIRECTA-8-2025-HGJ-1 | Gobierno Regional De Cajamarca-Hospital General De Jaén | 1 de 1 | 7 | pc2:D05, v2:C06 |
| E06 | 1209013 | LP-ABR-1-2026-RSP/OC-1 | Gobierno Regional De Huanuco - Red De Salud Pachitea | 1 de 1 | 7 | pc2:D06, v2:C07 |
| E07 | 1183834 | LP-ABR-5-2025-MDR/CS-1 | Municipalidad Distrital De Rondos | 2 de 2 | 8 | pc2:D07, v2:C09 |
| E08 | 1042389 | SIE-SIE-31-2024-CENARES/ MINSA-1 | Centro Nacional De Abastecimiento De Recursos Estratégicos | 8 de 27 | 14 | pc2:D08, v2:T30 |
| E09 | 1178657 | LP-ABR-27-2025-MML-OGA-OL-1 | Municipalidad Metropolitana De Lima | 1 de 1 | 7 | pc2:D09, v2:T29 |
| E10 | 2024-48-3 | SIE-SIE-1-2024-GRP-ORA-OEC-2 | Gobierno Regional De Piura Sede Central | 8 de 15 | 14 | pc2:D10 |
| E11 | 2025-42031-2 | CP-ABR-2-2025-INACAL-1 | Instituto Nacional De Calidad - Inacal | 1 de 1 | 7 | v2:D01 |
| E12 | 1168281 | LP-ABR-2-2025-PNADP-1 | Programa Nacional De Apoyo Directo A Los Mas Pobres | 1 de 1 | 7 | v2:D02 |
| E13 | 1153035 | LP-ABR-5-2025-IGN-CE-1 | Instituto Geografico Nacional | 1 de 1 | 7 | v2:D03 |
| E14 | 307696 | AS-SM-45-2016-SAN GABAN S.A.-1 | Empresa De Generacion Electrica San Gaban S.A. | 1 de 1 | 7 | v2:D04 |
| E15 | 687785 | DIRECTA-PROC-20-2020-OEC-GR CUSCO-1 | Gobierno Regional De Cusco Sede Central | 6 de 6 | 12 | v2:D05 |
| E16 | 2025-200019-101 | CP-ABR-2-2025-MTC/20-1 | MTC - Proyecto Especial De Infraestructura De Transporte | 1 de 1 | 7 | v2:D06 |
| E17 | 2025-10137-30 | AS-SM-4-2025-DP-1 | Despacho Presidencial | 1 de 1 | 7 | v2:D07 |
| E18 | 1153093 | COMPRE-COMPRE-1-2025-SUSALUD-1 | Superintendencia Nacional De Aseguramiento En Salud | 1 de 1 | 7 | v2:D08 |
| E19 | 2024-15-52 | AS-SM-13-2024-MINEM-1 | Ministerio De Energia Y Minas | 1 de 1 | 7 | v2:D09 |
| E20 | 2022-1962-101 | AS-SM-34-2022-INGEMMET/CS-1 | Instituto Geologico, Minero Y Metalurgico | 1 de 1 | 7 | v2:D10 |
| E21 | 2024-42031-31 | AS-SM-6-2024-INACAL-1 | Instituto Nacional De Calidad - Inacal | 1 de 1 | 7 | v2:D11 |
| E22 | 2023-10141-106 | AS-SM-36-2023-DEVIDA-1 | Comisión Nacional Para El Desarrollo Y Vida Sin Drogas | 1 de 1 | 7 | v2:D12 |
| E23 | 146269 | AMC-CLASICO-5-2015-MDCC-2 | Municipalidad Distrital De Ccapi | 1 de 1 | 7 | v2:D13 |
| E24 | 2024-25-47 | AS-SM-4-2024-IN-OGAF-OAB-1 | Ministerio Del Interior - PNP UE 001 OGA | 2 de 2 | 8 | v2:D14 |
| E25 | 1139426 | DIRECTA-DIRECTA-3-2025-HRVFCH-1 | Gobierno Regional De Amazonas - Hospital De Apoyo | 1 de 1 | 7 | v2:D15 |
| E26 | 1004365 | COMPRE-SM-3-2024-OEC/MPP-1 | Municipalidad Provincial De Piura | 1 de 1 | 7 | v2:D16 |
| E27 | 1134245 | DIRECTA-DIRECTA-1-2025-MINDEF/VRD/DGA/-1 | Ministerio De Defensa | 1 de 1 | 7 | v2:D17 |
| E28 | 2025-10466-39 | AS-SM-10-2025-HRHVM/CS-1 | Gobierno Regional De Huanuco-Hospital De Huanuco | 1 de 1 | 7 | v2:D18 |
| E29 | 323308 | AS-SM-50-2016-OEFA-1 | Organismo De Evaluacion Y Fiscalizacion Ambiental | 1 de 1 | 7 | v2:D19 |
| E30 | 145134 | AMC-SIE-3-2015-MDPM/CEP-1 | Municipalidad Distrital De Pillco Marca | 1 de 1 | 7 | v2:D20 |
| E31 | 2022-1343-38 | LP-SM-4-2022-CS/MDSA-1 | Municipalidad Distrital De Santa Anita | 1 de 1 | 7 | v2:D21 |
| E32 | 2024-255417-40 | AS-SM-24-2024-OEC/MDSA-1 | Municipalidad Distrital De San Antonio | 1 de 1 | 7 | v2:D22 |
| E33 | 2024-45-153 | SIE-SIE-33-2024-GOREMAD/OEC-1 | Gobierno Regional De Madre De Dios Sede Central | 1 de 1 | 7 | v2:D23 |
| E34 | 2024-1002997864-4 | AS-SM-1-2024-GRSM-UGEL-R/OEC-2 | Gobierno Regional De San Martin - UGEL | 2 de 2 | 8 | v2:D24 |
| E35 | 1177957 | LP-ABR-3-2025-UNADQTC-1 | Gobierno Regional De Cusco - Escuela De Bellas Artes | 1 de 1 | 7 | v2:C02 |
| E36 | 2025-200121-10 | LP-ABR-1-2025-APN-1 | MTC - Autoridad Portuaria Nacional | 1 de 1 | 7 | v2:C03 |
| E37 | 1179832 | CP-ABR-12-2025-FONDEPES-1 | Fondo Nacional De Desarrollo Pesquero | 1 de 1 | 7 | v2:C04 |
| E38 | 2026-99-2 | LP-ABR-2-2026-MDF/OC-1 | Municipalidad Distrital De Florida - Pomacochas | 2 de 2 | 8 | v2:C08 |
| E39 | 1152458 | LP-ABR-9-2025-BCRPLIM-1 | Banco Central De Reserva Del Perú | 1 de 1 | 7 | v2:C10 |
| E40 | 1181120 | CP-ABR-41-2025-SUNAT/8B7200-1 | Superintendencia Nacional De Aduanas Y De Administración Tributaria | 1 de 1 | 7 | v2:T12 |
| E41 | 1221986 | RES-PROC-3-2025-RENIEC-4 | Registro Nacional De Identificacion Y Estado Civil | 1 de 1 | 7 | v2:T13 |
| E42 | 1177899 | LP-ABR-2-2025-UNADQTC-1 | Gobierno Regional De Cusco - Escuela De Bellas Artes | 1 de 1 | 7 | v2:T14 |
| E43 | 1202736 | CP-ABR-1-2026-INGEMMET/C-1 | Instituto Geologico, Minero Y Metalurgico | 1 de 1 | 7 | v2:T15 |
| E44 | 2023-10141-67 | AS-SM-22-2023-DEVIDA-1 | Comisión Nacional Para El Desarrollo Y Vida Sin Drogas | 1 de 1 | 7 | v2:T16 |
| E45 | 2024-2525-125 | AS-SM-20-2024-BN-1 | Banco De La Nacion | 1 de 1 | 7 | v2:T17 |
| E46 | 1214462 | DIRECTA-DIRECTA-11-2026-INO-MINSA-1 | Instituto Nacional De Oftalmologia | 3 de 3 | 9 | v2:T18 |
| E47 | 1232809 | DIRECTA-DIRECTA-24-2026-INEN-1 | Instituto Nacional De Enfermedades Neoplasicas | 1 de 1 | 7 | v2:T20 |
| E48 | 2025-2005-45 | CP-ABR-16-2025-SAT-1 | Servicio De Administracion Tributaria De Lima | 1 de 1 | 7 | v2:T21 |
| E49 | 1201784 | RES-PROC-161-2025-RE-1 | Ministerio De Relaciones Exteriores | 6 de 6 | 12 | v2:T22 |
| E50 | 1228163 | DIRECTA-DIRECTA-4-2026-HGJ-1 | Gobierno Regional De Cajamarca-Hospital General De Jaén | 1 de 1 | 7 | v2:T23 |
| E51 | 2026-200022-30 | LP-SM-1-2026-VIVIENDA-OGA-UE-1 | Ministerio De Vivienda, Construcción Y Saneamiento | 5 de 5 | 11 | v2:T24 |
| E52 | 5640 | EXO-PROC-1-2014-PROMPERU | Comision De Promocion Del Peru Para La Exportacion Y El Turismo | 1 de 1 | 7 | v2:T25 |
| E53 | 10474 | ADS-CLASICO-11-2014-CEPO-MDCH-1 | Municipalidad Distrital De Chorrillos | 1 de 1 | 7 | v2:T26 |
| E54 | 1018367 | ABR-PROC-188-2022-OFP / PETROPERU-1 | Petroleos Del Peru S.A. | 1 de 1 | 7 | v2:T27 |
| E55 | 190074 | AMC-CLASICO-10-2015-M.P.VIRU-1 | Municipalidad Provincial De Viru | 1 de 1 | 7 | v2:T28 |

Totales: 55 documentos, 426 pasajes (96 de ítems y 55 de cada uno de los otros seis tipos), de 112 a 390 palabras por documento.

## Consultas y qrels

Las 22 consultas las escribimos nosotros pensando en lo que preguntaría un auditor. **Los qrels se anotaron leyendo los pasajes, antes de correr cualquier sistema**, y no salen de las respuestas de ningún modelo. Luego se congelaron con SHA-256 (`congelamiento.json`, commits `b623b36` y `f59e91d`; el segundo solo hace que el hash no dependa del fin de línea, los datos no cambiaron). Los experimentos verifican esos hashes antes de correr y se detienen si algo cambió.

Criterio: un pasaje es relevante si contiene la evidencia **literal** que pide la consulta. Si la respuesta necesita dos datos que están en pasajes distintos (por ejemplo postores y buena pro), los dos son relevantes.

| Tipo | Consultas | Qué prueba |
|---|---|---|
| señal / señal con negación | Q01, Q02, Q19 | marca con o sin "o equivalente" |
| léxico / código | Q05, Q06, Q07 | códigos exactos (IOARR, 006R01830, 5182-0733) |
| paráfrasis | Q08, Q09 | la consulta no usa las palabras del texto ("asistente virtual" vs "CHATBOT") |
| distractor | Q03, Q10, Q12, Q16, Q17 | hay otro proceso muy parecido (misma marca o misma entidad) |
| multi-pasaje | Q04, Q18 | la respuesta está repartida en varios pasajes |
| resultado / competencia | Q11, Q14, Q20 | postores o buena pro (Q14: el ítem quedó desierto) |
| numérica | Q13 | comparar porcentajes (adjudicado > 130 % del valor referencial) |
| contradicción | Q15 | el objeto dice "o equivalente" y el ítem no |
| control sin evidencia | Q21, Q22 | el corpus no tiene sanciones ni plazos de entrega |

11 consultas son difíciles, 9 de dificultad media y 2 de control. Q21 y Q22 tienen qrels vacíos: no entran en las métricas de recuperación, pero sí en el experimento 2, donde lo correcto es abstenerse.

Decisiones de anotación que conviene saber:

- **Q12:** solo `E50-P05` (pasaje de postores: "Número de postores registrados: 1"). `E50-P06` dice que Siemens ganó, pero no dice que fue el único postor.
- **Q14:** `E19-P02` (el ítem quedó desierto) y `E19-P06` (no hay buena pro registrada). La respuesta es negativa y necesita los dos.
- **Q15:** `E36-P01` (objeto con "o equivalente") y `E36-P02` (ítem sin "o equivalente"). La respuesta correcta es señalar la contradicción.
- **Q18:** los cinco pasajes de ítems de `E51`. Ninguno tiene todas las marcas.
- **Q13:** solo `E48-P06` (adjudicado al 132 %). `E11` (120 %), `E01` (106 %) y `E43` (101 %) también pasan el valor referencial pero no por más de 30 %: son distractores.

## Referencias del experimento 2

`referencias.jsonl` tiene, para las 12 consultas marcadas `exp2`, la respuesta de referencia, los pasajes que la sustentan (subconjunto de los qrels) y los hechos que la respuesta debe contener. También se escribió antes de correr el experimento 2. Sirve para la auditoría manual, no para un puntaje automático.

## Índice de procesos (experimento 3)

`indice_procesos.jsonl` se genera con `EP/src/armar_indice.py` desde los mismos CSV (`src/ocds.py::ficha_proceso`): una fila por `ocid` con valor referencial, número de postores, todos los ítems y las adjudicaciones. A diferencia del corpus, no recorta ítems (E02 tiene sus 104). No forma parte del benchmark de recuperación.
