### Lectura integrada - De embeddings y recuperación densa a RAG híbrido

#### Propósito

Esta lectura integra los conceptos de Semana 4 y Semana 5. El objetivo es entender la recuperación de información (retrieval) como una secuencia de decisiones de representación, indexación, ranking y uso de evidencia, no como una colección de librerías.

La arquitectura que conecta ambas semanas es:

```text
documentos
-> passages
-> fragmentos
-> representaciones
-> recuperación de candidatos
-> fusión
-> reranking
-> top-k
-> contexto
-> LLM
```

La lectura debe permitir responder una pregunta central:

> ¿Qué problema resuelve cada componente y qué evidencia necesitaríamos para afirmar que realmente mejora el sistema?.

#### 1. Embeddings para recuperación

Un embedding transforma un texto en un vector denso. Para recuperación, la meta no es reconstruir palabras sino producir una geometría útil para ranking: consultas y textos relevantes deberían quedar próximos según la función de similitud seleccionada.

Semana 4 utilizó:

```text
intfloat/multilingual-e5-small
```

con los prefijos:

```text
query:
passage:
```

La decisión importante es distinguir:

```text
modelo de embeddings != función de similitud != índice != recuperador (retriever)
```

SBERT muestra por qué un bi-encoder resulta operativo para búsqueda semántica: consulta y candidato se codifican independientemente y sus vectores pueden reutilizarse. E5 continúa esa línea con entrenamiento contrastivo orientado a representaciones de propósito general para recuperación, clustering y clasificación.

Lecturas primarias:

- Reimers, N. y Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. https://arxiv.org/abs/1908.10084
- Wang, L. et al. (2022). *Text Embeddings by Weakly-Supervised Contrastive Pre-training*. https://arxiv.org/abs/2212.03533

Preguntas de lectura:

1. ¿Por qué un bi-encoder permite indexar un corpus antes de recibir la consulta?
2. ¿Qué se pierde cuando cada fragmento se reduce a un único vector?
3. ¿Por qué el entrenamiento del encoder importa tanto como la distancia utilizada después?.

#### 2. Segmentación y unidad de recuperación

El recuperador no busca necesariamente documentos completos. Busca unidades indexadas.

```text
documento != passage != fragmento
```

Semana 4 comparó tamaños de fragmento manteniendo constante el resto del pipeline. La lección metodológica no es que exista un tamaño universalmente correcto, sino que la granularidad cambia qué evidencia puede entrar en una unidad recuperada y cuánto ruido acompaña a esa evidencia.

Para mantener trazabilidad, los qrels de CC-0F4 se definen sobre `passage_id`, no sobre `chunk_id`. Así, el ground truth permanece estable cuando cambia la segmentación.

Con `target_words = 180` sobre el corpus de Semana 4, el resultado son 24 fragmentos en total. Con `candidate_depth = 10` (Semana 5), cada recuperador examina cerca del 42% del corpus antes de fusionar o rerankear. A esta escala, "evidencia fuera de candidate_depth" es un evento distinto al que se observaría en un corpus de miles de fragmentos, y debe interpretarse con esa salvedad.

Preguntas de lectura:

1. ¿Por qué qrels definidos sobre `chunk_id` impedirían comparar dos políticas de segmentación?
2. ¿Qué riesgo introduce un fragmento grande?
3. ¿Qué riesgo introduce uno demasiado pequeño?
4. ¿Qué función cumple el overlap y por qué también puede duplicar evidencia?
5. ¿Cómo cambiaría la interpretación de `candidate_depth = 10` si el corpus tuviera 10,000 fragmentos en vez de 24?.

#### 3. Similitud, normalización e IndexFlatIP

Para dos vectores normalizados en L2:

$$
\hat{x}^T\hat{y}=\cos(x,y)
$$

Por eso Semana 4 puede utilizar `FAISS IndexFlatIP` sobre embeddings normalizados y obtener un ranking equivalente al producido por similitud coseno.

