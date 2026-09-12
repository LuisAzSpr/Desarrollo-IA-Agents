### Semana 5 - BM25, recuperación híbrida, reranking y RAG

#### Propósito

Semana 4 respondió:

```text
¿cómo recuperar automáticamente evidencia relevante?
        ->
embeddings -> segmentación -> similitud -> FAISS -> top-k
```

Semana 5 mantiene el mismo corpus, las mismas consultas, los mismos qrels y la misma segmentación de referencia, pero añade señales y etapas de recuperación:

```text
                         +-> BM25 ----------------+
                         |                        |
consulta ----------------+                        +-> RRF -> Cross-Encoder -> contexto -> LLM
                         |                        |
                         +-> E5 + FAISS ----------+
```

La pregunta experimental es:

> ¿Cómo cambia la recuperación de evidencia cuando se compara BM25, recuperación densa, recuperación híbrida mediante RRF y recuperación híbrida con reranking, manteniendo constantes corpus, consultas, qrels, segmentación y top-k?

#### Organización de la semana

```text
Lunes
-> Cuaderno5-CC-0F4.ipynb
-> teoría + experimento guiado

Jueves
-> E2
-> no existe Laboratorio5-CC-0F4.ipynb canónico
```

La comparación A/B/C/D se ejecuta el lunes dentro del cuaderno. El jueves se reserva a la evaluación oral E2.

#### Continuidad con Semana 4

Se reutiliza el benchmark de:

```text
Semana4/datos/
```

con:

```text
12 documentos
72 passages
24 consultas
qrels definidos sobre passage_id
```

La condición de segmentación queda fija en:

```text
target_words = 180
overlap_passages = 1
```

La recuperación densa conserva:

```text
modelo = intfloat/multilingual-e5-small
normalización = L2
similitud = producto interno
índice = FAISS IndexFlatIP
```

Semana 5 no vuelve a estudiar qué tamaño de fragmento es mejor. Esa variable ya fue estudiada en Semana 4.

#### BM25: tokenización e IDF como variables explícitas

El BM25 principal fija:

```text
k1 = 1.5
b = 0.75
epsilon = 0.25
lowercase = True
tokenización = regex Unicode
stopwords = lista mínima fija en español
stemming = no
lematización = no
normalización de tildes = no
```

La lista mínima evita retirar términos con carga semántica importante. Se conservan deliberadamente, entre otros:

```text
no
sin
si
puede
pueden
debe
más
```

La ecuación de Robertson produce un IDF bruto negativo cuando `df(t) > N/2`. Sin embargo, la implementación concreta `rank_bm25.BM25Okapi` no usa directamente esos valores negativos: calcula el promedio de IDF y sustituye los IDF negativos por:

```text
epsilon * average_idf
```

Por eso el cuaderno distingue:

```text
raw_idf
!=
effective_idf de BM25Okapi
```

La tokenización sigue siendo una decisión experimental relevante. El cuaderno compara, como ablación separada:

```text
BM25_raw
vs
BM25_stopwords
```

manteniendo fijos fórmula, `k1`, `b`, `epsilon`, chunks, queries y qrels. La ablación no se utiliza para escoger post hoc la variante que produzca el mejor resultado.

El fallback offline implementa la misma política IDF de `BM25Okapi`. Cuando `rank-bm25` está disponible, el cuaderno verifica automáticamente la paridad numérica entre ambas implementaciones.

#### Condiciones del experimento principal

```text
A = BM25_stopwords
B = dense E5 + FAISS
C = BM25_stopwords + dense + RRF
D = BM25_stopwords + dense + RRF + Cross-Encoder
```

Se fija:

```text
candidate_depth = 10
top-k in {1, 3, 5}
RRF rank_constant = 60
```

Métrica principal:

```text
mean Recall@3
```

También se reportan:

```text
Recall@1
Recall@5
```

La evaluación exhaustiva mediante MRR, nDCG, grounding y análisis sistemático de RAG queda para Semana 7.

#### Atribución causal

```text
BM25_raw vs BM25_stopwords
-> aísla el preprocesamiento léxico

dense vs hybrid
-> incorpora BM25 y la fusión; no aísla el efecto de un único componente

hybrid vs hybrid + reranker
-> comparación incremental que aísla de forma más limpia el efecto del reranker
```

`BM25 vs dense` compara dos familias de recuperación; no es una ablación de un solo componente.

#### Reranker canónico

```text
cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
```

