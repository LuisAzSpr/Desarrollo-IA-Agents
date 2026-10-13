### **Lectura 7 - Evaluación de retrieval y RAG: de una respuesta plausible a evidencia reproducible**

#### **1. Evaluar no es mirar una respuesta y decidir que parece correcta**

Un sistema RAG puede producir una respuesta convincente y, aun así, haber fallado en casi todos los puntos que importan. El retriever puede haber recuperado evidencia irrelevante, el generador puede haber ignorado el contexto correcto, una cita puede apuntar a un fragmento que no respalda la afirmación y una respuesta aparentemente precisa puede provenir del conocimiento paramétrico del modelo en vez de la evidencia recuperada.

Por eso la Semana 7 introduce una separación que debe mantenerse durante el resto del curso:

```text
retrieval != generación != sistema
```

Evaluar RAG como si fuese una función monolítica que recibe una pregunta y devuelve una respuesta destruye información diagnóstica. Si solo se observa la respuesta final, resulta difícil saber dónde actuar cuando el sistema falla.

La pregunta correcta ya no es únicamente:

> ¿La respuesta parece buena?,

Ahora debemos preguntar:

> ¿El sistema recuperó la evidencia que necesitaba, la colocó suficientemente arriba, la generación utilizó esa evidencia, las afirmaciones están respaldadas y el costo adicional de cada componente está justificado?.

Esta forma de pensar conecta con la tradición experimental de Information Retrieval. El capítulo 8 de *Introduction to Information Retrieval* parte de una pregunta similar: si existen muchas alternativas para construir un sistema de recuperación, necesitamos una colección de prueba y métricas que permitan comparar esas decisiones empíricamente.

#### **2. Una test collection tiene tres piezas: corpus, consultas y juicios de relevancia**

La evaluación de retrieval necesita una colección de prueba estable. En esta semana no se construye otra colección después de observar los resultados del sistema. Se reutiliza la creada en Semana 4:

```text
corpus + queries + qrels
```

El corpus contiene la evidencia que el sistema puede recuperar. Las consultas representan las necesidades de información. Los `qrels` indican qué elementos del corpus se consideran relevantes para cada consulta.

En CC-0F4 los `qrels` están definidos sobre `passage_id`. Esto es deliberado. Los chunks son una construcción del sistema y pueden cambiar cuando cambia `target_words`, overlap o una estrategia de segmentación. Si la relevancia se redefiniera sobre los chunks cada vez que cambia la segmentación, estaríamos cambiando simultáneamente el sistema y la regla con la que lo juzgamos.

La relación correcta es:

```text
passage
-> unidad estable de evidencia

chunk
-> unidad de recuperación construida por el sistema
```

Por eso el notebook mantiene un mapeo explícito:

```text
chunk_id
-> passage_ids
```

y evalúa la recuperación respecto de los `passage_id` originales.

#### **3. El overlap introduce un problema de evaluación que no debe ignorarse**

Supongamos que el passage relevante `D01-P03` aparece, por overlap, dentro de dos chunks:

```text
D01-C01
D01-C02
```

Si ambos chunks aparecen en el ranking, no debemos fingir que recuperamos dos evidencias relevantes diferentes. Es la misma evidencia repetida.

Por esa razón el cuaderno transforma el ranking de chunks en un ranking de passages sin duplicados. Recorre los chunks en orden y añade cada `passage_id` únicamente la primera vez que aparece.

Esta operación parece pequeña, pero tiene una consecuencia metodológica importante:

```text
unidad recuperada != unidad evaluada
```

Siempre que estas unidades sean distintas, el mapeo debe declararse. Ocultarlo puede inflar métricas o hacer incomparables dos configuraciones.

#### **4. Recall@k mide cobertura de evidencia relevante**

Para una consulta $q$, sea $R_q$ el conjunto de passages relevantes y sea $L_q^{(k)}$ el conjunto de passages que aparecen entre los primeros $k$ resultados del ranking.

Definimos:

$$
\mathrm{Recall@k}(q) =
\frac{|R_q \cap L_q^{(k)}|}
{|R_q|}.
$$

Si una consulta tiene un único passage relevante, Recall@k toma los valores 0 o 1. Si una consulta tiene varios passages relevantes, puede tomar valores intermedios.

Esto permite distinguir dos preguntas que a veces se confunden:

```text
¿apareció al menos una evidencia correcta?,
```

y:

```text
¿qué fracción de toda la evidencia marcada como relevante recuperé?.
```

Cuando existe un único relevante ambas ideas coinciden. Cuando existen varios, no.

Un Recall@5 alto indica que la evidencia relevante suele aparecer dentro de los primeros resultados. No indica que aparezca en la primera posición, no mide la calidad de la generación y no demuestra que el LLM utilice la evidencia.

#### **5. MRR pregunta qué tan pronto aparece la primera evidencia relevante**

Dos sistemas pueden tener el mismo Recall@5 y ofrecer experiencias muy distintas.

Considere:

```text
Sistema A
rank 1 -> relevante
rank 2 -> irrelevante
rank 3 -> irrelevante

Sistema B
rank 1 -> irrelevante
rank 2 -> irrelevante
rank 3 -> relevante
```

Para una consulta con una sola evidencia relevante, ambos pueden alcanzar Recall@5 = 1. Sin embargo, el primer sistema coloca la evidencia útil mucho antes.

La reciprocal rank para una consulta es:

$$
RR(q)=\frac{1}{r_q},
$$

donde $r_q$ es la posición de la primera evidencia relevante.

Mean Reciprocal Rank agrega esta cantidad:

$$
MRR =
\frac{1}{|Q|}
\sum_{q\in Q}
\frac{1}{r_q}.
$$

MRR es especialmente sensible a la primera evidencia relevante. Esa propiedad es útil cuando el sistema solo necesita una evidencia fuerte para responder, pero también significa que MRR no describe completamente qué ocurre con el resto de passages relevantes.

#### **6. nDCG incorpora posición y permite relevancia graduada**

Discounted Cumulative Gain reduce la contribución de resultados que aparecen más abajo:

$$
DCG@k =
\sum_{i=1}^{k}
\frac{2^{rel_i}-1}
{\log_2(i+1)}.
$$

El ranking ideal produce $IDCG@k$. Entonces:

$$
nDCG@k =
\frac{DCG@k}{IDCG@k}.
$$

En general, `rel_i` puede contener grados de relevancia. Un documento podría ser altamente relevante, parcialmente relevante o irrelevante.

Sin embargo, el benchmark de CC-0F4 posee `qrels` binarios. Semana 7 no asigna grados de relevancia retrospectivamente solo para obtener una métrica más sofisticada. En el experimento canónico:

```text
relevante = 1
no relevante = 0
```

nDCG sigue siendo útil porque penaliza que la evidencia correcta aparezca tarde. Lo importante es entender que la capacidad de manejar relevancia graduada pertenece a la definición general de la métrica, no a los datos concretos de este benchmark.

#### **7. No existe una métrica única de retrieval que resuma todo**

La tabla A/B/C de la semana reporta:

```text
Recall@1
Recall@3
Recall@5
MRR
nDCG@5
```

La razón es que cada métrica conserva información distinta.

Un sistema puede mejorar MRR porque mueve la primera evidencia relevante hacia arriba sin cambiar Recall@5. Otro puede aumentar Recall@5 recuperando más evidencia relevante, pero colocar el primer resultado correcto más abajo. También es posible que una mejora promedio esconda consultas individuales que empeoran.

Por eso una evaluación fuerte contiene dos niveles:

```text
agregado + por consulta
```

La tabla agregada responde:

> ¿qué patrón general observamos?,

El análisis por consulta responde:

> ¿en qué casos concretos cambia el ranking y por qué?.

#### **8. La ablación de Semana 7 debe mantener fijo el benchmark**

El experimento compara:

```text
A = dense

B = dense + BM25 + RRF

C = dense + BM25 + RRF + reranker
```

El propósito no es descubrir cuál pipeline gana universalmente. El benchmark es pequeño y docente. El propósito es practicar una comparación controlada y aprender qué evidencia sería necesaria para sostener una conclusión.

La transición A -> B incorpora una señal léxica y un mecanismo de fusión. No aísla un único componente.

La transición B -> C es más limpia:

```text
hybrid RRF vs hybrid RRF + reranker
```

porque mantiene el conjunto de recuperación y agrega la etapa de Cross-Encoder.

En cualquier caso, deben permanecer fijos:

```text
corpus
queries
qrels
chunking
modelos
candidate_depth
RRF constant
top-k
```

Si se cambian varias variables simultáneamente, una diferencia observada deja de tener una atribución clara.

#### **9. Mejor retrieval no implica automáticamente mejor RAG**

Este es uno de los puntos conceptuales más importantes de la semana.

Supongamos que una configuración mejora Recall@3. Eso demuestra una propiedad del ranking respecto de los qrels. No demuestra que:

- el generador haya leído la evidencia,
- la respuesta sea correcta,
- todas las afirmaciones estén respaldadas,
- las citas sean correctas,
- el costo adicional sea aceptable.

Podemos observar:

```text
retrieval correcto + generación incorrecta = RAG incorrecto
```

También:

```text
retrieval incorrecto + LLM conoce la respuesta = respuesta correcta no atribuible al RAG
```

Por eso una respuesta correcta no basta para demostrar que el sistema RAG funciona como mecanismo de grounding.

#### **10. Correctness y faithfulness responden preguntas diferentes**

Una respuesta es correcta cuando coincide suficientemente con lo que consideramos una respuesta válida para la consulta.

Una respuesta es faithful cuando sus afirmaciones están respaldadas por el contexto que el sistema realmente entregó al generador.

Estas propiedades pueden separarse.

Caso 1:

```text
respuesta correcta + evidencia correcta + afirmaciones respaldadas
```

Es el comportamiento deseado.

Caso 2:

```text
respuesta correcta + contexto no contiene la evidencia
```

La respuesta puede proceder del conocimiento paramétrico del LLM. Para una tarea que exige grounding, no deberíamos atribuir ese éxito al retrieval.

Caso 3:

```text
evidencia correcta + respuesta incorrecta
```

El problema ya no está necesariamente en retrieval. Puede encontrarse en prompting, compresión del contexto, generación o seguimiento de instrucciones.

La evaluación modular permite localizar estas diferencias.

#### **11. Una cita presente no es una cita correcta**

Semana 5 verificaba que una cita tuviera una forma válida y que el identificador citado perteneciera al contexto enviado al LLM. Ese control sigue siendo útil, pero no demuestra semántica.

Tenemos al menos tres niveles:

```text
citation parseable
-> la cita tiene una forma reconocible

citation in context
-> el identificador pertenece al contexto entregado

citation supports afirmación
-> la evidencia citada respalda la afirmación
```

Solo el tercer nivel se acerca realmente a grounding.

En Semana 7 se aprovecha que cada chunk conserva `passage_ids`. Una cita puede verificarse contra los qrels para preguntar si el chunk citado contiene la evidencia relevante conocida para esa consulta.

Esto sigue sin demostrar automáticamente que cada frase de la respuesta esté respaldada. Para eso necesitamos analizar afirmaciones.

#### **12. Faithfulness requiere observar afirmaciones y evidencia**

Una respuesta puede contener varias afirmaciones independientes. Juzgar toda la respuesta con un solo valor oculta qué parte está o no respaldada.

Una auditoría de afirmaciones sigue una lógica como:

```text
respuesta
-> separar afirmaciones
-> para cada afirmación:
      ¿qué evidencia lo respalda?
      ¿está en el contexto recuperado?
      ¿la evidencia realmente implica la afirmación?
```

El cuaderno genera una plantilla de auditoría manual. La intención no es mantener permanentemente una evaluación manual, sino que el estudiante entienda qué trabajo debe aproximar cualquier métrica automática de faithfulness.

RAGChecker es relevante precisamente porque propone un diagnóstico más fino a nivel de afirmaciones y separa métricas del retriever y del generator.

RAGAS también es útil como referencia porque propone métricas para evaluar varias dimensiones del pipeline RAG sin requerir siempre una respuesta de referencia humana.

ARES estudia otra estrategia: jueces entrenados para dimensiones como context relevance, answer faithfulness y answer relevance, apoyados por una pequeña cantidad de anotación humana.

Estas herramientas deben analizarse críticamente. Automatizar una evaluación no convierte la salida del evaluador en ground truth.

#### **13. Un proxy puede ser útil sin convertirse en verdad**

En ingeniería se utilizan proxies porque ciertas propiedades son costosas de medir directamente.

Por ejemplo:

```text
token overlap
citation-in-context
keyword coverage
```

