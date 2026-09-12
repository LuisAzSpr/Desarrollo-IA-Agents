### **Lectura 6 - Herramientas (tools), contratos y ejecución robusta**

La Semana 6 introduce una frontera nueva en el curso. Hasta aquí, el modelo podía generar texto o producir estructuras verificables; ahora se le permite proponer acciones sobre funciones externas. Ese cambio parece pequeño, pero modifica de manera importante la arquitectura del sistema: una salida del modelo ya no es solamente contenido, sino una posible solicitud de ejecución.

La idea central de esta lectura es que un modelo de lenguaje puede **proponer** una acción, pero no debe tener autoridad directa para ejecutarla. Entre la generación probabilística y la función determinista debe existir una capa de software que valide, limite, ejecute y registre lo que ocurre. Esa capa constituye la frontera de confianza de la semana.

#### **1. La frontera de confianza**

Un LLM produce tokens. Incluso cuando esos tokens forman JSON válido o parecen describir correctamente una llamada a una función, siguen siendo la salida de un componente probabilístico. Por esa razón, la aplicación no debe interpretar la generación del modelo como una orden privilegiada.

La secuencia correcta es:

```text
LLM -> propuesta -> validación -> decisión de ejecución
```

La aplicación conserva la autoridad. Decide qué herramientas existen, qué argumentos son admisibles, qué errores pueden reintentarse, cuánto tiempo puede consumir una operación y qué resultado se devuelve al modelo o al usuario.

Esta separación es importante porque permite razonar sobre el sistema con dos niveles distintos. El LLM puede equivocarse al seleccionar una herramienta o al construir sus argumentos; el software, en cambio, debe encargarse de que esos errores no se conviertan automáticamente en acciones inválidas.

#### **2. Salida estructurada, llamada de funciones y ejecución**

Tres conceptos cercanos suelen confundirse: **salida estructurada** (`structured output`), **llamada de funciones** (`function calling`) y **ejecución de funciones** (`function execution`).

Una salida estructurada solamente garantiza que la respuesta adopta una forma determinada. Por ejemplo, un modelo puede producir un objeto JSON con campos predefinidos. Eso no significa todavía que exista una herramienta ni que deba ejecutarse nada.

La llamada de funciones da un paso adicional: la estructura representa una intención de utilizar una herramienta. El modelo puede producir algo semejante a:

```json
{
  "name": "catalog.lookup_stock",
  "arguments": {
    "sku": "SKU001"
  }
}
```

Aun así, la función no se ha ejecutado. La ejecución ocurre únicamente cuando el software externo al modelo interpreta la llamada, valida sus argumentos, encuentra una implementación permitida y decide invocarla.

Por eso conviene mantener desde el inicio dos distinciones:

```text
salida estructurada != llamada de funciones
llamada de funciones != ejecución de funciones
```

La diferencia no es terminológica. Es una separación de responsabilidades dentro de la arquitectura.

#### **3. Especificación de herramienta (tool specification)**

Para que un modelo pueda proponer una llamada necesita conocer qué herramientas están disponibles y qué argumentos espera cada una. Esa información se representa mediante una **especificación de herramienta** (`tool specification`).

Una especificación mínima incluye el nombre, una descripción y el esquema de parámetros. Por ejemplo:

```json
{
  "name": "catalog.lookup_stock",
  "description": "Consulta stock local por SKU.",
  "parameters": {
    "type": "object",
    "properties": {
      "sku": {
        "type": "string"
      }
    },
    "required": ["sku"]
  }
}
```

El modelo necesita esta interfaz, pero no necesita conocer la implementación interna de `catalog.lookup_stock`. Esa separación permite cambiar el código de la herramienta sin modificar necesariamente la interfaz que observa el modelo.

La aplicación, además, mantiene una **lista de herramientas permitidas** (`allowlist`). En el cuaderno, esa idea se expresa mediante una tabla de funciones:

```python
TOOLS = {
    "calculator.calculate_total": ...,
    "catalog.lookup_stock": ...,
    "shipping.get_quote": ...,
}
```

