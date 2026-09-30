# Guía para la defensa oral

Preguntas probables y respuestas cortas, apoyadas en archivos del repositorio. La exposición vale 12 de los 20 puntos: conviene poder abrir el archivo que respalda cada respuesta.

## Guion sugerido (8 min + 2 min de demo)

| Min | Diapositiva | Idea que debe quedar |
|---|---|---|
| 0:00 | 1. Problema y tarea | Los datos OCDS permiten ver el negocio completo; la PC1 aísla una unidad: ¿la redacción de un requerimiento está direccionada? |
| 1:15 | 2. Arquitectura | Cadena corta y verificable: casos reales → prompt → Qwen 0.5B → decoding → JSON → validación → métricas |
| 2:15 | 3. Semanas 1-3 | Causalidad (etiqueta antes que justificación), logits/softmax (sondeo), decoding, KV cache, schema |
| 3:30 | 4. Prompt y salida | Qué cambia entre P0 y P1 (un solo bloque) y los tres niveles de validación |
| 4:45 | 5. Experimentos | Tabla de registro: variable modificada, fija, métrica, resultado |
| 6:15 | 6. Resultados y caso fallido | El modelo responde al prompt, no al caso; caso Cisco |
| 7:15 | 7. Limitación y conclusión | Conclusión proporcional a 10 casos; qué sigue en el proyecto multi-agente |
| 8:00 | Demo | `python src/demo.py --caso C01 --sondeo` (o mostrar un resultado guardado si el tiempo aprieta) |

Para la demo, ten abierta una terminal en la raíz del repositorio y el modelo ya descargado. La primera carga tarda ~5 s y la generación ~20 s en CPU; mientras genera, explica el prompt que se imprimió en pantalla.

## Semana 1 — Transformer, tokens, atención, causalidad

**¿Qué arquitectura tiene el modelo?** Decoder-only (Qwen2ForCausalLM): 24 bloques Transformer, dimensión 896, 14 cabezas de atención para las consultas y 2 para claves y valores (grouped-query attention), RoPE para posiciones y vocabulario de 151 936 tokens. Fuente: `config.json` del modelo y el reporte técnico de Qwen2.5.

**¿Qué es un token aquí?** Una unidad BPE. `alto` es un token, pero `medio` son dos (`med` + `io`) y `bajo` son dos (`b` + `ajo`). Por eso no se puede comparar la probabilidad de las etiquetas mirando un solo token: `sondear_etiqueta` multiplica las probabilidades de todos sus tokens y además exige que la cadena se cierre con un token que empiece con comilla (el BPE de Qwen suele cerrar con `",`).

**¿Por qué un decoder causal no puede usar información futura?** La máscara causal hace que la posición *t* solo atienda a posiciones ≤ *t*. En este JSON, `riesgo` se genera antes que `justificacion`, así que el token de la etiqueta se decide sin haber visto la justificación. La justificación es una racionalización posterior. Evidencia: con P1 el modelo justifica "agrega 'o equivalente'" en C01 (Cisco), cuando el texto no dice eso: primero eligió `medio` y después fabricó una razón compatible con esa etiqueta.

**¿Podrías cambiar el orden de los campos?** Sí: poner `justificacion` primero convierte la salida en algo parecido a razonar antes de responder. Sería un experimento válido para la PC2, cambiando solo el orden y dejando fijo todo lo demás.

## Semana 2 — Logits, softmax, decoding, contexto, KV cache

**¿Qué son los logits?** El vector de puntajes (uno por token del vocabulario, 151 936) que sale de la última capa en cada posición. Softmax los convierte en una distribución de probabilidad: p_i = exp(z_i/T) / Σ_j exp(z_j/T).

**¿Qué muestra el sondeo de logits?** Que la distribución p(alto, medio, bajo) casi no cambia entre casos y sí cambia entre prompts: con P0 "alto" domina en todos los casos y con P1 domina "medio" en todos. El modelo reacciona más al prompt que al requerimiento. Archivo: `results/sondeo_logits.jsonl`, figura `results/figs/sondeo_probabilidades.png`.

