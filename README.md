### CC0F4 - Tópicos de Ciencia de la Computación I

**Tema del periodo 2026-2:** Sistemas de IA con Agentes y Recuperación Multimodal.

Este curso estudia cómo diseñar, implementar y evaluar sistemas de inteligencia artificial que combinan modelos fundacionales, contexto, recuperación de información, herramientas, estado, memoria, agentes y multimodalidad. 

El énfasis está en comprender los componentes, experimentar, medir resultados, analizar errores y defender decisiones técnicas.

> **Lenguaje principal:** Python 3.x  
> **Entorno:** Jupyter Notebook/JupyterLab  
> **Periodo:** 2026-2  
> **Créditos:** 4  
> **Horas semanales:** 6 horas  
> **Teoría:** lunes de 6:00 p. m. a 8:00 p. m.  
> **Laboratorio:** jueves de 4:00 p. m. a 8:00 p. m.

#### Descripción del curso

Asignatura teórico-práctica orientada a sistemas de IA compuestos.

Se trabajan transformers, modelos de lenguaje, structured generation, context engineering, embeddings, retrieval, RAG, herramientas, workflows, agentes, memoria, evaluación y recuperación multimodal.

Los frameworks pueden utilizarse como apoyo, pero no constituyen el objetivo central del curso.

#### Competencia del curso

Diseñar, implementar, evaluar y sustentar sistemas contemporáneos de inteligencia artificial, justificando las decisiones técnicas mediante fundamentos y evidencia experimental.

#### Resultados de aprendizaje

Al finalizar el curso, el estudiante deberá ser capaz de explicar la mecánica de un modelo transformer causal, diseñar salidas estructuradas, implementar y comparar sistemas de retrieval y RAG, construir sistemas con herramientas y agentes, evaluar mediante métricas y ablaciones, trabajar con recuperación multimodal y sustentar oralmente sus decisiones técnicas.

#### Prerrequisitos esperados

Programación, estructuras de datos y algoritmos, álgebra lineal, probabilidad básica, aprendizaje automático, redes neuronales, fundamentos de inteligencia artificial, programación concurrente y distribuida, lectura técnica.

Durante la primera semana se realizará una **prueba diagnóstica de entrada** sobre programación, fundamentos matemáticos, machine learning, transformers y razonamiento experimental.

#### Enfoque metodológico

El curso combina teoría, implementación, experimentación, exposiciones técnicas y defensa oral.

Los lunes se desarrollan los fundamentos. Los jueves se realizan laboratorios, experimentos, exposiciones y discusión de resultados.

Toda actividad experimental deberá identificar, cuando corresponda, baseline, modificación, métrica, resultado, errores y conclusión.

Se permite utilizar herramientas de IA generativa para estudiar, programar, depurar y explorar alternativas. El estudiante debe comprender y poder defender todo lo que entrega.

#### Contenido general

#### Unidad I - Modelos fundacionales e interfaces estructuradas

Transformer causal, embeddings, Q/K/V, self-attention, multi-head attention, causal masking, tokenización, logits, softmax, generación autoregresiva, decoding, ventana de contexto, KV cache, prompting, structured generation, JSON Schema, context engineering.

#### Unidad II - Recuperación, contexto y RAG

Embeddings para retrieval, similitud, chunking, vector stores, dense retrieval, BM25, sparse retrieval, recuperación híbrida, reranking, cross-encoders, RAG, grounding, Recall@k, MRR, nDCG, benchmarks, ablaciones, análisis de errores.

#### Unidad III - Herramientas, agentes y evaluación

Tool calling, contratos de herramientas, validación, retries, timeouts, workflows, estado, planificación, ReAct, verificación, criterios de parada, memoria de trabajo, memoria episódica, memoria semántica, trazas, multiagentes, supervisor-worker, handoffs, evaluación de agentes, LLM-as-Judge, pass@k, pass^k.

#### Unidad IV - Recuperación y generación multimodal

Aprendizaje contrastivo, dual encoders, CLIP, OpenCLIP, embeddings texto-imagen, recuperación image-to-text, recuperación text-to-image, R@1, R@5, R@10, MRR, hard negatives, multimodal RAG, generación grounded, trazabilidad de evidencia, análisis de errores.

