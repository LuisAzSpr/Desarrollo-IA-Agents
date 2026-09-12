### Benchmark de Semana 3

Este benchmark didáctico contiene 60 incidentes en español.

Distribución:

```text
security    15
network     15
software    15
other       15
```

Cada categoría contiene casos `clear` y `ambiguous`.

El archivo incluye tres variantes de contexto por caso:

```text
relevant_context
neutral_context
distractor_context
```

El experimento no modifica los casos después de observar los resultados del LLM.

#### Propósito

El benchmark permite comparar:

```text
baseline = relevant_context

neutral = relevant_context + neutral_context

conflicting = relevant_context + distractor_context
```

No pretende representar la distribución real de incidentes de una organización ni ser un benchmark general de LLM.

El notebook calcula una huella SHA-256 del archivo y la incorpora a la configuración experimental para evitar reutilizar resultados obtenidos con otra versión del benchmark.
