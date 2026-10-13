### CC0F4 - Primera Práctica Calificada
#### Del tema de investigación a un prototipo LLM verificable

**Curso:** CC0F4 - Tópicos de Ciencia de la Computación I  
**Periodo:** 2026-2  
**Cobertura:** Semanas 1, 2 y 3  
**Duración:** 1 semana y media  
**Modalidad:** individual o grupal, según el tema registrado  
**Entregables:** repositorio GitHub + diapositivas + exposición  
**Nota máxima:** 20 puntos  

### 1. Propósito

Esta práctica lleva el tema de investigación de cada estudiante o grupo a una primera implementación: un **prototipo pequeño, ejecutable y defendible**. El objetivo no es construir todavía un sistema completo, sino demostrar que una pregunta concreta puede traducirse en una tarea controlada, ejecutarse con un LLM y evaluarse con evidencia.

En esta etapa no se espera implementar RAG, recuperación híbrida, agentes, sistemas multiagente ni multimodalidad. Esos componentes corresponden a fases posteriores del curso y no son necesarios para obtener una buena calificación en esta práctica.

La primera versión debe seguir una cadena de trabajo sencilla y verificable:

```text
problema
-> entrada y contexto
-> LLM
-> decoding
-> salida estructurada
-> validación
-> pequeña evaluación
-> defensa
```

### 2. Relación con el curso

La práctica integra los conceptos desarrollados durante las tres primeras semanas. No se busca repetir definiciones de memoria, sino utilizarlas para justificar las decisiones del prototipo y explicar su comportamiento.

#### Semana 1

Debes poder explicar:

- Transformer,
- tokens y representaciones,
- atención y causalidad,
- por qué un decoder causal no puede usar información futura.

#### Semana 2

Debes poder explicar:

- logits y probabilidades,
- softmax,
- greedy vs sampling,
- temperature, top-k o top-p cuando corresponda,
- contexto,
- función conceptual del KV cache.

#### Semana 3

Debes aplicar:

- separación entre instrucción, entrada y contexto,
- salida estructurada,
- JSON Schema o validación equivalente,
- diferencia entre JSON parseable, schema-valid y semánticamente correcto.

En conjunto, estas tres semanas permiten pasar de la arquitectura y la inferencia de un LLM a una interfaz estructurada que pueda ser validada y evaluada.

### 3. Tarea mínima

Reduce tu tema de investigación a una tarea pequeña, concreta y evaluable. La práctica no requiere resolver el problema completo de tu proyecto, requiere aislar una unidad de trabajo que pueda ejecutarse varias veces bajo condiciones comparables.

Ejemplos:

```text
riesgo de mercado
-> clasificar una señal como low/medium/high
```

```text
contrataciones públicas
-> clasificar una cláusula según riesgo
```

```text
auditor de respuestas LLM
-> clasificar una respuesta como supported/unsupported
```

La tarea debe producir una salida estructurada que pueda ser inspeccionada y validada automáticamente.

Ejemplo:

```json
{
  "label": "high",
  "confidence": 0.82,
  "reason": "..."
}
```

### 4. Requisitos mínimos

#### Modelo

Utiliza:

```text
Qwen/Qwen2.5-0.5B-Instruct
```

u otro LLM pequeño adecuado para la tarea. Identifica claramente el modelo utilizado y asegúrate de que pueda ejecutarse durante la demostración. La selección del modelo debe favorecer la reproducibilidad del experimento, no la complejidad innecesaria.

#### Datos

Utiliza entre:

```text
6 y 10 casos
```

Los casos pueden ser públicos, sintéticos o construidos por ti. En todos los casos, indica su procedencia y explica brevemente por qué son adecuados para la tarea elegida.

#### Prompts

Los experimentos pueden realizarse **mediante prompts**. No necesitas desarrollar una aplicación compleja para experimentar: el interés está en controlar qué cambia entre una condición y otra y en observar su efecto sobre las salidas.

Puedes modificar de forma controlada:

