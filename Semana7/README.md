### Semana 7 - Evaluación de retrieval y RAG

#### Propósito

Las Semanas 4 y 5 construyeron un sistema de recuperación y RAG. La Semana 7 cambia la pregunta:

```text
Semana 4
¿cómo recuperar evidencia?

Semana 5
¿cómo combinar BM25, dense retrieval, RRF y reranking?

Semana 7
¿cómo demostrar que una configuración es mejor, dónde falla y cuánto cuesta?
```

La tesis de la semana es:

```text
una respuesta plausible != un sistema evaluado
```

La evaluación se separa en tres niveles:

```text
retrieval
-> Recall@k
-> MRR
-> nDCG

generation
-> correctness
-> citation correctness
-> faithfulness/grounding

system
-> latencia
-> costos
-> failure modes
```

El objetivo no es aprender una biblioteca de evaluación. Primero se implementan y entienden las métricas; después se estudian frameworks como RAGAS, RAGChecker o ARES como referencias de investigación.

#### Material

| Recurso | Función |
|---|---|
| `Cuaderno7-CC-0F4.ipynb` | Material canónico del lunes: métricas, comparación A/B/C, análisis por consulta y evaluación de RAG |
| `Lectura7-CC-0F4.md` | Lectura técnica sobre test collections, métricas, grounding y failure analysis |
| `datos/reference_answers_semana7.jsonl` | Respuestas de referencia y evidencia que extienden las 24 consultas de Semana 4 |
| `datos/README.md` | Contrato del benchmark y reglas de uso |
| `resultados/README.md` | Artefactos que genera el cuaderno |

Semana 7 **reutiliza directamente**, sin copiar ni modificar:

```text
Semana4/datos/corpus_semana4.jsonl
Semana4/datos/queries_semana4.jsonl
Semana4/datos/qrels_semana4.json
```

#### Continuidad experimental

Los `qrels` permanecen definidos sobre `passage_id`. Esta decisión es importante porque los chunks dependen de la estrategia de segmentación, mientras que la relevancia de la evidencia no debe redefinirse cada vez que cambia una unidad de recuperación.

Por tanto:

```text
benchmark fijo + sistema variable = comparación interpretable
```

La Semana 7 no crea 20 o 40 consultas nuevas después de haber observado los resultados de Semana 5. Utiliza las 24 consultas existentes y añade únicamente las anotaciones necesarias para evaluar la generación.

#### Pregunta experimental

> ¿Cómo cambia la calidad del ranking, el comportamiento de la generación y el costo del sistema cuando se incorporan recuperación léxica y reranking al pipeline denso, manteniendo fijo el benchmark?.

#### Condiciones

```text
A = dense retrieval

B = dense retrieval
  + BM25
  + Reciprocal Rank Fusion (RRF)

C = dense retrieval
  + BM25
  + RRF
  + Cross-Encoder reranker
```

No se usa la expresión ambigua `dense + BM25` sin declarar cómo se fusionan los rankings.

#### Variables fijas

```text
corpus
queries
qrels
target_words = 180
overlap_passages = 1
dense model
BM25 policy
candidate_depth = 10
RRF constant = 60
reranker model
top-k
generator, cuando se ejecuta
prompt
decoding
```

Modelos canónicos heredados de Semana 5:

```text
dense:
intfloat/multilingual-e5-small

reranker:
cross-encoder/mmarco-mMiniLMv2-L12-H384-v1

generator opcional:
Qwen/Qwen2.5-0.5B-Instruct
```

#### Métricas de retrieval

```text
Recall@1
Recall@3
Recall@5
MRR
nDCG@5
```

Las medias se acompañan con **bootstrap pareado sobre las diferencias por consulta** para A->B y B->C. Se reporta `delta_mean` e IC 95% con 5000 remuestreos. El intervalo cuantifica incertidumbre condicionada a las 24 consultas; no convierte el benchmark docente en evidencia universal.

Los `qrels` son binarios. `nDCG` se introduce como métrica capaz de admitir relevancia graduada, pero el experimento canónico no inventa grados de relevancia que no existían en el benchmark.

Como los `qrels` están definidos sobre `passage_id` y el sistema recupera chunks, el cuaderno expande explícitamente el ranking de chunks a un ranking de passages sin duplicados antes de calcular las métricas.

Esto evita contar dos veces el mismo passage cuando aparece por overlap en más de un chunk.

#### Métricas de generación

La generación se evalúa separadamente de retrieval.

El núcleo distingue:

```text
answer correctness
citation correctness
faithfulness
```

No se afirma que una sola función automática mida perfectamente estas propiedades.

El cuaderno utiliza:

- respuesta de referencia y `required_facts` para apoyar la evaluación de correctness;
- relación `cita -> chunk -> passage_id -> qrels` para evaluar citas;
- una plantilla de auditoría manual a nivel de claims para faithfulness.

Se incluye un `reference_token_f1_proxy` únicamente como **proxy léxico de depuración**. No se presenta como métrica semántica universal.

RAGAS, RAGChecker y ARES se estudian como referencias de investigación, no como sustitutos de comprender la evaluación.

El experimento canónico fija `RAG_TOP_K=3` porque `Recall@3` es una métrica central y se desea mantener constante el presupuesto de contexto entre A/B/C. Después se estudia sensibilidad con `top_k` 1/3/5 como extensión separada; no se mezclan ambas variaciones en la comparación causal principal.

#### Métricas de sistema

La latencia se registra tanto end-to-end como por etapa:

```text
dense_ms
bm25_ms
rrf_ms
reranker_ms
total_ms
```

El cuaderno reporta medias por etapa y `total_p95_ms`. Esto permite atribuir el costo incremental de la condición C al componente correspondiente, en lugar de concluir únicamente que el pipeline completo tarda más.

Cuando se ejecuta generación real también se registra:

```text
generation_latency_ms
```

Estas mediciones son instrumentación del experimento docente. No sustituyen un microbenchmark de producción con warm-up, múltiples repeticiones, hardware controlado y sincronización explícita cuando corresponda.

La Semana 7 exige discutir trade-offs: una mejora de ranking puede no justificar el costo adicional del reranker.

#### Taxonomía de fallos

El análisis de errores utiliza al menos:

```text
RETRIEVAL_MISS
RANKING_ERROR
PARTIAL_RECALL
RETRIEVAL_OK

GENERATION_IGNORE
UNSUPPORTED_CLAIM
CITATION_ERROR
INCOMPLETE_ANSWER
```

Las cuatro primeras se pueden derivar de qrels y rankings.

Las cuatro últimas requieren inspeccionar la respuesta y la evidencia; no se inventan automáticamente a partir de una métrica agregada.

#### Ejecución

Validación sin descargar modelos:

```bash
CC0F4_RUN_REAL_RETRIEVAL=0 \
CC0F4_RUN_REAL_RERANKER=0 \
CC0F4_RUN_REAL_LLM=0 \
make execute-cuaderno7
```

Ejecución canónica de retrieval/reranking:

```bash
CC0F4_RUN_REAL_RETRIEVAL=1 \
CC0F4_RUN_REAL_RERANKER=1 \
CC0F4_RUN_REAL_LLM=0 \
make execute-cuaderno7
```

Extensión opcional con generación real:

```bash
CC0F4_RUN_REAL_RETRIEVAL=1 \
CC0F4_RUN_REAL_RERANKER=1 \
CC0F4_RUN_REAL_LLM=1 \
make execute-cuaderno7
```

El modo offline valida software y métricas, pero sus números no sustituyen la evidencia obtenida con los modelos canónicos.

#### Resultados generados

El cuaderno genera en `Semana7/resultados/`:

```text
retrieval_summary.csv
retrieval_per_query.csv
latency_by_stage.csv
bootstrap_pairwise_ci.csv
generation_outputs.csv          # solo si se ejecuta generación
faithfulness_audit_template.csv
latest_run.json
```

#### Referencias externas principales

- Manning, Raghavan y Schütze. *Introduction to Information Retrieval*, Chapter 8: Evaluation in Information Retrieval.  
  https://nlp.stanford.edu/IR-book/
- Es et al. *RAGAS: Automated Evaluation of Retrieval Augmented Generation*.  
  https://arxiv.org/abs/2309.15217
- Saad-Falcon et al. *ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems*.  
  https://arxiv.org/abs/2311.09476
- Ru et al. *RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation*.  
  https://arxiv.org/abs/2408.08067

#### Criterio de cierre

La semana está cerrada cuando el estudiante puede defender:

```text
retrieval quality != generation quality

Recall@k != MRR != nDCG

mejor Recall@k != mejor respuesta necesariamente

correct answer != faithful answer

cita presente != cita correcta

citation correctness != faithfulness

aggregate metric != error analysis

offline fallback != evidencia canónica

LLM-as-Judge != ground truth

más componentes != mejor sistema necesariamente
```

y puede presentar una tabla comparativa A/B/C con métricas, latencia, casos de error y una conclusión limitada por el benchmark.

#### Puente al proyecto parcial

Semana 8 ya no debería aceptar:

```text
"mi RAG funciona porque responde bien"
```

El proyecto parcial debe llegar con:

```text
benchmark
baseline
variante
métricas
errores
limitaciones
evidencia reproducible
```
