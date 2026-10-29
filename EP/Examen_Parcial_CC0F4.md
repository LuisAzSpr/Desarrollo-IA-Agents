### CC0F4 - Examen Parcial
#### Del prototipo LLM y la recuperación densa a un sistema RAG evaluable

**Curso:** CC0F4 - Tópicos de Ciencia de la Computación I  
**Periodo:** 2026-2  
**Cobertura:** Semanas 1 a 7  
**Publicación:** lunes 19 de octubre de 2026  
**Fecha máxima de entrega y presentación:** jueves 29 de octubre de 2026, durante la Semana 9  
**Modalidad:** individual, excepto el único grupo de dos estudiantes ya conformado  
**Entregables:** repositorio GitHub + diapositivas + demostración y defensa oral  
**Nota máxima:** 20 puntos

### 1. Propósito

Continúa el **mismo tema de investigación** trabajado en la PC1 y la PC2. El examen integra generación estructurada, recuperación, RAG, contratos de herramientas y evaluación experimental. No se trata de desarrollar una aplicación nueva ni de agregar componentes por acumulación, sino de justificar cuáles funcionan, dónde fallan y qué evidencia respalda cada conclusión.

El trabajo debe aprovechar los cuadernos, lecturas y laboratorios de las siete semanas. Se valorará la **adaptación razonada** del material de clase al proyecto, no su reproducción literal. No se exige interfaz gráfica, agentes, ReAct, memoria ni despliegue en producción.

### 2. Relación con las siete semanas

El estudiante debe incorporar al `README.md` una **matriz de trazabilidad de siete filas**, una por semana. Cada fila identificará un recurso concreto revisado (`Cuaderno`, `Lectura` o `Laboratorio`, cuando exista), el concepto estudiado, dónde aparece aplicado o analizado en su trabajo (archivo, sección o celda), una evidencia verificable y una limitación o conclusión propia.

La defensa abarcará los siguientes conocimientos:

- **Semana 1:** tokens, embeddings, Q/K/V, atención y máscara causal, explicar la arquitectura del modelo elegido.
- **Semana 2:** logits, softmax, greedy y sampling, ventana de contexto y función del KV cache, justificar el decoding utilizado.
- **Semana 3:** instrucciones, contexto, JSON Schema, validación estructural y semántica, reutilizar la interfaz de la PC1.
- **Semana 4:** chunking, overlap, embeddings, similitud, FAISS, `top-k` y `qrels`, recuperar y revisar la línea base de la PC2.
- **Semana 5:** BM25, recuperación híbrida, RRF, Cross-Encoder y RAG, comparar arquitecturas de recuperación.
- **Semana 6:** function calling, contratos, validación de dominio, errores, retries y timeouts, implementar una herramienta acotada y verificable.
- **Semana 7:** Recall@k, MRR, nDCG, grounding, corrección de citas, latencia y análisis de errores, evaluar y defender los resultados.

**Una lista de definiciones o referencias a cuadernos no constituye evidencia de aprendizaje.** Se requiere explicar decisiones, mostrar ejecuciones o resultados y relacionarlos con los conceptos correspondientes.

### 3. Tarea mínima

A partir del prototipo de PC1 y del recuperador de PC2, construye una extensión pequeña que permita recuperar evidencia de tu dominio, utilizarla en una respuesta RAG, evaluar variantes de recuperación y demostrar una herramienta con contratos verificables. Conserva el problema original y delimita una pregunta experimental clara.

Flujo de referencia:

```text
problema del proyecto
-> consulta estructurada y validada
-> recuperación densa /híbrida/reranking
-> evidencia top-k
-> respuesta RAG con citas
-> evaluación y análisis de errores

herramienta local independiente
-> contrato -> validación -> ejecución o error estructurado
```

La herramienta puede permanecer independiente de RAG. No debe implementarse un agente para conectar ambos flujos.

### 4. Requisitos mínimos

#### Datos reales y evidencia de relevancia