Si el modelo propone `catalog.delete_product` y esa herramienta no existe en la lista, el sistema no debería intentar adivinar qué quiso decir. Debe producir un error de protocolo. Antes de validar argumentos, primero hay que comprobar que la herramienta solicitada pertenece al conjunto permitido.

#### **4. El contrato estructural**

Una vez validado el nombre de la herramienta, el siguiente problema son sus argumentos. Para ello se utiliza un **contrato de entrada** que expresa tipos y restricciones estructurales.

Con Pydantic, por ejemplo, una cotización de envío puede declararse así:

```python
class ShippingQuoteInput(BaseModel):
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    weight_kg: float = Field(gt=0, le=50)
```

Este contrato puede verificar que `origin` y `destination` tengan tres caracteres y que `weight_kg` sea un número dentro de un rango. También puede detectar campos ausentes o valores con tipos incorrectos.

Sin embargo, el contrato estructural responde solamente a una pregunta: **¿la entrada tiene la forma esperada?**

No puede responder por sí solo a otra pregunta igualmente importante: **¿esa entrada tiene sentido dentro del dominio?**

#### **5. Validación de dominio**

Considere los siguientes argumentos:

```text
origin = LIM
destination = XXX
weight_kg = 2.0
```

Todos los campos pueden satisfacer el contrato estructural. `LIM` y `XXX` son cadenas de tres caracteres y `2.0` es un peso válido. Aun así, la ruta `LIM-XXX` puede no existir en el catálogo de envíos.

Esto muestra que hay distintos niveles de validez. Un dato puede tener el tipo esperado, cumplir un esquema y, sin embargo, ser inválido para el dominio.

Por esa razón, en la semana se utiliza la distinción:

```text
válido por tipo (type-valid)
!=
válido por esquema (schema-valid)
!=
válido para el dominio (domain-valid)
```

La diferencia es especialmente importante en sistemas con herramientas. Un modelo puede producir argumentos perfectamente parseables y compatibles con JSON Schema, pero semánticamente incorrectos para la operación que intenta realizar.

#### **6. Validación en la fuente**

Una regla debe comprobarse cerca del componente que posee el conocimiento necesario para decidirla. Pydantic conoce tipos y restricciones declarativas; el catálogo conoce qué SKU existen; el componente de envíos conoce qué rutas están disponibles.

Ese principio puede resumirse como **validar en la fuente** (`validate at source`). Si `catalog.lookup_stock` sabe exactamente qué SKU existen, no tiene sentido pedir a un LLM que determine esa regla mediante razonamiento probabilístico.

La consecuencia arquitectónica es importante: no toda validación debe concentrarse en una sola capa. Algunas reglas pertenecen al contrato estructural y otras al dominio. La separación evita duplicar conocimiento y permite producir errores más precisos.

#### **7. Contratos de salida**

La frontera de confianza no termina cuando la herramienta acepta sus argumentos. También debe verificarse lo que la herramienta devuelve.

Suponga que `shipping.get_quote` promete una salida con esta forma:

```json
{
  "origin": "LIM",
  "destination": "CUS",
  "weight_kg": 2.0,
  "price": 15.0
}
```

Si la implementación devuelve:

```json
{
  "route": "LIM-CUS",
  "cost": "unknown"
}
```

la herramienta fue ejecutada, pero violó su contrato de salida. El problema ya no está en los argumentos suministrados por el modelo, sino en la respuesta producida por la implementación.

La Semana 6 clasifica este caso como `output_contract`. La idea es simétrica a la validación de entrada: si no confiamos ciegamente en lo que produce el modelo, tampoco conviene asumir que toda implementación externa devolverá siempre la forma prometida.

#### **8. Excepción y error estructurado**

Dentro de un programa, una excepción es una forma natural de señalar un problema. Sin embargo, una arquitectura compuesta necesita representar los errores de manera más estable que el texto arbitrario de una excepción.

Por ejemplo, un fallo temporal puede convertirse en:

```json
{
  "status": "error",
  "error": {
    "code": "temporary_unavailable",
    "kind": "transient",
    "retryable": true,
    "message": "Servicio temporalmente no disponible."
  }
}
```