`IndexFlatIP` realiza búsqueda exacta por producto interno. No es un índice aproximado y no permite sacar conclusiones sobre el trade-off recall-latencia de ANN. En el cuaderno de Semana 5 se solicita el ranking completo únicamente porque el corpus es pequeño y se desea un desempate determinista; esa estrategia no se propone como patrón escalable.

Referencia:

- Johnson, J., Douze, M. y Jégou, H. (2017). *Billion-scale similarity search with GPUs*. https://arxiv.org/abs/1702.08734

Preguntas de lectura:

1. ¿Qué condición permite interpretar producto interno como coseno?
2. ¿Qué diferencia existe entre una representación y una estructura de índice?
3. ¿Por qué FAISS no significa automáticamente ANN?.

#### 3.1 Índice, almacén vectorial y recuperador

Antes de comparar estas piezas, conviene fijar la distinción terminológica:

```text
recuperación
-> proceso o tarea de buscar y ordenar evidencia

recuperador
-> componente que ejecuta una estrategia de recuperación
```

Estas tres piezas no son equivalentes:

```text
índice vectorial
-> estructura que permite buscar vectores

almacén vectorial
-> gestiona vectores + texto + metadatos + persistencia y, según el sistema, filtros o API

recuperador
-> componente del sistema que recibe una consulta y decide cómo producir candidatos y ranking
```

FAISS puede funcionar como índice dentro de un sistema mayor, pero `IndexFlatIP` por sí solo no constituye un almacén vectorial completo. Un proyecto como `secure-vector-db` sirve como referencia de cómo aparecen persistencia, metadatos, API e índices bajo una interfaz de software, pero no forma parte del experimento canónico de Semana 5.

