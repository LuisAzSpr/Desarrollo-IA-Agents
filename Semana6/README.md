### Semana 6 - Herramientas, llamada de funciones, contratos, validación, errores, reintentos (retries) y límites de tiempo (timeouts)

#### Propósito

Semana 5 terminó en una arquitectura donde el LLM recibe evidencia recuperada. Semana 6 cambia la frontera del sistema: el modelo ya no solo produce texto o respuestas apoyadas en contexto, sino que puede proponer una acción sobre una herramienta externa.

```text
Semana 5
LLM + evidencia recuperada
        ->
Semana 6
LLM + herramientas con contratos verificables
```

La pregunta central es:

> ¿Cómo convertir una propuesta probabilística de llamada a una herramienta en una ejecución controlada, validable, observable y temporalmente acotada?

La cadena conceptual de la semana es:

```text
usuario
   |
   v
LLM + especificaciones de herramientas (tool specifications)
   |
   v
ToolCall
{name, arguments}
   |
   v
análisis sintáctico (parsing)
   |
   v
lista de herramientas permitidas (allowlist)
   |
   v
contrato de entrada (input contract)
   |
   v
validación de dominio (domain validation)
   |
   v
política de ejecución (execution policy)
   |
   +-> reintento selectivo (retry)
   +-> espera progresiva entre reintentos (backoff)
   +-> tiempo de espera por intento (timeout)
   +-> límite temporal total (deadline)
   |
   v
implementación de la herramienta (tool implementation)
   |
   v
contrato de salida (output contract)
   |
   v
ToolResult/ToolError
   |
   v
observación (observation)
```

La tesis pedagógica de la semana es:

```text
Semana 6 no estudia agentes.

Semana 6 estudia la frontera de confianza
entre un LLM probabilístico y una función determinista.
```

#### Organización excepcional de la semana

La Semana 6 dispone únicamente de la sesión del **lunes 5 de octubre de 2026, de 6:00 p. m. a 8:00 p. m.**

El **jueves 8 de octubre de 2026 es feriado nacional por el Combate de Angamos**, por lo que **no se programa laboratorio ni exposición** en esta semana.

El cuaderno conserva material adicional y ejercicios de práctica autónoma para que el estudiante pueda profundizar fuera de las dos horas presenciales. El núcleo de la sesión del lunes se concentra en la frontera de confianza, contratos, validación, errores estructurados, reintentos selectivos y límites temporales.

#### Resultados de aprendizaje

Al finalizar la semana el estudiante debe poder:

- distinguir salida estructurada (structured output), llamada de funciones (function calling) y ejecución de funciones (function execution),
- explicar por qué la salida de un LLM no constituye entrada confiable,
- diseñar un contrato de entrada tipado,
- separar validación estructural de validación de dominio,
- diseñar contratos de salida,
- representar errores como datos estructurados,
- clasificar errores usando `protocol`, `validation`, `domain`, `transient`, `timeout`, `execution` y `output_contract`,
- decidir qué errores son reintentables (`retryable`),
- distinguir reintento (`retry`) de reparación (`repair`),
- distinguir tiempo de espera por intento (`timeout`) de límite temporal total (`deadline`),
- medir resultados correctos aunque el resultado esperado sea un error,
- auditar llamadas a herramientas (`tool calls`) mediante trazas reproducibles,
- evaluar por separado selección de herramienta, análisis sintáctico (`parsing`), validez del esquema, semántica de argumentos y resultado de extremo a extremo (`end-to-end`).

#### La llamada de herramientas (tool calling) no es ejecución

```text
llamada de funciones (function calling) != ejecución de funciones (function execution)
```

El modelo puede proponer:

```json
{
  "name": "catalog.lookup_stock",
  "arguments": {
    "sku": "SKU001"
  }
}
```