Este objeto no elimina las excepciones internas. Las transforma en una interfaz controlada que otros componentes pueden interpretar.

La diferencia es fundamental:

```text
excepción interna != contrato de error
```

Una excepción pertenece al mecanismo de implementación. `ToolError`, en cambio, pertenece a la interfaz del sistema.

#### **9. Taxonomía de errores**

Una política de ejecución robusta necesita distinguir por qué falló una operación, porque no todos los errores admiten la misma respuesta.

Un error `protocol` aparece cuando la propia llamada no pertenece al protocolo esperado, por ejemplo porque la herramienta no existe o porque el sobre de la llamada está mal formado. Repetir exactamente la misma petición no corrige el problema.

Un error `validation` indica que los argumentos no cumplen el contrato estructural: falta un campo, el tipo es incorrecto o un valor está fuera del rango permitido. Tampoco tiene sentido hacer un reintento automático con los mismos argumentos.

Un error `domain` aparece cuando la estructura es válida pero la operación no tiene sentido para el dominio, como un SKU inexistente o una ruta no disponible. De nuevo, repetir lo mismo no cambia la situación.

Los errores `transient`, en cambio, representan fallos temporales. Un servicio puede estar momentáneamente ocupado y funcionar unos milisegundos después. Estos errores sí son candidatos naturales a un reintento acotado.

Un `timeout` significa que la operación no terminó dentro del presupuesto temporal asignado. Puede ser reintentable, pero únicamente si la política lo permite y todavía existe presupuesto total.

Un error `execution` representa una excepción inesperada de implementación. La política de esta semana no lo reintenta por defecto, porque no hay evidencia de que repetir la operación vaya a corregirlo.

Finalmente, `output_contract` indica que la herramienta terminó, pero devolvió una respuesta incompatible con su contrato. También se considera no reintentable por defecto.

La taxonomía no intenta describir todos los fallos posibles de un sistema real. Su objetivo es hacer explícita una idea: **fallar no implica automáticamente reintentar**.

#### **10. Reintento (retry) frente a reparación (repair)**

Un **reintento** (`retry`) repite una operación con los mismos argumentos ya validados porque el fallo podría ser temporal. Una **reparación** (`repair`) modifica la llamada porque los argumentos originales eran incorrectos.

La diferencia puede verse con dos ejemplos. Si `shipping.get_quote` falla porque el servicio está temporalmente ocupado, repetir los mismos argumentos puede tener sentido. Si falla porque `weight_kg = -2`, repetir exactamente la misma llamada no solucionará nada.

Por eso:

```text
reintento (retry) != reparación (repair)
```

La Semana 6 se concentra en reintentos controlados. No implementa un ciclo en el que el error vuelve al LLM, el modelo genera argumentos nuevos y el sistema vuelve a decidir qué hacer. Ese comportamiento introduce una dinámica iterativa que corresponde mejor al estudio posterior de flujos de trabajo y agentes.

#### **11. Espera progresiva entre reintentos (backoff)**

Cuando un fallo es transitorio, tampoco conviene repetir inmediatamente la misma operación de manera indefinida. Si un servicio está degradado, una ráfaga de reintentos puede empeorar el problema.

Por esa razón se introduce una espera entre intentos, conocida como **backoff**. En el experimento docente se utiliza una política determinista: después del primer fallo se esperan 20 ms; después del segundo, 40 ms.

El objetivo no es encontrar el mejor algoritmo de backoff, sino hacer visible que un reintento también consume presupuesto temporal.

En sistemas de producción suele añadirse variación aleatoria (`jitter`) para evitar que muchos clientes se sincronicen y vuelvan a intentarlo al mismo tiempo. En esta semana no se incorpora `jitter`, porque introduciría otra variable dentro del experimento.

#### **12. Tiempo de espera por intento (timeout)**

Un **timeout por intento** establece cuánto tiempo puede durar una sola ejecución de la herramienta.

Si:

```text
per_attempt_timeout = 100 ms
```

y una operación tarda 140 ms, el intento se cancela por exceder su presupuesto. Esto no significa necesariamente que la lógica de la herramienta sea incorrecta. Significa que no cumplió la restricción temporal del sistema.