**Greedy vs sampling.** Greedy toma el argmax en cada paso: es determinista (se comprobó repitiendo la corrida con otra semilla: mismo texto). Sampling muestrea de la distribución; con T = 0,8 la distribución se afila un poco respecto de T = 1 y top-p = 0,9 descarta la cola de tokens que acumula el último 10 % de probabilidad (Holtzman et al., 2020). `top_k = 0` desactiva top-k para que la única truncación sea top-p.

**¿Por qué con la misma semilla casos distintos dan la misma salida?** Porque las distribuciones de todos los casos son casi iguales (con P1, p(medio) entre 0,54 y 0,76) y la semilla fija la secuencia de números aleatorios. El sampling elige el token cuyo intervalo de probabilidad acumulada contiene ese número; si los intervalos casi no cambian entre casos, el mismo número cae en el mismo token. Por eso la semilla 2 da `bajo` en 8 de 10 casos y la semilla 0 da salidas inválidas en los 10. El acuerdo entre casos con la misma semilla (0,86) supera la estabilidad de un caso entre semillas (0,72).

**¿Por qué el sampling produjo `"medio|ninguna"`?** Después de `medio`, el token más probable es el cierre `",`, pero `|` también tiene probabilidad porque el prompt muestra `"alto|medio|bajo"`. Greedy nunca lo elige; el sampling sí (30 de 50 muestras), y a partir de ahí el modelo sigue copiando el formato. Una decodificación restringida por schema lo impediría.

**¿Qué efecto tiene T = 0,8?** Divide los logits por 0,8 antes del softmax, lo que afila la distribución: en C01, p(`med`) sube de 0,55 (T = 1) a 0,67 (T = 0,8). Aun así, las alternativas conservan probabilidad y aparecen cuando el número aleatorio cae en ellas.

**¿Qué hace el KV cache?** Guarda las claves y valores de las posiciones ya procesadas. Sin él, cada token nuevo recalcula la atención de todo el prompt (~630 tokens); con él, solo se calcula la fila del token nuevo. Medición (`results/kv_cache.json`): 32 tokens en 8,0 s con caché y 75,8 s sin caché (×9,4), con el mismo texto, porque el caché es una optimización exacta. El sondeo también lo usa: calcula el prompt una vez y reutiliza su caché para puntuar cada etiqueta.

**¿Qué trampa encontraste en el decoding?** El `generation_config.json` de Qwen2.5-Instruct activa sampling por defecto (T = 0,7, top-p = 0,8, top-k = 20, repetition_penalty = 1,1) y `transformers` rellena con esos valores los parámetros que no se cambian. Sin neutralizarlo, un experimento "greedy" habría usado repetition_penalty = 1,1 sin que nadie lo registrara. Ver `src/llm.py::cargar`.

**¿Por qué 192 tokens de salida?** El JSON esperado ocupa ~90-130 tokens. Con 192 hubo un truncamiento con P0 (C03) y uno con P1 (C04), ambos por justificaciones que no terminaban. Se cuentan en `metricas.json` (campo `truncados`) y aparecen como `json_invalido`: son un modo de fallo real, no un error del parser.

## Semana 3 — Instrucción, entrada, contexto, salida estructurada

**¿Cómo separaste instrucción, entrada y contexto?** En bloques con encabezado fijo (`TAREA`, `REQUERIMIENTO`, `CONTEXTO DEL PROCESO`, `CRITERIOS DE DECISIÓN`, `FORMATO DE SALIDA`), cada uno en su archivo. La entrada (texto del requerimiento) viene de OCDS, el contexto también, y la instrucción es fija por condición.