**No se aceptará como evaluación principal un corpus exclusivamente sintético ni los conjuntos diminutos utilizados en ejercicios anteriores, por ejemplo, 6 a 12 documentos y 4 a 6 consultas.** Esos conjuntos pueden generar coincidencias fáciles, rankings artificialmente favorables, métricas inestables y conclusiones que no se sostienen fuera de los ejemplos seleccionados.

Utiliza documentos auténticos, públicos o de procedencia verificable, relacionados con tu tema. Por ejemplo, reúne **30 documentos reales**, o **100 pasajes trazables procedentes de al menos 15 documentos reales**. Define **20 consultas distintas** y sus `qrels` de referencia, anotados antes de comparar sistemas. Incluye consultas difíciles y distractores relevantes. No infles el corpus duplicando documentos ni generes automáticamente la evidencia gold a partir de las respuestas del mismo sistema evaluado.

Documenta procedencia, permisos de uso cuando correspondan, selección, versiones, identificadores estables y limitaciones. Si la colección pública ya dispone de consultas y juicios de relevancia, puedes reutilizarlos indicando su origen. Estos mínimos permiten una evaluación docente más significativa, pero **no prueban generalización estadística**.

#### Implementación

Reutiliza, corrige y documenta los componentes de PC1 y PC2. Fija corpus, consultas, `qrels`, segmentación, modelos, `top-k`, parámetros, semillas y decoding para las comparaciones pertinentes. Guarda prompts, configuración y resultados. Se permiten modelos pequeños y ejecución local. Los modos simulados u offline sirven para comprobar el software, **no sustituyen los resultados del experimento con modelos reales**.

### 5. Experimentos obligatorios

#### Experimento 1 - Recuperación y reranking

Sobre el mismo benchmark, compara:

```text
A = recuperación densa con embeddings + FAISS
B = A + BM25 + fusión RRF
C = B + reranking con Cross-Encoder
```

Reporta `Recall@1`, `Recall@3`, `Recall@5`, `MRR`, `nDCG@5` y latencia por etapa. Analiza al menos dos consultas con diferencias relevantes. Explica que A frente a B incorpora simultáneamente recuperación léxica y fusión, mientras que B frente a C permite examinar el efecto incremental del reranker. No declares superioridad general a partir de promedios aislados.

#### Experimento 2 - RAG y evidencia

Compara, sobre **al menos 10 consultas fijadas previamente**, respuestas del mismo LLM sin recuperación (`closed-book`) y con evidencia recuperada mediante una configuración declarada del experimento 1. Conserva modelo, preguntas y decoding. Incluye citas a identificadores de pasajes y al menos un caso sin evidencia suficiente, donde corresponda abstenerse.

Evalúa por separado **corrección de la respuesta**, **corrección de citas** y **faithfulness/grounding** mediante una auditoría manual breve de afirmaciones y pasajes. Presenta al menos un error o respuesta no sustentada. No utilices únicamente fluidez, similitud léxica o una valoración automática del LLM como prueba de calidad.

#### Experimento 3 - Contratos de una herramienta

Implementa **una función local vinculada al dominio del proyecto**, con especificación, contrato de entrada, validación de dominio, contrato de salida y `ToolResult`/`ToolError` o equivalentes. Registra pruebas de una ejecución válida, entrada inválida, error de dominio y fallo transitorio o timeout controlado. Justifica cuándo corresponde reintentar y cuándo no. No se requieren cadenas de herramientas, APIs pagadas ni agentes.

#### Registro experimental

Para cada experimento presenta la pregunta, línea base, variables fijas, modificación, métricas, resultados, al menos un error, limitaciones y conclusión. Incluye una tabla comparativa y archivos con salidas originales que permitan comprobar los cálculos. Se deben conservar también los resultados negativos.

### 6. Fuentes

Utiliza al menos **una fuente primaria técnica y una fuente adicional pertinente al dominio**. Relaciónalas con decisiones concretas del proyecto. Incluye referencias específicas a los cuadernos, lecturas y laboratorios revisados en la matriz de trazabilidad. Las herramientas de búsqueda bibliográfica pueden apoyar la revisión, pero no reemplazan la lectura de las fuentes.

