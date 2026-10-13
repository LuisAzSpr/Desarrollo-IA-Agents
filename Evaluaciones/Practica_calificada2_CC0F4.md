### CC0F4 - Segunda Práctica Calificada
#### De una consulta estructurada a recuperación densa verificable

**Curso:** CC0F4 - Tópicos de Ciencia de la Computación I  
**Periodo:** 2026-2  
**Cobertura:** Semanas 3 y 4  
**Duración:** 5 días  
**Modalidad:** individual o grupal, según el tema registrado  
**Entregables:** repositorio GitHub + diapositivas + exposición  
**Nota máxima:** 20 puntos  

### 1. Propósito

Esta práctica es una actividad corta de reforzamiento que continúa el trabajo iniciado en la Primera Práctica Calificada. Mantén el mismo tema de investigación y construye una extensión pequeña que conecte dos ideas del curso:

```text
Semana 3: generación estructurada y validación -> Semana 4: embeddings y recuperación densa
```

El objetivo no es construir todavía un sistema RAG completo. La práctica debe mostrar que puedes transformar una necesidad de información en una consulta estructurada, recuperar evidencia relevante mediante embeddings y evaluar si el recuperador encuentra los fragmentos esperados.

El flujo mínimo es:

```text
necesidad de información
-> LLM
-> consulta estructurada
-> JSON Schema
-> query embedding
-> índice FAISS
-> top-k
-> evaluación
-> defensa
```

La salida recuperada no se utiliza todavía para generar una respuesta final con el LLM.

### 2. Relación con el curso

La práctica refuerza conceptos ya estudiados y los conecta en un flujo único.

#### Semana 3

Debes aplicar:

- separación entre instrucción, entrada y contexto,
- salida JSON,
- JSON Schema o validación equivalente,
- diferencia entre salida parseable, schema-valid y semánticamente adecuada,
- control del prompt y de las condiciones experimentales.

#### Semana 4

Debes aplicar:

- segmentación de documentos,
- embeddings para `query` y `passage`,
- normalización cuando corresponda,
- similitud mediante producto interno o coseno,
- índice `FAISS IndexFlatIP`,
- recuperación `top-k`,
- `Recall@k`,
- análisis de al menos un error de recuperación.

No se exige:

```text
BM25
recuperación híbrida
reranking
RAG
GraphRAG
agentes
```

### 3. Tarea mínima

Reduce tu tema de investigación a una pequeña necesidad de búsqueda.

Ejemplos:

```text
riesgo de mercado -> recuperar fragmentos relacionados con una señal o evento de riesgo
```

```text
contrataciones públicas -> recuperar cláusulas relacionadas con un requisito potencialmente direccionado
```

```text
elegibilidad laboral -> recuperar requisitos relevantes para una condición de elegibilidad
```

```text
vulnerabilidades -> recuperar evidencia relacionada con una CVE o categoría CWE
```

```text
documentos regulatorios -> recuperar fragmentos asociados con una obligación o restricción
```

```text
revisión científica -> recuperar fragmentos relacionados con una afirmación técnica
```

Utiliza un corpus pequeño y controlable. La prioridad es poder inspeccionar los resultados y defenderlos.

### 4. Requisitos mínimos

#### Corpus

Utiliza aproximadamente:

```text
6 a 12 documentos breves
```

o un conjunto equivalente de textos relacionados con tu tema.

Los documentos pueden ser públicos, sintéticos o construidos a partir de fuentes identificadas. Registra su procedencia.

#### Consultas

Define entre:

```text
4 y 6 necesidades de información
```

Para cada una, indica qué documento o fragmento debería considerarse relevante. Estas relaciones constituyen tus `qrels` mínimos.

#### Consulta estructurada

Utiliza un LLM para transformar cada necesidad de información en una salida pequeña y validable.

Ejemplo:

```json
{
  "query": "market volatility after interest-rate announcement",
  "intent": "risk_event",
  "abstain": false
}
```

Diseña un JSON Schema pequeño para esa salida.

#### Embeddings e índice

Utiliza como referencia:

```text
intfloat/multilingual-e5-small
```

y conserva los prefijos adecuados:

```text
query:
passage:
```

Utiliza recuperación densa exacta con:

```text
FAISS IndexFlatIP
```

Si empleas vectores normalizados, debes poder explicar la relación entre producto interno y similitud coseno.

### 5. Experimentos

Realiza **dos experimentos pequeños**. El objetivo es reforzar el método experimental y no aumentar innecesariamente la implementación.

#### Experimento 1 - Consulta estructurada
**Experimento basado en prompts: sí**

Compara:

```text
Q0 = consulta original del estudiante
Q1 = consulta estructurada producida por el LLM
```

Mantén constantes:

- corpus,
- segmentación,
- modelo de embeddings,
- índice,
- `top-k`.

Para Q1, registra:

```text
schema_valid_rate
```

y compara de manera exploratoria si Q0 y Q1 recuperan los mismos fragmentos relevantes.

No es necesario demostrar que la consulta generada por el LLM sea mejor. El objetivo es observar si la transformación conserva, mejora o degrada la necesidad de información original.

Incluye al menos un caso y explica qué ocurrió.

#### Experimento 2 - Tamaño de fragmento
**Experimento basado en prompts: no**

Compara:

```text
small = 100 palabras
baseline = 180 palabras
large = 320 palabras
```

Mantén constantes:

- corpus,
- consultas,
- `qrels`,
- overlap,
- modelo de embeddings,
- normalización,
- similitud,
- índice,
- `top-k`.

Reporta:

```text
Recall@1
Recall@3
Recall@5
```