**Diferencia entre JSON parseable, schema-valid y semánticamente correcto.** Parseable: se puede leer como JSON (con P0 las 10 salidas venían dentro de un bloque ```json, así que solo eran recuperables). Schema-valid: además cumple el contrato (con P0 hubo `"senal": "marca_con_equivalente|ninguna"`, que copia la notación del prompt y viola el enum). Correcto: además la etiqueta coincide con el gold y la evidencia existe en el texto. Con P1, casi todas las salidas son schema-valid pero la mayoría son incorrectas.

**¿Por qué la coherencia `senal -> riesgo` no está en el schema?** Se podría expresar con `if/then` en JSON Schema, pero se dejó como chequeo semántico aparte para ver por separado cuántas salidas cumplen la forma y cuántas son internamente consistentes.

## Datos y negocio

**¿De dónde salen los casos?** De `tender_items.description` de 10 procesos reales del SEACE (2025-2026), elegidos con `src/construir_casos.py`. Cada uno tiene su ficha 360° en `data/fichas/` y la URL de sus bases.

**¿Quién puso las etiquetas?** El autor, con la rúbrica escrita en `data/README.md`, que es la misma que P1 entrega al modelo. Es una limitación: no hay un segundo anotador.

**¿Por qué no usaste el texto de las bases?** Porque los CSV solo tienen la URL del PDF (y 52 % de los documentos son zip o rar). Descargar y fragmentar las bases es la base del RAG de fases posteriores.

**¿Por qué el número de postores no forma parte del gold?** Porque es una señal de resultado, no de redacción. Un proceso con un solo postor puede tener bases limpias (C08, combustible en un distrito pequeño) y uno con 28 postores puede exigir una marca (C01). En el sistema multi-agente serán dos agentes distintos; el Exp. 2 mide qué pasa si se mezclan en el mismo prompt.

**¿Cómo se relacionan las tablas?** Todo cuelga de `main.id` vía `main_id`; los ids hijos solo son únicos junto con `main_id`. Diagrama en `docs/esquema_ocds.md`; integridad comprobada en `results/perfil_datos.md`.

## Resultados

**¿P1 es mejor que P0?** En estos 10 casos P1 mejora la validez estructural (0,5 → 0,9) y deja de copiar la notación del enum, pero no hace que el modelo distinga casos: cambia la etiqueta dominante de "alto" a "medio". La accuracy sube de 0,2 a 0,3 solo porque "medio" coincide con tres casos gold; el macro-F1 baja de 0,17 a 0,15. No se puede concluir que P1 sea mejor en general.

**¿Cuál es la evidencia más fuerte de que el modelo no mira el caso?** El sondeo de logits: con P1, p(alto) media es 0,26 en los casos que exigen una marca y 0,28 en los genéricos. Y con P0 es 0,85 y 0,91. Las probabilidades cambian con el prompt, no con el requerimiento.

**¿Qué pasó con el few-shot?** Las 10 salidas copian el segundo ejemplo completo (señal, evidencia "TRACTOR ORUGA BULLDOZER D375A B086 KOMATSU" y justificación sobre zapatas), incluso para los switches Cisco. El formato llegó a 10/10 y la accuracy a 0,4, pero la evidencia literal quedó en 0/10: el chequeo semántico lo detecta.

**¿El contexto conflictivo tuvo algún efecto?** No cambió ninguna etiqueta válida, pero sí: (1) la justificación de C08 y C09 pasó a describir bien el texto (regla 4) sin cambiar la etiqueta; (2) C04 y C05 superaron los 400 caracteres de justificación y fallaron el schema; (3) en probabilidad, E[riesgo] se movió +0,03 en promedio hacia donde apunta la señal (7 de 10 casos), demasiado poco para cambiar el argmax.

**¿Qué pasaría con un modelo más grande?** Es la hipótesis principal para la siguiente iteración (Qwen2.5-1.5B o 3B con el mismo protocolo). El diseño del repositorio lo permite cambiando `MODEL_ID` y `MODEL_REVISION` en `src/config.py`.

**¿Por qué 10 casos?** El enunciado pide entre 6 y 10. Con 10 casos, una diferencia de un caso mueve la accuracy 10 puntos; por eso cada conclusión se formula como "en estos casos" y se acompaña del análisis por caso.