Esta distinción es importante porque el tiempo forma parte del contrato operativo. Una función puede producir una respuesta correcta y, aun así, ser inaceptable si llega demasiado tarde.

#### **13. Límite temporal total (deadline)**

Controlar cada intento por separado no es suficiente. Si se permiten varios reintentos, la suma de ejecuciones y esperas puede superar fácilmente el tiempo total que la aplicación está dispuesta a dedicar a la solicitud.

Por ejemplo:

```text
max_attempts = 3
per_attempt_timeout = 100 ms
backoff = 20 ms, 40 ms
overall_deadline = 230 ms
```

Aquí no basta con permitir tres intentos de 100 ms. Antes de iniciar un nuevo intento, el entorno de ejecución debe comprobar cuánto presupuesto queda y si existe tiempo suficiente para realizar el `backoff` y continuar.

Esta es la diferencia entre **timeout por intento** y **deadline total**. El primero limita una ejecución individual; el segundo limita la vida completa de la operación.

En el runtime de Semana 6, la comprobación se realiza antes de esperar el siguiente `backoff`. Si el presupuesto ya no alcanza, el sistema termina de manera controlada.

#### **14. Idempotencia**

Los reintentos son más seguros cuando repetir una operación no produce efectos adicionales. Consultar el stock de un producto es un ejemplo sencillo: realizar la misma consulta dos veces no duplica ninguna acción.

Crear un pago, registrar una compra o enviar una orden son casos distintos. Si la primera operación tuvo éxito pero la respuesta se perdió, un reintento ingenuo podría ejecutar el efecto por segunda vez.

Este problema conduce al concepto de **idempotencia**. En sistemas reales se utilizan mecanismos como `idempotency_key`, `request_id` o deduplicación para reconocer operaciones repetidas.

La Semana 6 solamente introduce esta idea para mostrar que una política de retry no puede diseñarse de manera aislada. No se implementan todavía transacciones ni sistemas distribuidos.

#### **15. Inyección de fallos (fault injection)**

Un experimento sobre robustez no debería depender de que una red o un servicio falle casualmente durante la clase. Si las condiciones cambian de una ejecución a otra, resulta difícil atribuir diferencias a la política evaluada.

Por eso el cuaderno utiliza **inyección de fallos** (`fault injection`). Los fallos se programan de manera determinista con escenarios como `transient_once`, `transient_twice`, `always_transient`, `slow_once`, `always_slow`, `internal_error` y `malformed_output`.

De esta manera, las condiciones A, B, C, D y E reciben exactamente el mismo estímulo. La variable que cambia es la política del runtime, no el comportamiento aleatorio del entorno.

La inyección de fallos convierte una demostración anecdótica en un experimento reproducible.

#### **16. Observabilidad**

Cuando una operación puede tener varios intentos, una métrica final no es suficiente para comprender lo ocurrido. Necesitamos poder reconstruir la secuencia.

Por eso cada intento genera una traza, por ejemplo:

```json
{
  "case_id": "r10",
  "condition": "D",
  "tool_name": "shipping.get_quote",
  "attempt": 2,
  "status": "error",
  "error_kind": "transient",
  "retryable": true,
  "latency_ms": 0.12
}
```

La traza permite recorrer el sistema en sentido inverso:

```text
métrica agregada -> caso -> intento -> causa
```

Esta capacidad es esencial para el análisis de errores. Dos configuraciones pueden producir la misma tasa global y, sin embargo, fallar de maneras muy diferentes.

#### **17. Elegir la métrica correcta**

Una métrica como `success_rate` puede ser engañosa. Imagine una solicitud con `quantity = 0`. Un runtime ingenuo podría ejecutar la función y devolver un número. Si contamos únicamente ejecuciones que producen una respuesta, podríamos considerarlo un éxito.

Pero el comportamiento correcto era rechazar esa entrada con un error de validación.

Por eso la métrica principal del Experimento A es `correct_outcome_rate`: mide si el sistema produjo el resultado que debía producir, tanto cuando ese resultado es una respuesta válida como cuando es un rechazo correctamente clasificado.

