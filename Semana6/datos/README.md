### Datos de Semana 6

#### `catalogo_tools.json`

Contiene:

```text
tool specifications
stock local
rutas locales
```

Las tool specifications son visibles para el modelo.

Las implementaciones no se incluyen dentro de esta estructura.

#### `benchmark_runtime.jsonl`

17 casos del Experimento A.

Incluye:

```text
inputs válidos
validation errors
domain errors
unknown tool
transient faults
timeouts
internal error
malformed output
```

Cada caso declara su outcome esperado.

El benchmark es pequeño y docente. No pretende demostrar generalización.

#### `benchmark_tool_calls.jsonl`

24 prompts:

```text
6 calculator
6 stock
6 shipping
6 no_tool
```

Cada registro contiene:

```text
id
prompt
expected_tool
expected_arguments
should_call_tool
```

#### `tool_call_fixtures.json`

Fixtures usados cuando:

```bash
CC0F4_RUN_REAL_TOOL_LLM=0
```

Los fixtures están deliberadamente alineados con el benchmark.

Sirven para probar:

```text
parser
contratos
métricas
pipeline
```

No sirven para afirmar:

```text
"el LLM obtuvo 100%"
```

porque en ese modo no se ejecuta ningún LLM.