pero la aplicación conserva la autoridad para aceptar o rechazar la solicitud, validar los argumentos, ejecutar la función, decidir si corresponde reintentar, cancelar cuando se supera un presupuesto temporal y registrar lo ocurrido.

#### Herramientas canónicas

La semana utiliza tres herramientas locales:

```text
calculator.calculate_total
catalog.lookup_stock
shipping.get_quote
```

El Experimento A no requiere una API externa. Esto permite estudiar la política de ejecución sin introducir variabilidad de red ni fallos externos no controlados.

#### Niveles de contrato

##### Especificación de herramienta (tool specification)

Es la descripción que observa el modelo y contiene, como mínimo:

```text
name
description
parameters
```

##### Contrato de entrada (input contract)

Valida forma, tipos y restricciones estructurales. En el entorno Python se representa mediante Pydantic y puede relacionarse con JSON Schema.

##### Contrato de dominio (domain contract)

Valida reglas que no pertenecen únicamente al tipo. Por ejemplo, `"SKU999"` puede ser un `str` perfectamente válido y cumplir un esquema, pero no existir en el catálogo.

```text
válido por tipo (type-valid)
!=
válido por esquema (schema-valid)
!=
válido para el dominio (domain-valid)
```

##### Contrato de salida (output contract)

Una herramienta también debe cumplir la forma de salida prometida.

```text
herramienta ejecutada != salida válida
```

#### Errores estructurados

La interfaz canónica utiliza `ToolResult` y `ToolError`. Una excepción interna puede convertirse en un error estable que el resto del sistema pueda interpretar.

```text
excepción interna != contrato de error
```

La taxonomía utilizada es:

```text
protocol        -> protocolo
validation      -> validación
domain          -> dominio
transient       -> transitorio
timeout         -> tiempo de espera agotado
execution       -> ejecución
output_contract -> contrato de salida
```

La política inicial es deliberadamente conservadora:

```text
protocol        -> sin reintento automático
validation      -> sin reintento automático
domain          -> sin reintento automático
transient       -> reintento acotado
timeout         -> reintento solo si queda presupuesto
execution       -> sin reintento por defecto
output_contract -> sin reintento automático
```

#### Reintento (retry) no es reparación (repair)

Un reintento repite una operación con los mismos argumentos ya validados porque el fallo puede ser temporal. Una reparación cambia la llamada porque los argumentos eran incorrectos.

```text
reintento (retry) != reparación (repair)
```

La Semana 6 estudia reintentos controlados. No implementa un nuevo ciclo LLM para corregir llamadas defectuosas, porque eso introduce decisión iterativa y se acerca a flujos de trabajo (`workflows`) y agentes, reservados para semanas posteriores.

#### Tiempo de espera (timeout) y límite temporal total (deadline)

Se distinguen tres mecanismos:

```text
per_attempt_timeout
max_attempts
overall_deadline
```

El `timeout` limita un intento individual. El `overall_deadline` limita el tiempo total de la operación, incluidos intentos y esperas entre reintentos. Antes de continuar con un nuevo `backoff`, el entorno debe comprobar que todavía existe presupuesto suficiente.

```text
más reintentos != mejor sistema en todos los casos
```

#### Experimento A - Entorno de ejecución determinista (runtime)

La pregunta experimental es:

> ¿Qué efecto tiene agregar progresivamente validación, errores estructurados, reintentos y límites temporales cuando las entradas y los fallos permanecen fijos?

Se comparan cinco condiciones acumulativas:

```text
A = despacho directo ingenuo (dispatch)

B = A
  + contrato tipado de entrada

C = B
  + ToolResult/ToolError
  + contrato de salida

D = C
  + reintento selectivo (retry)
  + espera progresiva (backoff)

E = D
  + tiempo de espera por intento (timeout)
  + límite temporal total (deadline)
```

Las comparaciones permiten atribuir con mayor claridad el efecto de cada mecanismo:

```text
A vs B -> validación de entrada
B vs C -> errores estructurados + contrato de salida
C vs D -> reintentos selectivos
D vs E -> límites temporales
```

Los fallos se inyectan de forma determinista:

```text
none
transient_once
transient_twice
always_transient
slow_once
always_slow
internal_error
malformed_output
```

La inyección de fallos permite que todas las condiciones reciban los mismos estímulos y evita depender de fallos casuales de Internet o de servicios externos.

#### Métricas del Experimento A

```text
correct_outcome_rate
uncaught_exception_rate
error_classification_accuracy
invalid_execution_rate
transient_recovery_rate
mean_attempts
latency_mean_ms
latency_p95_ms
deadline_overrun_rate
```

`correct_outcome_rate` es la métrica principal porque un resultado correcto no siempre significa éxito de la herramienta. Si el SKU no existe, el comportamiento correcto puede ser producir un error `domain` y no ejecutar una acción inválida.

#### Experimento B - Llamada de funciones (function calling) con un LLM

Una vez fijado el entorno de ejecución, se puede evaluar la interfaz probabilística que produce llamadas a herramientas.

Cada solicitud permite:

```text
0 o 1 llamada a herramienta
```

No se incluyen llamadas paralelas, cadenas de múltiples herramientas, reparación automática, ReAct ni ciclos de agente.

El benchmark contiene 24 casos:

```text
6 calculator.calculate_total
6 catalog.lookup_stock
6 shipping.get_quote
6 casos sin herramienta (no_tool)
```

Las métricas son:

```text
tool_choice_accuracy
arguments_parse_rate
arguments_schema_valid_rate
arguments_semantic_accuracy
no_tool_accuracy
end_to_end_task_accuracy
```

La evaluación conserva dos distinciones esenciales:

```text
llamada válida != llamada correcta

éxito de la herramienta != éxito de la tarea
```

#### Análisis sintáctico (parsing) de la respuesta del modelo real

El cuaderno utiliza `tokenizer.parse_response(...)` cuando el tokenizer ofrece una plantilla compatible. Como mecanismo alternativo transparente mantiene un parser explícito de bloques `<tool_call> ... </tool_call>`.

El parser exige como máximo una llamada porque esa es una restricción experimental de Semana 6.

```text
parsear != reparar
```

#### Modelo real opcional

El modelo docente por defecto para la extensión es:

```text
Qwen/Qwen3-1.7B
```

Ejecución:

```bash
CC0F4_RUN_REAL_TOOL_LLM=1 make execute-cuaderno6
```

Cuando la plantilla lo permite se utiliza:

```text
do_sample=False
enable_thinking=False
```

El modelo real es opcional. El Experimento A y la validación estructural del cuaderno no dependen de él.

#### Ejecución sin modelo real

Para validar el software sin cargar un LLM:

```bash
CC0F4_RUN_REAL_TOOL_LLM=0 make execute-cuaderno6
```

En este modo:

```text
Experimento A
-> ejecución real del entorno local

Experimento B
-> fixtures deterministas de ToolCall
```

Por tanto:

```text
modo offline
= valida software, contratos, parsing y métricas

modo offline
!=
evidencia del comportamiento de un LLM real
```

#### Práctica autónoma

Debido al feriado del jueves, los ejercicios adicionales del cuaderno se consideran material de práctica autónoma. Pueden utilizarse para reforzar:

```text
allowlist
validación estructural vs validación de dominio
clasificación de excepciones
política de retry
presupuesto temporal
contrato de salida
evaluación de ToolCall
```

No se asume que los siete ejercicios deban resolverse durante la sesión presencial de dos horas.

#### Dependencias

Semana 6 utiliza el entorno global del curso. El camino canónico usa directamente:

```text
pydantic
transformers
pandas
```

El entorno global también mantiene disponibles:

```text
jsonschema
tenacity
httpx
pytest
```