Ver proyecto en:[secure-vector-db](https://github.com/kapumota/secure-vector-db)

Una precisión importante para no sacar la conclusión equivocada. En `secure-vector-db`, el generador de embeddings por defecto es una función hash determinística, pensada para pruebas rápidas y reproducibles, no un modelo semántico. `sentence-transformers` está disponible pero es opcional. Un almacén vectorial completo (persistencia, API, índices) no implica automáticamente búsqueda semántica real, esa es una decisión de embeddings independiente de la infraestructura de almacenamiento.

Pregunta de lectura:

> Si cambiáramos `IndexFlatIP` por un servicio persistente con filtros y API, ¿qué propiedades pertenecerían al algoritmo de recuperación y cuáles a la infraestructura del sistema?.

#### 4. Recuperación dispersa y BM25

La recuperación densa no reemplaza todos los mecanismos léxicos. Una consulta puede contener códigos, siglas, nombres, identificadores o términos poco frecuentes cuya coincidencia exacta resulte muy informativa.

BM25 pertenece a la familia de recuperación dispersa. Su intuición combina:

```text
frecuencia del término + rareza del término + saturación de frecuencia + normalización por longitud del documento
```

Una forma habitual de escribir el score es:

$$
\mathrm{BM25}(q,d)=
\sum_{t\in q}
\mathrm{IDF}(t)
\frac{f(t,d)(k_1+1)}
{f(t,d)+k_1(1-b+b|d|/\mathrm{avgdl})}.
$$

Los parámetros `k1` y `b` controlan, respectivamente, saturación de frecuencia y normalización por longitud. En Semana 5 no se optimizan estos parámetros después de observar los resultados.

Lectura principal:

- Robertson, S. y Zaragoza, H. (2009). *The Probabilistic Relevance Framework: BM25 and Beyond*. DOI: 10.1561/1500000019

#### 4.1 El otro lado de IDF: valor bruto, implementación y stopwords

La intuición de "rareza informativa" necesita una precisión. La forma Robertson del IDF es:

$$
\mathrm{IDF}_{raw}(t)=\log\frac{N-\mathrm{df}(t)+0.5}{\mathrm{df}(t)+0.5}.
$$

Si:

```text
df(t)/N > 0.5
```

entonces `IDF_raw(t)` es negativo.

Pero la biblioteca usada en el curso introduce una segunda decisión. `rank_bm25.BM25Okapi` calcula primero esos IDF brutos, obtiene `average_idf` y sustituye cada IDF negativo por:

```text
epsilon * average_idf
```

con `epsilon = 0.25` por defecto. Por tanto:

```text
IDF Robertson bruto
!=
IDF efectivo de BM25Okapi
```

El signo del valor efectivo depende también de `average_idf`; no debe suponerse que el piso siempre es positivo.

En un corpus docente pequeño, términos funcionales del español pueden aparecer en una gran proporción de fragmentos. Aunque `BM25Okapi` aplique su política de piso, la tokenización puede seguir afectando materialmente el ranking. Por eso Semana 5 trata el preprocesamiento léxico como parte del protocolo experimental.

El BM25 principal usa una lista mínima y fija de stopwords. La lista intenta retirar palabras funcionales de muy baja carga semántica sin eliminar términos que cambian la intención de una consulta. Se conservan deliberadamente, por ejemplo:

```text
no
sin
si
puede
pueden
debe
más
```

Esto evita convertir una regla de frecuencia documental en una eliminación automática de contenido semántico.

El cuaderno añade además una ablación:

```text
BM25_raw
vs
BM25_stopwords
```

manteniendo fijos `k1`, `b`, `epsilon`, chunks, queries y qrels. La finalidad no es demostrar que remover stopwords siempre mejora BM25, sino mostrar que:

```text
preprocesamiento léxico
es una variable experimental
```

Finalmente, aumentar el corpus no elimina por sí solo el fenómeno del IDF bruto negativo. El signo depende de la proporción `df/N`. Un término que siga apareciendo en más de la mitad de los documentos continuará teniendo `IDF_raw < 0`, aunque `N` sea muy grande.

Preguntas de lectura:

1. ¿Por qué repetir veinte veces un término no debería producir una mejora lineal ilimitada?
2. ¿Por qué BM25 puede ser fuerte para identificadores y entidades raras?
3. ¿Qué diferencia existe entre `IDF_raw` y el IDF efectivo de `BM25Okapi`?
4. ¿Por qué `epsilon * average_idf` no debe interpretarse automáticamente como un número positivo?
5. ¿Por qué una lista de stopwords no debería construirse simplemente eliminando todo término con `df/N > 0.5`?
6. ¿Qué perderíamos si elimináramos `no`, `sin` o verbos modales de consultas diagnósticas?
7. ¿Por qué la recuperación dispersa y la recuperación densa pueden ser complementarias?.

#### 5. Recuperación híbrida

Si BM25 y la recuperación densa capturan señales distintas, aparece una estrategia natural:

```text
BM25 -------+
             +-> fusión
Dense -------+
```

El problema es que los scores no están calibrados en la misma escala.

```text
BM25 score = 7.4

dense inner product = 0.81
```

No existe una razón automática para promediarlos directamente.

Semana 5 utiliza Reciprocal Rank Fusion (RRF), que opera sobre posiciones de ranking:

$$
\mathrm{RRF}(d)=
\sum_{r\in R}
\frac{1}{k+r(d)}.
$$

`k` es una constante de suavizado. El cuaderno usa `k=60` como valor fijo para el experimento.

Lectura principal:

- Cormack, G. V., Clarke, C. L. A. y Büttcher, S. (2009). *Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods*. SIGIR 2009. DOI: 10.1145/1571941.1572114

Preguntas de lectura:

1. ¿Qué problema evita RRF al trabajar con rankings en lugar de scores?
2. ¿Puede RRF recuperar un documento que no aparece en ninguna lista de candidatos?
3. ¿Por qué la profundidad de candidatos debe mantenerse fija al comparar sistemas?.

#### 6. Recuperación y reranking no son la misma tarea

Un recuperador debe ser suficientemente barato para buscar sobre todo el corpus. Un reranker recibe un conjunto mucho más pequeño y puede gastar más cómputo por par consulta-documento.

```text
corpus grande
-> recuperador
-> candidatos
-> reranker
-> ranking final
```

Por tanto:

```text
recuperación != recuperador
recuperador != índice
recuperador != reranker
```

Un bi-encoder produce representaciones independientemente. Un Cross-Encoder procesa consulta y candidato conjuntamente y puede modelar interacción fina entre ambos textos. El costo es que debe ejecutar inferencia para cada par.

Semana 5 utiliza un Cross-Encoder multilingüe como etapa final:

```text
cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
```

Lectura primaria:

- Nogueira, R. y Cho, K. (2019). *Passage Re-ranking with BERT*. https://arxiv.org/abs/1901.04085

Lectura complementaria:

- Documentación Sentence Transformers, *Retrieve & Re-Rank*. https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html

Preguntas de lectura:

1. ¿Por qué no aplicar el Cross-Encoder a millones de fragmentos?
2. ¿Qué error del recuperador no puede corregir el reranker?
3. ¿Por qué aumentar el número de candidatos puede mejorar cobertura y también aumentar costo?

#### 7. De ranking a RAG

Retrieval-Augmented Generation (RAG) conecta una memoria paramétrica, el LLM, con una memoria externa recuperable.

En CC-0F4 la versión didáctica se expresa como:

```text
consulta
-> recuperar evidencia
-> ordenar evidencia
-> seleccionar top-k
-> construir contexto
-> LLM
-> respuesta
```

Lewis et al. introducen RAG combinando generación neuronal con acceso a memoria no paramétrica externa. La idea fundamental para el curso no es reproducir exactamente esa arquitectura de entrenamiento, sino comprender la separación entre recuperación y generación.

Lectura primaria:

- Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. https://arxiv.org/abs/2005.11401

Preguntas de lectura:

1. ¿Por qué una respuesta puede ser incorrecta aunque el fragmento correcto esté en top-k?
2. ¿Por qué una respuesta correcta no demuestra que el recuperador sea bueno?
3. ¿Qué información debería conservarse para rastrear una respuesta hasta la evidencia recuperada?.

#### 8. Taxonomía mínima de fallos

Semana 5 introduce una separación que será formalizada en Semana 7:

```text
fallo de recuperación
-> evidencia relevante fuera del top-k

fallo de ranking
-> evidencia recuperada, pero demasiado abajo

fallo de construcción de contexto
-> evidencia correcta se pierde, trunca o mezcla con ruido

fallo de generación
-> el LLM recibe evidencia suficiente pero responde incorrectamente
```

No se debe atribuir automáticamente un error de respuesta al LLM.

#### 9. Qué no debe concluirse todavía

A partir del experimento de Semana 5 no se puede afirmar universalmente que:

```text
hybrid siempre supera a dense

reranking siempre mejora la recuperación

más candidatos siempre es mejor

mejor Recall@k implica mejor RAG

un Cross-Encoder concreto es el mejor para todos los dominios
```

Las conclusiones deben expresarse como:

> Bajo este corpus, estas consultas, estos qrels, esta segmentación y estos modelos, observamos...

#### 10. Mapa final de Semanas 4 y 5

```text
SEMANA 4
texto
-> fragmentos
-> E5
-> FAISS
-> dense ranking
        |
        v
SEMANA 5
BM25 --------------------+
                          +-> RRF -> Cross-Encoder -> top-k -> contexto -> LLM
Dense de Semana 4 -------+
```

#### 11. Preguntas de preparación para E2

1. ¿Qué problema concreto resuelve BM25 que un embedding puede resolver de forma distinta?
2. ¿Por qué no deben promediarse scores de dos recuperadores sin justificar su calibración?
3. ¿Cuál es la diferencia entre fusión y reranking?
4. ¿Qué ventaja y qué costo introduce un Cross-Encoder?
5. ¿Qué significa que un documento relevante esté fuera del candidate pool?
6. ¿Por qué Recall@k pertenece a la recuperación y no mide directamente calidad de generación?
7. ¿Qué información externa añade RAG al LLM?
8. ¿En qué punto del pipeline puede aparecer truncación?
9. Si el corpus fuera un millón de veces mayor, ¿qué propiedades cambiarían por el tamaño absoluto `N` y cuáles dependen de la razón `df/N`?
10. ¿Cómo cambiaría la interpretación de `candidate_depth = 10` al pasar de 24 a millones de fragmentos?
11. ¿Qué parte de este pipeline evaluarías con MRR o nDCG y por qué?.
