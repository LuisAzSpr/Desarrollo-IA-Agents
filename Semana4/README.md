### Semana 4 - Embeddings, segmentación y recuperación densa

#### Propósito

Semana 3 convirtió la generación probabilística en una interfaz verificable y mostró que la selección de contexto afecta al sistema.

Semana 4 cambia la pregunta:

```text
Semana 3
¿qué contexto entregamos al modelo?
        ->
Semana 4
¿cómo recuperamos automáticamente el contexto relevante?
```

La cadena conceptual es:

```text
documentos
-> passages
-> chunks
-> embeddings
-> similitud
-> índice
-> ordenamiento
-> top-k
```

No se construye todavía un sistema RAG.

#### Experimento principal

Pregunta:

> ¿Cómo afecta el tamaño objetivo de los fragmentos a la recuperación de evidencia relevante cuando las demás variables permanecen fijas?.

Línea base:

```text
target_words = 180
```

Variantes:

```text
small = 100
large = 320
```

Variables fijas:

```text
corpus
queries
qrels
overlap_passages = 1
modelo de embeddings
normalización L2
similitud = producto interno
índice = IndexFlatIP
top-k
```

Métricas:

```text
Recall@1
Recall@3
Recall@5
```

La métrica principal para la discusión es:

```text
mean Recall@3
```

#### Modelo canónico

```text
intfloat/multilingual-e5-small
```

Se utiliza por ser multilingüe, compacto y estar orientado a recuperación de información. Produce embeddings de 384 dimensiones y admite hasta 512 tokens.

El cuaderno utiliza los prefijos requeridos por el modelo:

```text
query:
passage:
```

El laboratorio verifica además que ninguna condición introduzca truncación.

#### Ejecución sin descarga

Para verificar el cuaderno del lunes sin descargar el encoder:

```bash
CC0F4_RUN_REAL_RETRIEVAL=0 make execute-cuaderno4
```

Para validar el laboratorio:

```bash
CC0F4_RUN_REAL_RETRIEVAL=0 \
jupyter nbconvert \
  --to notebook \
  --execute Semana4/Laboratorio4-CC-0F4.ipynb \
  --ExecutePreprocessor.timeout=600 \
  --output /tmp/Laboratorio4-validado.ipynb
```

El modo offline utiliza TF-IDF + SVD únicamente para validar el software. Sus métricas no constituyen evidencia del experimento canónico.

#### Entorno

Semana 4 utiliza el entorno global del curso. No crea un `requirements.txt` propio.

El `requirements.txt` de la raíz ya contiene:

```text
sentence-transformers
faiss-cpu
```

Desde la raíz del repositorio:

```bash
make check-semana4
make execute-cuaderno4
```

#### Alcance deliberado

Semana 4 incluye:

```text
embeddings
segmentación
similitud coseno/producto interno
recuperación densa exacta
FAISS
top-k
Recall@k mínimo
```

Semana 4 no incluye:

```text
BM25
recuperación híbrida
reranking con cross-encoder
generación RAG
LangChain
Qdrant
GraphRAG
agentes
```

#### Criterio de cierre

El estudiante debe poder defender:

```text
texto -> embedding -> ordenamiento

coseno(vectores normalizados) == producto interno(vectores normalizados)

documento != fragmento

IndexFlatIP == búsqueda exacta

índice != almacén vectorial != recuperador

más contexto por fragmento != mejor recuperación necesariamente

resultado agregado != análisis de errores
```

y presentar:

```text
small vs baseline vs large
    ->
Recall@k
    ->
análisis de errores
    ->
conclusión limitada
```

#### Puente a la Semana 5

```text
Semana 4: recuperación densa -> evidencia top-k -> Semana 5: BM25 + recuperación densa -> fusión -> reranking -> contexto -> LLM
```