Estas bibliotecas pueden emplearse en extensiones, verificaciones o ejercicios posteriores, pero la ausencia de laboratorio en Semana 6 significa que no se exige una actividad canónica separada basada en ellas.

La implementación explícita de reintento, espera progresiva y límites temporales con `asyncio` es deliberada:

```text
comprender el mecanismo -> medirlo -> después delegarlo a una librería
```

#### Material de referencia

Se aprovechan patrones de distintos repositorios y fuentes para conectar mecanismos pequeños con prácticas de ingeniería reproducible. Entre ellos se encuentran implementaciones de atención y sistemas de IA, ejemplos de contratos Pydantic, trazas, coordinación con `asyncio` y validación en la fuente.

No se reutilizan en esta semana:

```text
ciclos de agentes
planificación
memoria
transporte MCP
microservicios
Kubernetes
orquestación distribuida
```

MCP puede mencionarse como contexto tecnológico de interoperabilidad, pero no forma parte del entorno de ejecución canónico de Semana 6.

#### Reproducibilidad

El cuaderno genera:

```text
Semana6/resultados/latest_run.json
```

El manifiesto registra, entre otros:

```text
hashes SHA-256
seed
versiones
modo offline/real
modelo
programación de fallos (fault schedule)
políticas A/B/C/D/E
max_attempts
backoff
timeouts
deadline
métricas
limitaciones
```

La programación de fallos es parte del experimento y queda incluida en el hash del benchmark.

#### Validación

Desde la raíz del repositorio:

```bash
make check-semana6
```

Como Semana 6 no tiene laboratorio por el feriado del jueves 8 de octubre, debe estar incluida en:

```make
NO_LAB_WEEKS ?= 3 5 6
```

El `Makefile` valida entonces:

```text
Semana6/README.md
Semana6/Cuaderno6-CC-0F4.ipynb
notebooks mediante nbformat
```

sin exigir un notebook de laboratorio.

Para ejecutar el cuaderno sin modelo real:

```bash
CC0F4_RUN_REAL_TOOL_LLM=0 make execute-cuaderno6
```

Para comprobar conjuntamente las semanas cerradas:

```bash
make CHECK_WEEKS="1 2 3 4 5 6" check
```

#### Alcance deliberado

Semana 6 incluye:

```text
especificación de herramienta (tool specification)
llamada de funciones (function calling)
ejecución de funciones (function execution)
lista permitida (allowlist)
Pydantic
contrato de entrada
validación de dominio
contrato de salida
errores estructurados
inyección de fallos
reintento (retry)
backoff
timeout
overall deadline
trazas
latencia
análisis de errores
benchmark de function calling
```

Semana 6 no incluye:

```text
agentes
ReAct
planificación
memoria
LangGraph
LangChain
MCP como runtime del curso
ciclos de múltiples herramientas
llamadas paralelas a herramientas
ciclos automáticos de reparación con LLM
```

#### Criterio de cierre

El estudiante debe poder defender:

```text
salida estructurada != llamada de herramientas

llamada de herramientas != ejecución de herramientas

especificación de herramienta != implementación

válido por tipo != válido por esquema != válido para el dominio

contrato de entrada != contrato de salida

salida del LLM != entrada confiable

excepción != error estructurado de herramienta

retry != repair

retryable != failed

timeout != retry

per-attempt timeout != overall deadline

llamada válida != llamada correcta

éxito de la herramienta != éxito de la tarea

function calling != agente

MCP != function calling
```

#### Puente a la Semana 7

Semana 6 estudia cómo ejecutar una acción individual bajo contratos y políticas explícitas. Semana 7 cambia el foco hacia la evaluación sistemática de los sistemas de recuperación y RAG construidos en las semanas anteriores.

```text
Semana 6
acción individual verificable
        ->
Semana 7
evaluación sistemática de retrieval/RAG
```

Los flujos de trabajo (`workflows`), planificación, ReAct y agentes permanecen reservados para la Semana 9.