### 7. Repositorio GitHub

Continúa preferentemente el repositorio de PC1 y PC2, sin eliminar evidencia previa. Organiza la entrega en una carpeta `parcial/` o identifica claramente la versión evaluable.

```text
parcial/
├── README.md
├── src/ o notebooks/
├── data/                 # fuentes, consultas y qrels o enlaces verificables
├── prompts/
├── results/              # métricas, respuestas y trazas
└── slides/
    └── Examen_Parcial_CC0F4.pdf
```

El README debe incluir problema y continuidad con PC1/PC2, instrucciones de ejecución, descripción y procedencia del corpus, arquitectura, matriz de las siete semanas, tres experimentos, resultados, errores, limitaciones, conclusiones y fuentes. Identifica el commit utilizado para la evaluación. En el único grupo de dos estudiantes se añadirá una sección de **contribuciones individuales verificables**; ambos deben dominar el trabajo completo.

### 8. Diapositivas

Máximo **7 diapositivas de contenido**: problema y continuidad, arquitectura y datos, trazabilidad de aprendizajes, comparación de recuperación, RAG y evidencia, herramienta y contratos, resultados, errores y conclusiones. Prioriza figuras, tablas y resultados verificables sobre descripciones extensas.

### 9. Exposición y defensa

**Individual:** 8 minutos de exposición, 2 de demostración y 5 de preguntas, máximo 15 minutos.  
**Único grupo de dos:** 10 minutos de exposición, 3 de demostración y 7 de preguntas, máximo 20 minutos.

La demostración mostrará una consulta, evidencia recuperada, una respuesta con citas, una métrica comprobable y al menos un caso de validación o error de herramienta. Las preguntas cubrirán fundamentos de las siete semanas y decisiones presentes en el repositorio. En el grupo, ambos integrantes responderán individualmente y podrán recibir calificaciones diferentes de acuerdo con su dominio y contribución.

### 10. Rúbrica

#### Dominio técnico y defensa oral - 12 puntos

Comprensión de los contenidos de las siete semanas, explicación de código y materiales revisados, interpretación de resultados, justificación de decisiones y respuestas individuales durante la defensa. La matriz de trazabilidad deberá sustentarse con evidencia real.

#### Experimentos y demostración - 4 puntos

Comparación A/B/C de recuperación, generación RAG con evaluación de evidencia, herramienta con contratos y pruebas, control de variables, resultados reproducibles y demostración funcional.

#### Contenido técnico y fuentes - 2 puntos

Pertinencia de las fuentes, uso razonado de cuadernos, lecturas y laboratorios, corrección de conceptos y relación entre literatura, datos y decisiones.

#### Claridad y organización - 2 puntos

README, trazabilidad de archivos y datos, diapositivas, organización del repositorio y manejo del tiempo.

**Nota máxima: 20 puntos.** Se conserva la distribución de las dos prácticas anteriores: **12 + 4 + 2 + 2**. Un repositorio funcional no reemplaza la defensa individual ni la evidencia experimental.

### 11. Tema de investigación

Se mantiene **el tema final registrado en PC1 y continuado en PC2**. No se admiten cambios de tema ni nuevos grupos para este examen sin autorización docente. Los métodos se adaptarán al problema específico, manteniendo un núcleo de evaluación comparable para todos.

### 12. Criterio final y continuidad hacia la Semana 9

La entrega debe dejar un **baseline reproducible, corpus y `qrels` trazables, recuperación comparada, una demostración RAG evaluada y una herramienta con contratos**, de manera que el proyecto pueda ampliarse posteriormente con workflows y agentes a partir de la Semana 9, sin implementarlos ahora.

Se evaluará la capacidad de **comprender, adaptar, medir, analizar errores y defender**. No se premiará tener más componentes, métricas artificialmente altas ni respuestas aparentemente convincentes sin evidencia verificable.