#### Programación semanal

| Semana | Tema central | Evaluación oral |
|---|---|---|
| 1 | Presentación del curso, sistemas de IA compuestos, transformer, atención, causalidad, tokens, prueba diagnóstica | - |
| 2 | Logits, softmax, decoding, generación autoregresiva, ventana de contexto y KV cache | - |
| 3 | Prompting, generación estructurada, JSON Schema, validación, ingenieria de contexto | **E1** |
| 4 | Embeddings para retrieval, chunking, similitud, vector stores, dense retrieval, FAISS | - |
| 5 | BM25, recuperación híbrida, reranking, RAG | **E2** |
| 6 | Tools, function calling, contratos, validación, errores, retries, timeouts | - |
| 7 | Evaluación de retrieval y RAG, Recall@k, MRR, nDCG, grounding, error analysis | **E3** |
| 8 | Proyecto parcial | - |
| 9 | Workflows, agentes, planificación, ReAct, verificación, criterios de parada | - |
| 10 | Estado y memoria, working memory, episodic memory, semantic memory | - |
| 11 | Sistemas multiagente, supervisor-worker, handoffs, blackboard, trazas | **E4** |
| 12 | Optimización, prompt, contexto, retrieval, tools, test-time compute, SFT, LoRA, QLoRA | - |
| 13 | Evaluación de agentes, graders, LLM-as-Judge, pass@k, pass^k | - |
| 14 | Aprendizaje contrastivo, CLIP, OpenCLIP, recuperación multimodal | **E5** |
| 15 | Multimodal RAG, generación grounded, integración, demostraciones | - |
| 16 | Proyecto final | - |

#### Exposiciones de investigación

Durante el semestre se realizarán **5 exposiciones evaluadas con defensa oral**, distribuidas en las semanas 3, 5, 7, 11 y 14.

| Evaluación | Semana | Eje temático de referencia |
|---|---:|---|
| **E1** | 3 | Transformers, prompting, generación estructurada o ingeniería de contexto |
| **E2** | 5 | Retrieval, recuperación híbrida, reranking o RAG |
| **E3** | 7 | Evaluación de retrieval/RAG, grounding, métricas o análisis de errores |
| **E4** | 11 | Agentes, memoria, sistemas multiagente, coordinación o trazas |
| **E5** | 14 | Aprendizaje contrastivo, VLM, CLIP/OpenCLIP o recuperación multimodal |

El eje temático indica la relación esperada con el avance del curso. El tema específico y la fuente primaria de cada exposición serán asignados o aprobados con anticipación.

Los temas podrán incluir atención eficiente, FlashAttention, GQA, ColBERT, GraphRAG, constrained decoding, MCP, memoria persistente, sistemas multiagente, automatic prompt optimization, test-time compute, LLM-as-Judge, VLM, Document AI y agentes multimodales.

Cada exposición deberá presentar problema, fuente primaria, idea principal, método, limitaciones, pequeño experimento o demostración y conclusión.

La exposición debe mostrar comprensión y análisis crítico, no solo resumir documentación.

#### Sistema de evaluación

El curso considera **5 exposiciones de investigación, 1 proyecto parcial y 1 proyecto final**.

**E1, E2, E3, E4 y E5:** exposiciones de temas de investigación.  
**EP:** proyecto parcial.  
**EF:** proyecto final.

Se elimina la menor nota de las cinco exposiciones.

```text
PE = promedio de las cuatro mejores notas entre E1, E2, E3, E4 y E5
PF = (PE + EP + EF)/3
```

#### Exposiciones

Las exposiciones evalúan búsqueda y lectura de fuentes, comprensión técnica, análisis crítico, demostración o experimento y defensa oral.

Criterios sugeridos: dominio y defensa oral 60%, contenido técnico y uso de fuentes 10%, experimento o demostración 20%, claridad y organización 10%.

#### Proyecto parcial

El proyecto parcial integra los contenidos de las semanas 1 a 7.

Debe incluir problema, baseline, structured generation o context engineering, retrieval o RAG, métricas, análisis de errores y defensa oral.

No se exige una interfaz gráfica.

#### Proyecto final

El proyecto final integra los contenidos del curso en un sistema de IA compuesto.