Utiliza como métrica principal para la discusión:

```text
mean Recall@3
```

Incluye al menos un caso donde el tamaño del fragmento ayude, perjudique o no cambie la recuperación.

#### Registro de experimentos

Resume los resultados:

| Experimento | Variable modificada | Variable fija | Métrica | Resultado | Conclusión |
|---|---|---|---|---|---|
| Consulta | query original/estructurada | corpus, embeddings, índice, top-k | schema_valid_rate + recuperación |  |  |
| Chunking | tamaño del fragmento | corpus, queries, qrels, embeddings, índice | Recall@k |  |  |

Formula conclusiones limitadas a los datos y condiciones evaluadas.

### 6. Fuentes

Utiliza como mínimo:

```text
1 fuente primaria + 1 fuente adicional
```

Una fuente debe estar relacionada con embeddings, dense retrieval, semantic search o el método utilizado. La otra puede relacionarse con tu dominio de aplicación.

Puedes utilizar:

- Elicit,
- Consensus,
- ResearchRabbit,
- Connected Papers,
- Scite,
- SciSpace.

Las herramientas apoyan el descubrimiento y la lectura. La evidencia académica proviene de las fuentes consultadas.

### 7. Repositorio GitHub

Para reducir trabajo administrativo, puedes **continuar el repositorio utilizado en la PC1** y agregar una carpeta específica para esta práctica.

Estructura sugerida:

```text
pc2/
├── README.md
├── src/ o notebook/
├── data/
├── prompts/
├── results/
└── slides/
    └── PC2.pdf
```

Si prefieres utilizar un repositorio independiente, usa un nombre como:

```text
cc0f4-pc2-<apellido-o-grupo>-<tema-corto>
```

#### README

Incluye:

```text
1. Problema de recuperación
2. Corpus y consultas
3. Consulta estructurada y JSON Schema
4. Modelo de embeddings
5. Segmentación
6. Índice y similitud
7. Experimento 1 - Consulta
8. Experimento 2 - Chunking
9. Resultados
10. Un error de recuperación
11. Limitación
12. Conclusión
13. Fuentes
```

El README debe permitir seguir el experimento sin depender de las diapositivas.

### 8. Diapositivas

Utiliza como máximo:

```text
5 diapositivas de contenido
```

Estructura sugerida:

```text
1. Problema y necesidad de recuperación
2. Pipeline: consulta estructurada -> embeddings -> FAISS
3. Experimentos
4. Resultados y error de recuperación
5. Limitación y conclusión
```

Prioriza diagramas, tablas pequeñas, ejemplos y resultados.

### 9. Exposición

La exposición es la parte principal de la evaluación. Esta práctica es de reforzamiento, por lo que la presentación debe ser breve y técnica.

#### Tiempo

```text
6 min  exposición
2 min  demostración
4 min  preguntas
-----------------
12 min máximo
```

En la demostración muestra:

- una necesidad de información,
- el JSON producido,
- su validación,
- la consulta enviada al encoder,
- los fragmentos `top-k`,
- un resultado de `Recall@k`.

No necesitas ejecutar todos los experimentos en vivo.

### 10. Rúbrica

#### Dominio y defensa oral - 12 puntos

Se evalúa:

- comprensión de structured generation y validación,
- comprensión de embeddings y similitud,
- diferencia entre documento, fragmento, índice y recuperador,
- interpretación de `Recall@k`,
- capacidad de explicar errores y limitaciones,
- respuestas durante la defensa.

#### Experimentos y demostración - 4 puntos

Se evalúa:

- Experimento 1: consulta original vs consulta estructurada,
- Experimento 2: tamaño del fragmento,
- control de variables,
- métricas registradas,
- demostración funcional.

#### Contenido técnico y fuentes - 2 puntos

Se evalúa:

- fuente primaria pertinente,
- fuente adicional,
- conexión entre fuentes y decisiones técnicas.

#### Claridad y organización - 2 puntos

Se evalúa:

- diapositivas,
- README,
- organización del repositorio,
- manejo del tiempo.

**Nota máxima: 20 puntos**

### 11. Tema de investigación

Continúa con el **tema final declarado en la práctica calificada 1**.

No necesitas implementar todas las partes presentes en el título general de tu proyecto. Para esta práctica, trabaja únicamente la parte que pueda expresarse como una necesidad de recuperación de información.

Si tu tema no parece requerir recuperación de manera inmediata, formula una pregunta auxiliar:

```text
¿Qué evidencia textual necesitaría recuperar el sistema antes de tomar una decisión o producir una respuesta?
```

Utiliza esa evidencia como objeto de la práctica.

### 12. Criterio final

Esta práctica no busca construir RAG antes de tiempo. Busca comprobar que puedes conectar una interfaz estructurada con un recuperador denso y evaluar si la evidencia relevante aparece en los primeros resultados.

El proceso esperado es:

```text
formular
-> estructurar
-> recuperar
-> medir
-> analizar
-> explicar
-> defender
```

La prioridad es que puedas mostrar dónde estaba la evidencia relevante, qué recuperó el sistema, cuándo falló y qué conclusión está respaldada por las métricas.

Una recuperación con resultados imperfectos sigue siendo válida si puedes explicar con precisión:

```text
qué buscabas
-> qué consideraste relevante
-> qué recuperaste
-> qué métrica obtuviste
-> dónde falló
-> qué limitación permanece
```
La práctica calificada utiliza la semana 3 sobre generación estructurada, JSON Schema e ingeniería de contexto y la  Semana 4 sobre embeddings, segmentación, FAISS, top-k y 
Recall@k. Todavía no pedimos RAG completamente.