La diferencia obliga a pensar la evaluación en términos de comportamiento esperado y no solamente de operaciones que “terminaron”.

#### **18. El experimento incremental**

El Experimento A compara cinco condiciones acumulativas:

```text
A: despacho directo ingenuo (dispatch)
B: A + validación de entrada
C: B + errores estructurados y validación de salida
D: C + reintentos selectivos
E: D + timeout por intento y deadline total
```

La construcción incremental tiene una razón metodológica. Si se modificaran simultáneamente validación, errores, reintentos y límites temporales, una mejora en la métrica final no podría atribuirse con claridad a un componente específico.

En cambio, A frente a B permite estudiar el efecto de la validación de entrada; B frente a C muestra qué cambia al estructurar errores y validar salidas; C frente a D permite observar la recuperación de fallos transitorios; D frente a E introduce los límites temporales.

El experimento no pretende demostrar que E sea universalmente “mejor”. Pretende mostrar qué propiedad añade cada mecanismo y qué costo introduce.

#### **19. Llamada de funciones con un LLM**

Una vez fijado el runtime, puede estudiarse una pregunta distinta: ¿qué tan bien produce el modelo las llamadas?

Este segundo experimento ya no evalúa principalmente la robustez de la ejecución, sino la interfaz probabilística que decide si usar una herramienta, cuál seleccionar y qué argumentos producir.

La evaluación separa varias dimensiones: selección de herramienta (`tool selection`), análisis de argumentos (`arguments parsing`), validez del esquema (`schema validity`), corrección semántica y corrección de extremo a extremo (`end-to-end correctness`).

Considere este caso:

```text
usuario: "Consulta SKU003"

modelo:
tool = catalog.lookup_stock
args = {"sku": "SKU002"}
```

La herramienta seleccionada es correcta y los argumentos pueden cumplir perfectamente el esquema. Sin embargo, el SKU producido no corresponde a la solicitud del usuario.

Esto demuestra otra distinción importante:

```text
válido por esquema != semánticamente correcto
```

Un sistema de evaluación útil debe ser capaz de identificar esa diferencia.

#### **20. Análisis sintáctico (parsing) de respuestas**

Los modelos con uso de herramientas no siempre devuelven JSON puro. Algunos utilizan delimitadores especiales alrededor de la llamada, por ejemplo:

```text
<tool_call>
{"name": "...", "arguments": {...}}
</tool_call>
```

Por eso el runtime no debe asumir que toda la respuesta generada puede enviarse directamente a `json.loads()`.

Transformers puede proporcionar `tokenizer.parse_response(...)` cuando el tokenizer incluye una plantilla de respuesta compatible. El cuaderno utiliza esa capacidad cuando está disponible y mantiene un parser explícito como alternativa.

La alternativa no intenta “arreglar” silenciosamente respuestas defectuosas. Su trabajo es interpretar una estructura conocida. Esta diferencia mantiene otra separación útil:

```text
parsear != reparar
```

Si el modelo produce una estructura inválida, la evaluación debe poder registrarlo como fallo en lugar de ocultarlo mediante una reparación automática.

#### **21. Por qué `arguments_parse_rate` requiere cuidado**

La métrica `arguments_parse_rate` parece sencilla, pero contiene una sutileza. Si una solicitud debería producir una llamada a herramienta y el modelo no produce ninguna, no hay argumentos que hayan sido parseados correctamente.

Por tanto, en un caso con:

```text
should_call_tool = True
call = None
```

el resultado correcto es:

```text
arguments_parse_ok = False
```

Contarlo como `True` inflaría artificialmente la métrica. El problema no sería del parser, sino de la ausencia de una llamada requerida, pero desde el punto de vista del pipeline no existen argumentos disponibles para continuar.

Esta clase de detalle muestra por qué las métricas deben definirse antes de interpretar resultados.

#### **22. Tenacity como abstracción del reintento**

El cuaderno implementa primero el retry de manera explícita para que puedan observarse sus componentes: número de intento, condición que permite reintentar, espera entre intentos y presupuesto restante.

Una biblioteca como Tenacity permite expresar la misma política con una abstracción de más alto nivel. Esto reduce código repetitivo, pero no elimina las decisiones de diseño.