- instrucción,
- ejemplos dentro del prompt,
- contexto,
- formato de salida,
- política de decoding.

Cuando realices un experimento mediante prompts, guarda en el repositorio el **prompt exacto** utilizado. Esto permite reproducir la condición experimental y evita que la comparación dependa de cambios no documentados.

Estructura sugerida:

```text
prompts/
├── baseline.txt
├── experimento_prompt.txt
└── experimento_contexto.txt
```

Si deseas atribuir un resultado a un cambio específico, no modifiques simultáneamente varias partes del prompt. Cambia una variable principal y conserva las demás condiciones.

#### Decoding

Registra la política utilizada:

```text
greedy
```

o:

```text
sampling
temperature
top_k
top_p
seed
```

según corresponda. La configuración debe quedar registrada con suficiente precisión para repetir el experimento.

#### Salida estructurada

Incluye:

- un formato JSON,
- un JSON Schema o validación equivalente,
- una forma de distinguir salida válida de salida incorrecta.

La validación estructural no reemplaza la evaluación semántica. Una salida puede ser JSON válido y cumplir el schema, pero seguir siendo incorrecta respecto de la tarea.

### 5. Experimentos

Realiza **tres experimentos pequeños**. Cada experimento debe responder una pregunta concreta y modificar una variable principal mientras mantiene constantes las demás condiciones relevantes.

Puedes implementar los experimentos con código mínimo o mediante variaciones controladas de prompts, según lo indicado en cada caso.

#### Experimento 1 - Prompt baseline vs prompt mejorado
**Experimento basado en prompts: sí**

Utiliza los mismos casos y compara:

```text
P0 = prompt baseline
P1 = prompt mejorado
```

Ejemplos de modificación:

- instrucción más precisa,
- separación explícita entre tarea y contexto,
- incorporación de criterios de decisión,
- mejor especificación del formato de salida.

Mantén constantes:

- modelo,
- casos,
- contexto,
- decoding,
- JSON Schema.

Reporta:

- `schema_valid_rate`,
- una métrica relacionada con la tarea,
- un ejemplo donde P1 mejore, empeore o no cambie la respuesta.

Explica **qué cambió exactamente en el prompt** y relaciona ese cambio con la evidencia observada. No concluyas que P1 es mejor en general si los resultados sólo lo muestran para los casos evaluados.

#### Experimento 2 - Contexto
**Experimento basado en prompts: sí**

Compara:

```text
C0 = contexto base
C1 = contexto modificado
```

Elige uno de estos cambios:

- contexto neutral,
- contexto incompleto,
- contexto conflictivo,
- contexto más largo.

Mantén constantes:

- modelo,
- instrucción,
- decoding,
- schema,
- casos.

Reporta:

```text
schema_valid_rate
```

y una métrica semántica adecuada al tema, por ejemplo:

```text
accuracy
macro_f1
exact_match
abstention_rate
```

Incluye al menos un caso en el que el cambio de contexto afecte la respuesta y explica qué cambió en el comportamiento del sistema. Si no observas una diferencia relevante, también es un resultado válido siempre que esté documentado y correctamente interpretado.

#### Experimento 3 - Decoding
**Experimento basado únicamente en prompts: no**

En este experimento el prompt permanece igual. La variable principal es la política de decoding.

Compara sobre al menos 3 casos:

```text
D0 = greedy
D1 = sampling
```

Por ejemplo:

```text
temperature = 0.8
top_p = 0.9
```

Mantén constantes:

- modelo,
- prompt,
- contexto,
- casos,
- max_new_tokens.

Observa:

- variabilidad,
- estabilidad de la etiqueta,
- validez del JSON,
- cambios cualitativos en la explicación.

No se exige demostrar que una política de decoding sea universalmente mejor. El objetivo es observar cómo cambia el comportamiento de generación cuando se modifica la política de selección de tokens.

#### Experimento opcional - Few-shot
**Experimento basado en prompts: sí**

Si deseas realizar un cuarto experimento, compara:

```text
F0 = zero-shot
F1 = few-shot
```