El Cross-Encoder se aplica solo al conjunto pequeño de candidatos producido por la fusión. No se utiliza para puntuar todo el corpus.

#### Generador canónico para la demostración RAG

Se reutiliza el modelo pequeño de Semana 3:

```text
Qwen/Qwen2.5-0.5B-Instruct
```

El objetivo no es comparar modelos generativos. Se mantiene fijo para mostrar:

```text
ranking -> evidencia -> contexto -> LLM
```

Una mejora de Recall@k no demuestra automáticamente una mejora de calidad final de RAG.

#### Evidencia empírica

El cuaderno registra:

```text
Recall@1/Recall@3/Recall@5
ablación BM25_raw vs BM25_stopwords
latencia media y p95 por etapa
latencia media y p95 por sistema
bootstrap pareado de Recall@3
closed-book vs RAG
auditoría de chunk_id citados
control negativo sin evidencia esperada
manifiesto reproducible de corrida
```

El bootstrap se aplica sobre las mismas consultas y reporta IC 95% para diferencias de `Recall@3`. Es evidencia descriptiva bajo este benchmark, no una garantía de generalización.

#### Reproducibilidad

La corrida genera:

```text
Semana5/resultados/latest_run.json
```

El manifiesto registra, entre otros:

```text
hashes SHA-256 del benchmark
seed
flags real/offline
model IDs y revisiones cuando están disponibles
versiones de paquetes
candidate_depth
RRF constant
k1/b/epsilon
versión de tokenización BM25
lista y hash de stopwords
ablación BM25
métricas
bootstrap
latencias
resultados RAG
```

Solo una corrida canónica debe presentarse como evidencia empírica. El modo offline valida software.

#### Ejecución sin descargar modelos

```bash
CC0F4_RUN_REAL_RETRIEVAL=0 \
CC0F4_RUN_REAL_RERANKER=0 \
CC0F4_RUN_REAL_LLM=0 \
make execute-cuaderno5
```

Los resultados offline no sustituyen la ejecución canónica con E5, FAISS, Cross-Encoder y Qwen.

#### Entorno

Semana 5 utiliza el entorno global del curso. El `requirements.txt` de la raíz contiene las dependencias necesarias, incluidas:

```text
sentence-transformers
faiss-cpu
rank-bm25
transformers
accelerate
```

No se crea un entorno por semana.

#### Limitaciones del benchmark

Con `target_words = 180`, la configuración baseline produce 24 fragmentos. Con `candidate_depth = 10`, cada retriever entrega candidatos equivalentes a cerca del 42% del corpus.

Por tanto:

```text
este notebook demuestra candidate generation y reranking
!=
benchmark de recuperación a gran escala
```

Solicitar el ranking completo a `IndexFlatIP` y aplicar después un desempate determinista es razonable para este corpus docente, pero no escala a colecciones grandes. En producción se pediría directamente un conjunto acotado de vecinos.

El benchmark tampoco fue diseñado post hoc como colección adversarial de distractores léxicos duros. Agregar esos distractores después de observar resultados constituiría una condición experimental nueva.

#### Alcance deliberado

Semana 5 incluye:

```text
BM25
recuperación dispersa
recuperación densa heredada de Semana 4
RRF
recuperación híbrida
Cross-Encoder
retrieve-then-rerank
construcción mínima de contexto
RAG mínimo
Recall@k
latencia
incertidumbre por bootstrap
```

Semana 5 no convierte todavía en objetivo principal:

```text
MRR
nDCG
RAGAS
LLM-as-Judge
grounding exhaustivo
GraphRAG
agentic RAG
LangChain
LangGraph
MCP
agentes
```

#### Criterio de cierre

La semana está cerrada cuando el estudiante puede defender:

```text
sparse retrieval != dense retrieval

raw Robertson IDF != effective BM25Okapi IDF

tokenización != detalle irrelevante

BM25 score != dense score

fusionar rankings != promediar scores sin calibración

retriever != reranker

bi-encoder != cross-encoder

candidate generation != final ranking

mejor Recall@k != mejor respuesta RAG necesariamente

cita válida != groundedness demostrado

RAG = retrieval + contexto + generación
```

y explicar:

```text
BM25 -------+
             +-> RRF -> Cross-Encoder -> top-k -> contexto -> LLM
E5 + FAISS --+
```

#### Puente a la la Semana 6

```text
Semana 5
LLM + evidencia recuperada
        ->
Semana 6
LLM + herramientas con contratos, validación, retries y timeouts
```
