### Semana 3 - Prompting, generación estructurada, validación y ingeniería de contexto

#### Propósito

Semana 2 estudió cómo un modelo produce el siguiente token. Semana 3 estudia qué ocurre cuando esa generación debe convertirse en una
interfaz utilizable por software.

La cadena conceptual es:

```text
prompt -> contexto -> LLM -> texto sin procesar -> JSON parse -> JSON Schema -> validación semántica -> evaluación emparejada
```

El objetivo no es memorizar técnicas de prompting ni aprender una API de Transformers. El objetivo es convertir una generación probabilística en una interfaz verificable y evaluarla mediante evidencia.

#### Resultados de aprendizaje

Al finalizar la semana el estudiante debe poder:

- separar instrucción, entrada, contexto y contrato de salida,
- distinguir prompting de context engineering,
- diferenciar JSON exacto, JSON recuperable y JSON válido respecto de un schema,
- diseñar un contrato pequeño mediante JSON Schema,
- explicar por qué `schema-valid != semantically correct`,
- ejecutar un LLM instruction-tuned local mediante un chat template,
- comparar `baseline`, `neutral` y `conflicting` sobre los mismos casos,
- distinguir accuracy, Macro-F1, abstención y errores de formato,
- auditar las respuestas brutas que originan una métrica,
- formular una conclusión proporcional a la evidencia.

#### Material

| Recurso | Función |
|---|---|
| `Cuaderno3-CC-0F4.ipynb` | Cuaderno canónico del lunes con un LLM real |
| `datos/benchmark_incidentes_semana3.csv` | Benchmark controlado de 60 casos |
| `datos/README.md` | Diseño y alcance del benchmark |

No existe `Laboratorio3-CC-0F4.ipynb`.

El jueves se dedica íntegramente a la evaluación oral E1.

#### Modelo canónico

```text
Qwen/Qwen2.5-0.5B-Instruct
```

El modelo es deliberadamente pequeño para que la inferencia local sea
viable y para mantener el foco en la arquitectura experimental.

El cuaderno permite fijar una revisión concreta mediante:

```bash
export CC0F4_MODEL_REVISION=<revision>
```

Si no se define, se usa la revisión resuelta por Hugging Face y se
registra cuando está disponible.

#### Modo aula

Configuración canónica:

```python
CLASSROOM_MODE = True
DO_SAMPLE = False
N_REPEATS = 1
```

Se seleccionan 12 casos balanceados:

```text
3 security
3 network
3 software
3 other
```

con un caso `ambiguous` por categoría.

Costo lógico:

```text
12 casos x 3 condiciones = 36 generaciones
```

#### Ejecución completa

Para utilizar los 60 casos:

```python
CLASSROOM_MODE = False
```

Entonces:

```text
60 x 3 = 180 generaciones
```

No cambia el protocolo experimental.

#### Condiciones

```text
baseline = entrada + contexto relevante

neutral = entrada + contexto relevante + contexto neutral

conflicting = entrada + contexto relevante + contexto conflictivo
```

La comparación principal es:

```text
baseline vs conflicting
```

`neutral` funciona como control negativo para separar el efecto de "más texto" del efecto de "información conflictiva".

#### Estándar experimental

```text
pregunta -> hipótesis -> baseline -> una modificación -> métrica -> resultado -> limitación -> conclusión
```

No se reajustan después de observar los resultados:

```text
benchmark
prompt
schema
contextos
modelo
métricas
```

para fabricar una diferencia deseada.

#### Métricas

Formato:

```text
raw_json_parse_rate
recovered_json_parse_rate
schema_valid_rate
```

Semántica:

```text
category_accuracy
macro_f1
```

Comportamiento del sistema:

```text
abstention_rate
severity_consistency_rate
```

Costo:

```text
prompt_tokens
generated_tokens
latency_ms
```

Para Macro-F1 se fija el universo de clases gold:

```text
security
network
software
other
```

`unknown` e `invalid` penalizan la clase gold correspondiente, pero no se
tratan como nuevas clases objetivo.

#### Reproducibilidad

Los resultados se guardan en:

```text
.build/semana3_llm/
```

El nombre incorpora una huella de:

```text
modelo
revisión resuelta
casos
prompt
schema
decoding
benchmark SHA-256
condiciones
```

Por tanto, cambiar la configuración genera un archivo distinto.

#### Sampling

La clase usa greedy:

```python
DO_SAMPLE = False
```

La extensión:

```python
DO_SAMPLE = True
N_REPEATS = 3
```

estudia estabilidad.

Cuando existen repeticiones, el bootstrap agrega primero por `id` y remuestrea casos, no repeticiones individuales.


#### Entorno

Semana 3 utiliza el entorno global del curso. No crea un requirements
propio.

Desde la raíz:

```bash
make check-semana3
make execute-cuaderno3
```

Para validar estructura y lógica sin descargar el modelo:

```bash
CC0F4_RUN_REAL_LLM=0 make execute-cuaderno3
```

#### Primera ejecución del modelo

La primera ejecución requiere acceso a Internet para descargar el modelo si todavía no se encuentra en la caché local de Hugging Face.

El cuaderno funciona en CPU, aunque la inferencia será más lenta. Una GPU compatible acelera el experimento, pero no cambia el protocolo.

El `Makefile` incluido define:

```text
NOTEBOOK_TIMEOUT ?= 600
```

y puede sobrescribirse, por ejemplo:

```bash
make execute-cuaderno3 NOTEBOOK_TIMEOUT=900
```

Para comprobar únicamente estructura, benchmark, parsing, schema y análisis sin descargar el modelo:

```bash
CC0F4_RUN_REAL_LLM=0 make execute-cuaderno3
```

#### Criterio de cierre

El estudiante debe poder defender:

```text
prompt != context

JSON parseable != schema-valid

schema-valid != semantically correct

prompt-only JSON != constrained generation

más contexto != mejor contexto

diferencia observada != conclusión universal
```

#### Puente a Semana 4

Semana 3 selecciona manualmente el contexto. La semana 4 pregunta:

```text
¿cómo recuperar automáticamente el contexto relevante? -> embeddings -> similitud -> chunking -> dense retrieval -> FAISS
```