Agregando 1 o 2 ejemplos al prompt.

Mantén constantes:

- modelo,
- casos,
- decoding,
- schema.

Este experimento es opcional y no aumenta por sí solo la nota. Úsalo únicamente si aporta evidencia útil para la exposición o ayuda a entender mejor el comportamiento de tu sistema.

#### Registro de experimentos

Resume cada experimento en una tabla:

| Experimento | Variable modificada | Variable fija | Métrica | Resultado | Conclusión |
|---|---|---|---|---|---|
| Prompt | prompt | modelo, casos, contexto, decoding |  |  |  |
| Contexto | contexto | modelo, prompt, casos, decoding |  |  |  |
| Decoding | decoding | modelo, prompt, contexto, casos |  |  |  |

Formula una conclusión proporcional a la evidencia observada. Distingue entre lo que muestran tus casos y cualquier afirmación más general que todavía no puedas sostener.

### 6. Fuentes

Utiliza como mínimo:

```text
1 fuente primaria + 1 fuente adicional
```

La fuente primaria debe estar directamente relacionada con el método, modelo o problema técnico que estás utilizando. La fuente adicional puede complementar, comparar o contextualizar la decisión técnica.

Apóyate en las herramientas conocidas en la prueba de entrada:

- Elicit,
- Consensus,
- ResearchRabbit,
- Connected Papers,
- Scite,
- SciSpace.

No es obligatorio utilizar las seis. Utilízalas como apoyo para descubrir, relacionar y contrastar literatura, la evidencia principal debe seguir proviniendo de las fuentes académicas consultadas.

### 7. Repositorio GitHub

El repositorio debe permitir que otra persona identifique qué se hizo, reproduzca la ejecución básica y encuentre los prompts, datos y resultados utilizados en los experimentos.

#### Nombre sugerido

```text
cc0f4-pc1-<apellido-o-grupo>-<tema-corto>
```

#### Estructura mínima

```text
cc0f4-pc1-.../
├── README.md
├── requirements.txt
├── src/ o notebook/
├── data/
├── prompts/
├── results/
└── slides/
    └── PC1.pdf
```

#### README

Incluye:

```text
1. Problema
2. Tarea mínima
3. Relación con Semanas 1, 2 y 3
4. Modelo
5. Datos
6. Salida estructurada
7. Cómo ejecutar
8. Prompts utilizados
9. Experimento 1 - Prompt
10. Experimento 2 - Contexto
11. Experimento 3 - Decoding
12. Resultados
13. Un error o caso fallido
14. Limitación
15. Conclusión
16. Fuentes
```

El README no debe limitarse a enumerar archivos. Debe explicar con claridad la tarea, las condiciones experimentales, los resultados y las limitaciones del prototipo.

### 8. Diapositivas

Utiliza como máximo:

```text
7 diapositivas de contenido
```

Estructura sugerida:

```text
1. Problema y tarea
2. Arquitectura mínima
3. Relación con Semanas 1, 2 y 3
4. Prompt y salida estructurada
5. Experimentos
6. Resultados y caso fallido
7. Limitación y conclusión
```

Usa las diapositivas para apoyar la explicación, no para reemplazarla. Prioriza diagramas, resultados, ejemplos y evidencia sobre párrafos extensos de texto.

### 9. Exposición

La exposición es la parte principal de la evaluación. Debes demostrar que comprendes las decisiones del prototipo y que puedes relacionarlas con los conceptos trabajados durante las tres primeras semanas.

#### Tiempo

```text
8 min  exposición
2 min  demostración
5 min  preguntas
-----------------
15 min máximo
```

En la demostración muestra, por ejemplo:

- una entrada,
- el prompt o contexto,
- la respuesta del modelo,
- el JSON,
- la validación,
- un resultado guardado.

La demostración debe ser breve y preparada. Su función es aportar evidencia de ejecución, no consumir el tiempo de explicación técnica.

### 10. Rúbrica

#### Dominio y defensa oral - 12 puntos

Se evalúa:

- comprensión del problema y de la solución,
- dominio de los conceptos de Semanas 1, 2 y 3,
- interpretación del experimento,
- capacidad de responder preguntas sobre código, configuración y resultados.

#### Experimentos y demostración - 4 puntos

Se evalúa:

- Experimento 1: prompt baseline vs prompt mejorado,
- Experimento 2: modificación controlada del contexto,
- Experimento 3: decoding,
- métricas apropiadas,
- prompts y configuraciones registradas,
- demostración funcional.

#### Contenido técnico y fuentes - 2 puntos

Se evalúa:

- fuente primaria pertinente,
- fuente adicional,
- conexión entre literatura y decisiones técnicas.

#### Claridad y organización - 2 puntos

Se evalúa:

- diapositivas,
- README,
- organización del repositorio,
- manejo del tiempo.

**Nota máxima: 20 puntos**

### 11. Temas de referencia

Los siguientes temas corresponden a los temas registrados para la práctica. La tarea mínima de cada prototipo debe ser coherente con el tema declarado, pero puede trabajar únicamente una parte acotada del problema general.

| Estudiante | Tema |
|---|---|
| Luis Angel Azaña Vega | Sistema multi-agente LLM para la detección de requisitos direccionados en bases de contrataciones del Estado usando registros OCDS |
| David Fernando Reeves Goñi | Sistema multi-agente LLM para la detección de requisitos direccionados en bases de contrataciones del Estado usando registros OCDS |
| Omar Romulo Quispe Santos | Multi-Agent LLM Architectures and RAG for Automated Pedagogy: A Review of Exam Generation, Scoring, and Feedback |
| Luis Antonio Rojas Huaroc | Agente de extracción y verificación estructurada de elegibilidad en ofertas laborales universitarias |
| Pedro Lautaro Quispe Ballesteros | Vigilante de riesgo de mercado con alertas tempranas |
| Germain Ronald Choquechambi Quispe | Triage inteligente de vulnerabilidades con RAG híbrido sobre CVE/CWE y agentes verificadores |
| Luiggi Sergio Gil Cardoso | Análisis de documentos regulatorios con extracción estructurada, RAG y verificación de cumplimiento |
| Frank Oliver Hinojosa Zamora | Auditor de respuestas de LLM con verificación de fuentes, grounding y análisis automático de errores |
| Jesus Diego Osorio Tello | Asistente de respuesta a incidentes DevSecOps con RAG sobre runbooks, logs y evidencia técnica |
| Cesar Augusto Sanchez Malaspina | Agente de revisión científica que identifica desacuerdos entre artículos mediante citation context y RAG |
| Carlos Sinai Unda Miguel | Detección Automática de Contradicciones Normativas en Textos Jurídicos Peruanos Mediante Retrieval-Augmented Generation e Inferencia de Lenguaje Natural |

Si cambiaste tu tema después de la prueba de entrada, utiliza el **tema final declarado**. Recuerda que en esta práctica no necesitas implementar todos los componentes que aparecen en el título general de tu proyecto, debes reducirlo a una tarea mínima compatible con los contenidos de las Semanas 1, 2 y 3.

### 12. Criterio final

La práctica no busca premiar el sistema más grande ni la arquitectura con más componentes. Busca evaluar si puedes transformar una idea de investigación en un experimento pequeño, reproducible y defendible.

El proceso esperado es:

```text
comprender
-> construir
-> medir
-> explicar
-> defender
```

La prioridad es que puedas demostrar qué construiste, cómo lo evaluaste, dónde falla y qué evidencia respalda tu conclusión.

Los experimentos basados en prompts son completamente válidos siempre que:

```text
se guarde el prompt exacto
-> se cambie una variable principal
-> se mantengan las demás condiciones
-> se mida el resultado
-> se analice al menos un caso
-> se defienda la conclusión
```

Una buena práctica no es la que produce únicamente resultados favorables, sino la que permite explicar con precisión qué se probó, qué se observó, qué limitaciones permanecen y qué conclusión está realmente respaldada por la evidencia.