Podrá incluir retrieval, herramientas, agentes, memoria, evaluación y multimodalidad según el problema elegido.

Debe presentar problema, baseline, arquitectura, experimentos, métricas, ablaciones, análisis de errores, conclusiones y defensa oral.

#### Estándar experimental

Todo experimento relevante debe registrar modelo, datos, configuración, métrica, resultado, errores y conclusión.

Se debe evitar modificar varias variables a la vez cuando se desea atribuir una mejora a un componente específico.

#### Herramientas y entorno

Python 3.x, PyTorch, Hugging Face Transformers, Hugging Face Datasets, sentence-transformers, FAISS, rank-bm25, Pydantic o JSON Schema, OpenCLIP, Jupyter Notebook o JupyterLab.

LangChain, LangGraph, smolagents, MCP u otras herramientas pueden utilizarse como ejemplos o extensiones. 

No se evaluará la memorización de APIs.

#### Convenciones de idioma y terminología

El idioma principal de las explicaciones, instrucciones, actividades, comentarios docentes y análisis del curso es el **español**.

Los cuadernos pueden utilizar ejemplos, corpus y datasets en **español o inglés** cuando ello resulte adecuado para el objetivo pedagógico o experimental. El uso de un idioma determinado en los datos no implica que todo el cuaderno deba utilizar ese mismo idioma.

Se mantienen en inglés los elementos cuyo nombre forma parte de una interfaz de software, una convención de programación o una denominación técnica ampliamente utilizada, por ejemplo:

```text
embedding
Transformer
self-attention
top-k
Recall@k
MRR
nDCG
FAISS
IndexFlatIP
BM25
RAG
LLM
query:
passage:
```

También se mantienen en inglés:

```text
nombres de variables
nombres de funciones y clases
nombres de modelos
nombres de bibliotecas
APIs
parámetros de configuración
identificadores de datasets
```

Cuando existe una traducción técnica clara y natural, la explicación utiliza español. Por ejemplo:

```text
dense retrieval -> recuperación densa
sparse retrieval -> recuperación dispersa
chunking -> segmentación
chunk -> fragmento
inner product -> producto interno
vector store -> almacén vectorial
error analysis -> análisis de errores
```

En los experimentos, el idioma de los datos debe mantenerse fijo cuando no constituye la variable estudiada. Si se compara español e inglés, esa diferencia deberá declararse explícitamente como parte del diseño experimental.

La prioridad es mantener simultáneamente **claridad pedagógica, precisión técnica y reproducibilidad del código**, evitando traducciones artificiales de nombres que forman parte del ecosistema de software o de la literatura científica.



#### Bibliografía principal

- **Chip Huyen**, *AI Engineering: Building Applications with Foundation Models*, O'Reilly Media, 2025.
- **Suhas Pai**, *Designing Large Language Model Applications: A Holistic Approach to LLMs*, O'Reilly Media, 2025.
- **Jay Alammar y Maarten Grootendorst**, *Hands-On Large Language Models: Language Understanding and Generation*, O'Reilly Media, 2024.
- **Anjanava Biswas y Wrick Talukdar**, *Building Agentic AI Systems*, Packt Publishing, 2025.
- **Vaswani et al.**, *Attention Is All You Need*, NeurIPS, 2017.
- **Lewis et al.**, *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, NeurIPS, 2020.
- **Yao et al.**, *ReAct: Synergizing Reasoning and Acting in Language Models*, ICLR, 2023.
- **Radford et al.**, *Learning Transferable Visual Models From Natural Language Supervision*, ICML, 2021.

#### Integridad académica

Se permite utilizar asistentes de programación y modelos generativos. El estudiante es responsable de comprender el código, verificar afirmaciones, reconocer fuentes, revisar resultados, identificar errores y sustentar decisiones.

Toda reutilización de código, ideas o material externo debe realizarse con honestidad académica.

#### Principio del curso

El objetivo es **construir, medir, comparar, analizar y defender**.

CC0F4 no evalúa quién produce el sistema más llamativo, sino quién puede explicar qué construyó, por qué lo hizo de esa manera, cómo sabe si funciona, dónde falla y qué evidencia respalda sus conclusiones.