La biblioteca no sabe automáticamente si un `DomainError` debe reintentarse, cuál es el número razonable de intentos ni qué deadline corresponde a la aplicación. Esas decisiones continúan perteneciendo al sistema.

Por ello, Tenacity debe entenderse como una herramienta para **expresar** una política de reintento, no como un sustituto de la política.

#### **23. JSON Schema y Pydantic**

Pydantic y JSON Schema se conectan de manera natural en una arquitectura de herramientas. Pydantic permite expresar un contrato tipado dentro del runtime de Python y, a partir de ese modelo, puede generar JSON Schema para describir la misma interfaz hacia otros componentes.

La relación puede verse así:

```text
modelo Pydantic
-> JSON Schema
-> especificación de herramienta
```

Esto reduce la posibilidad de mantener manualmente dos contratos diferentes.

Sin embargo, generar un esquema no resuelve automáticamente la validación del dominio. Saber que `sku` es una cadena no permite saber si el SKU existe. El esquema describe principalmente forma y restricciones declarativas; el dominio conserva su propio conocimiento.

#### **24. MCP como contexto tecnológico**

Model Context Protocol (MCP) puede entenderse como un intento de estandarizar parte de la interoperabilidad entre aplicaciones de IA y servidores que exponen capacidades.

Para esta semana interesa observar la separación arquitectónica que propone: una aplicación puede descubrir o describir herramientas mediante un protocolo común, pero la existencia de ese protocolo no elimina la necesidad de contratos, validación, autorización, timeouts, retries ni observabilidad.

En otras palabras, MCP y function calling no son sinónimos. Una llamada de función describe una intención de utilizar una herramienta; MCP aborda una frontera de interoperabilidad más amplia entre componentes.

Semana 6 no necesita implementar un servidor MCP. El objetivo es comprender que, aun cuando exista un protocolo de integración, la frontera de confianza sigue siendo responsabilidad de la aplicación.

#### **25. El límite con los agentes**

Un sistema que recibe una solicitud, produce cero o una llamada a herramienta y devuelve una observación no necesita ser descrito todavía como un agente.

La arquitectura de esta semana puede resumirse como:

```text
solicitud -> 0/1 tool call -> validación -> ejecución -> resultado
```

Un sistema agéntico suele añadir otros elementos: estado persistente, ciclos de decisión, planificación, criterios de parada, memoria y múltiples acciones sucesivas.

Por eso conviene cerrar la semana con una última distinción:

```text
llamada de funciones (function calling) != agente
```

Mantener ese límite ayuda a estudiar cada mecanismo de manera aislada antes de combinarlos en arquitecturas más complejas.

#### **26. Preguntas adicionales**

1. ¿Por qué una llamada a herramienta (`tool call`) no debe ejecutarse directamente después de ser producida por el LLM?
2. ¿Qué diferencia existe entre una entrada válida por esquema (`schema-valid`) y una entrada válida para el dominio (`domain-valid`)?
3. ¿Por qué no se hace retry automático de un error de validación?
4. ¿Qué diferencia existe entre reintento (`retry`) y reparación (`repair`)?
5. ¿Qué problema resuelve el deadline total que no resuelve un timeout por intento?
6. ¿Por qué `success_rate` puede ser una métrica engañosa?
7. ¿Qué comparación del Experimento A permite atribuir una mejora específicamente a los reintentos?
8. ¿Cuándo repetir una operación puede ser peligroso aunque el error sea temporal?
9. ¿Por qué también debe validarse la salida de una herramienta?
10. ¿Qué diferencia conceptual existe entre MCP y function calling?
11. ¿Por qué la arquitectura de Semana 6 todavía no requiere un agente?
12. ¿Qué significa exactamente que un error sea `retryable`?.

La idea que debe permanecer al finalizar la lectura es simple: un LLM puede proponer una acción, pero la robustez del sistema depende de todo lo que ocurre después de esa propuesta. Contratos, validación, clasificación de errores, límites temporales y observabilidad son los mecanismos que convierten una llamada probabilística en una interacción controlada con software determinista.