pueden ayudar a detectar errores y validar un pipeline de evaluación.

Pero:

```text
proxy operativo != métrica semántica validada != ground truth
```

El proyecto [Patrimonio_Andino_Grounded](https://github.com/kapumota/MCC225/tree/main/Semana4/Proyecto) de MCC225 contiene métricas operativas que son útiles para comparar condiciones dentro de su propio pipeline. Semana 7 puede utilizarlas como ejemplo crítico: una métrica útil para depuración no necesariamente generaliza como medida universal de hallucination o faithfulness.

La misma cautela aparece en [ai-code-triage](https://github.com/kapumota/ai-code-triage): el sistema produce señales para priorizar revisión, pero su documentación evita convertirlas en prueba de autoría. La lección transferible es metodológica:

> una métrica debe interpretarse según aquello que realmente observa.

#### **14. La latencia también forma parte del resultado**

Añadir un reranker puede mejorar el ranking y, al mismo tiempo, aumentar la latencia.

Por eso la tabla final incluye:

```text
latency_mean_ms
latency_p95_ms
```

El promedio resume comportamiento típico. El percentil 95 muestra una zona de la cola que el promedio puede ocultar.

Una conclusión adecuada puede ser:

> En este benchmark, el reranker aumenta nDCG@5 y MRR, pero introduce una latencia adicional. Con estos datos no podemos afirmar que el trade-off sea conveniente en todos los escenarios de producción.

Una conclusión inadecuada sería:

> El reranker es mejor.

La segunda elimina condiciones, costo y alcance.

#### **15. Incertidumbre: comparar las mismas consultas exige una comparación pareada**

Una diferencia entre medias no debe interpretarse automáticamente como una mejora estable.

Supongamos:

```text
MRR(B) = 0.71
MRR(C) = 0.76
```

La diferencia observada es 0.05, pero las 24 consultas no son 24 números intercambiables entre sistemas: **cada consulta fue evaluada bajo B y bajo C**.

Por ello el objeto relevante es:

$$
d_i = MRR_i(C)-MRR_i(B).
$$

Semana 7 utiliza bootstrap pareado: remuestrea consultas completas con reemplazo y calcula repetidamente la media de $d_i$. El resultado se resume con:

```text
delta_mean
IC 95% inferior
IC 95% superior
```

Si el intervalo cruza cero, el remuestreo es compatible tanto con mejoras como con empeoramientos de la media.

Si no cruza cero, la dirección observada es más estable **dentro de este benchmark**.

La segunda frase es crucial. Un intervalo obtenido sobre 24 consultas docentes no demuestra que la mejora se generalice a otro corpus, otro dominio o consultas futuras. El bootstrap añade una herramienta concreta para cuantificar incertidumbre, no elimina la limitación del diseño experimental.

La comparación B->C es especialmente útil porque mantiene el pipeline híbrido y agrega el reranker. Si el IC de MRR o nDCG@5 favorece C, la interpretación debe seguir limitada a:

> en este benchmark y bajo esta configuración, el reranker produjo una diferencia de ranking cuya dirección fue estable bajo el remuestreo pareado utilizado.

No:

> los Cross-Encoders siempre mejoran RAG.

#### **16. Medir costo por condición no basta cuando queremos atribuirlo**

Si solo se registra:

```text
latency(B)
latency(C)
```

podemos afirmar que C tarda más, pero no qué etapa explica el aumento.

Por eso el notebook instrumenta:

```text
dense_ms
bm25_ms
rrf_ms
reranker_ms
total_ms
```

El objetivo es distinguir costo total de costo incremental.

Por ejemplo:

```text
B
dense + BM25 + RRF

C
dense + BM25 + RRF + reranker
```

Si `reranker_ms` domina la diferencia B->C, entonces la discusión del trade-off puede atribuir el costo al componente realmente añadido.

Aun así, estas medidas no son un benchmark de rendimiento de producción. Para eso serían necesarios, entre otros elementos, warm-up, múltiples repeticiones, control de concurrencia, hardware fijo y sincronización explícita en operaciones aceleradas.

#### **17. Criterio operativo para auditar faithfulness**

Una auditoría manual también necesita reglas.

Para cada afirmación atómica se utiliza:

```text
supported_by_context = 1
```

solo si al menos un chunk del contexto entregado contiene evidencia explícita suficiente para respaldar la afirmación sin recurrir a conocimiento externo ni a una inferencia no justificada.

Se utiliza:

```text
supported_by_context = 0
```

si la evidencia está ausente, contradice la afirmación o solo respalda una parte material.

Una oración compuesta no recibe `0.5`. Se divide en afirmaciones atómicas y se evalúa cada uno por separado. Además, el evaluador registra el `supporting_chunk_id`.

Esta regla no elimina todos los desacuerdos humanos, pero vuelve auditable el criterio y hace posible comparar evaluadores.

#### **18. Por qué el contexto canónico usa top-3**

El experimento principal fija:

```text
RAG_TOP_K = 3
```

por dos razones.

Primero, `Recall@3` es una métrica central del bloque de retrieval. Segundo, mantener top-k constante evita cambiar simultáneamente el ranking y el presupuesto de contexto cuando se comparan A/B/C.

Después, como experimento de sensibilidad separado, se puede variar:

```text
1
3
5
```

y volver a observar generación, citas, faithfulness y latencia.

Separar ambas preguntas evita confundir:

```text
¿mejoró el retriever?,
```

con:

```text
¿cambió el comportamiento porque entregué más contexto al LLM?.
```

#### **19. El análisis de errores convierte una métrica en diagnóstico**

El cuaderno utiliza una taxonomía mínima para retrieval:

```text
RETRIEVAL_MISS
RANKING_ERROR
PARTIAL_RECALL
RETRIEVAL_OK
```

`RETRIEVAL_MISS` significa que la evidencia relevante no apareció ni siquiera dentro de la profundidad candidata observada.

`RANKING_ERROR` significa que la evidencia sí estaba entre los candidatos, pero no llegó al top-k que recibiría el generador.

`PARTIAL_RECALL` aparece cuando una consulta tiene varias evidencias relevantes y solo recuperamos una parte.

`RETRIEVAL_OK` significa que, bajo el criterio declarado, la evidencia relevante quedó disponible para la siguiente etapa.

Para generation se añaden categorías que normalmente necesitan auditoría:

```text
GENERATION_IGNORE
UNSUPPORTED_CLAIM
CITATION_ERROR
INCOMPLETE_ANSWER
```

Este vocabulario es más útil que decir simplemente:

```text
"RAG falló"
```

#### **20. El modo offline valida software, no el comportamiento de los modelos canónicos**

El notebook conserva un modo sin descargas para comprobar:

- lectura del benchmark,
- chunking,
- cálculo de métricas,
- RRF,
- tablas,
- exportación,
- failure taxonomy.

En ese modo, dense retrieval y reranking usan sustitutos deterministas ligeros.

Los resultados obtenidos son útiles para testing:

```text
el pipeline ejecuta
las métricas son calculables
los artefactos se generan
```

pero no deben presentarse como evidencia del comportamiento de E5 o del Cross-Encoder canónico.

La distinción debe ser explícita:

```text
validación software != evidencia experimental
```

#### **21. Qué debe contener una conclusión científica proporcional**

Una conclusión fuerte de Semana 7 debe mencionar:

1. benchmark utilizado,
2. condiciones comparadas,
3. métrica principal,
4. resultado observado,
5. costo o trade-off,
6. al menos un patrón de error,
7. limitación.

Ejemplo:

> Sobre las 24 consultas del benchmark docente, la condición C obtuvo un MRR mayor que la condición B, mientras que Recall@5 permaneció similar. La inspección por consulta muestra que el reranker movió evidencia ya recuperada hacia posiciones superiores, por lo que la mejora observada corresponde principalmente a ranking y no a mayor cobertura. La latencia p95 aumentó. El benchmark es pequeño y no permite generalizar el resultado a colecciones de producción.

Aquí cada afirmación tiene un alcance identificable.

#### **23. Cierre**

Semana 7 introduce una disciplina que debe permanecer durante el resto del curso:

```text
construir
-> medir
-> comparar
-> localizar errores
-> limitar la conclusión
-> defender la evidencia
```

La idea final es sencilla:

> un sistema RAG no está evaluado porque produzca una respuesta convincente. Está evaluado cuando podemos separar qué recuperó, qué utilizó, qué afirmó, qué evidencia respalda esas afirmaciones, cuánto costó y dónde falla.
