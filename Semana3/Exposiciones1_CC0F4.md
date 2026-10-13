### Exposiciones de la Semana 3 CC0F4

Curso CC-0F4, Tópicos de Ciencia de la Computación I, periodo 2026-2.

Eje de la Semana 3: **prompting, generación estructurada, JSON Schema, validación e ingeniería de contexto**.

Esta actividad complementa el trabajo desarrollado en `Cuaderno3-CC-0F4.ipynb`. La Semana 2 ya estudió logits, softmax, decoding, autoregresión, ventana de contexto y KV cache. Por eso las exposiciones no deben repetir esos contenidos como tema principal. Deben utilizarlos solamente cuando sean necesarios para explicar un problema propio de la Semana 3.

### Propósito de la actividad

La exposición busca que el estudiante pase de explicar conceptos a defender decisiones técnicas con evidencia. Cada tema amplía una parte del cuaderno de la Semana 3 y debe responder una pregunta concreta.

El estudiante debe poder explicar:

- qué problema intenta resolver,
- qué concepto de la Semana 3 está utilizando,
- qué variable modifica,
- qué mantiene constante,
- qué resultado obtiene,
- qué error o limitación observa,
- qué conclusión puede sostener con la evidencia disponible.

La idea central es mantener el mismo estándar experimental utilizado en los cuadernos del curso:

```text
pregunta
-> hipótesis
-> baseline
-> una modificación principal
-> métrica
-> resultado
-> análisis de error
-> limitación
-> conclusión
```

No se espera una exposición basada únicamente en diapositivas. Cada estudiante debe incluir una pequeña demostración, experimento o evidencia ejecutable.

### Relación directa con el Cuaderno 3

El Cuaderno 3 separa varias propiedades que no deben confundirse:

```text
prompt != context

JSON parseable != schema-valid

schema-valid != semanticamente correcto

prompt-only JSON != generación restringida

más contexto != mejor contexto

diferencia observada != conclusión universal
```

Las seis exposiciones desarrollan precisamente estas diferencias desde distintos ángulos.

La actividad también conserva el enfoque del cuaderno sobre trazabilidad. Cuando exista experimento, deben registrarse como mínimo:

```text
modelo
datos o casos
configuración
condición baseline
modificación aplicada
métrica
resultado
errores observados
limitación
conclusión
```

### Uso de herramientas de IA para investigación

Las herramientas de IA se utilizan para localizar, organizar y comprender literatura, no para reemplazar la lectura de las fuentes originales.

Se pueden utilizar:

- **Elicit**, para localizar artículos relacionados y construir comparaciones.
- **Connected Papers** o **ResearchRabbit**, para identificar antecedentes y trabajos posteriores.
- **Scite**, para observar cómo otros trabajos citan una fuente primaria.
- **SciSpace**, para apoyar la lectura de papers, localizar métodos, figuras, tablas y limitaciones.

El flujo recomendado es:

1. Partir de la fuente primaria asignada.
2. Leer las secciones principales y localizar problema, método, resultados y limitaciones.
3. Buscar trabajos relacionados y antecedentes.
4. Revisar si existen trabajos posteriores que apoyen, limiten o contradigan el resultado.
5. Preparar una conclusión propia basada en las fuentes originales.

Las herramientas de IA no deben aparecer como fuentes bibliográficas. La fuente es siempre el artículo, la especificación técnica o la documentación original.

Toda afirmación técnica, cifra, resultado o nombre de artículo producido por una herramienta debe verificarse antes de utilizarse.

Cada estudiante entrega un registro breve de uso de IA:

| Herramienta | Consulta realizada | Resultado útil | Error o límite detectado | Cómo se verificó |
| --- | --- | --- | --- | --- |
| | | | | |

### Estructura común de todas las exposiciones

Para mantener una sesión compacta, todas las exposiciones siguen la misma estructura.

#### Problema

Explicar qué dificultad concreta existe y por qué importa dentro de un sistema que utiliza LLM.

#### Fuente primaria

Presentar brevemente el trabajo principal utilizado como referencia. No es necesario resumir todo el paper. Se deben seleccionar únicamente las partes que ayudan a responder la pregunta de la exposición.

#### Concepto técnico

Explicar el concepto central utilizando el vocabulario de la Semana 3.

#### Demostración o experimento

Mostrar un ejemplo reproducible y pequeño. Debe existir una condición de referencia y una modificación controlada.

#### Evidencia

Presentar una tabla, salida del programa, gráfico sencillo, conjunto de errores o comparación que permita defender la conclusión.

#### Limitación

Indicar claramente qué no demuestra el experimento.

#### Conclusión

La conclusión debe ser proporcional a la evidencia observada.

#### Defensa oral

El estudiante debe poder explicar el código, la configuración, la decisión experimental y los errores sin depender de las diapositivas.



### Exposición 1. Diseño de prompts: zero-shot, few-shot y razonamiento explícito

#### Relación con Semana 3

Esta exposición estudia **prompting como variable experimental**.

El objetivo no es presentar una colección de técnicas de prompt engineering, sino demostrar que cambiar la forma en que se especifica una tarea puede modificar el comportamiento del modelo incluso cuando los pesos no cambian.

El estudiante debe distinguir claramente:

```text
instrucción
entrada
contexto
ejemplos
contrato de salida
```

#### Fuentes de partida

- Brown et al., *Language Models are Few-Shot Learners*.
- Wei et al., *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*.

Las referencias deben verificarse en la fuente original antes de la exposición.

#### Pregunta principal

¿Agregar ejemplos o razonamiento explícito modifica el rendimiento de una tarea cuando el modelo, los casos y la configuración de generación permanecen constantes?

#### Conceptos que deben explicarse

**Zero-shot** significa realizar la tarea mediante una instrucción sin ejemplos demostrativos.

**Few-shot** incorpora ejemplos dentro del contexto de entrada, pero no actualiza los pesos del modelo.

**Razonamiento explícito** agrega texto intermedio antes de la respuesta final. No debe asumirse que una explicación más extensa implica una respuesta más correcta.

También debe explicarse que los ejemplos consumen parte de la ventana de contexto.

#### Experimento sugerido

Seleccionar una tarea pequeña de clasificación o respuesta exacta.

Comparar:

```text
condición A:
zero-shot

condición B:
few-shot

condición C:
few-shot con razonamiento explícito
```

Mantener constantes:

```text
modelo
casos
decoding
contrato de salida
métrica
```

Medir:

```text
exactitud
tokens de entrada
tokens de salida
errores por condición
```

No cambiar simultáneamente prompt, modelo y dataset.

#### Qué debe discutirse

El estudiante debe explicar si la mejora observada puede atribuirse al cambio del prompt y qué otros factores podrían influir.

También debe señalar que una cadena de razonamiento plausible puede contener errores y que una respuesta más larga no equivale automáticamente a una respuesta mejor.

#### Preguntas de defensa

- ¿Por qué few-shot puede cambiar la respuesta aunque no actualice los pesos?
- ¿Qué variable cambió realmente entre las condiciones?
- ¿Cómo distinguir una mejora real de una respuesta simplemente más extensa?
- ¿Qué pasaría si el mismo experimento se ejecutara con un modelo más pequeño?

#### Conexión con proyectos posteriores

Esta exposición ayuda a definir un baseline de prompting antes de introducir retrieval, herramientas o agentes.



### Exposición 2. Generación estructurada con JSON Schema, Pydantic y reintentos

#### Relación con Semana 3

Esta exposición extiende directamente la cadena trabajada en el Cuaderno 3:

```text
raw text
-> JSON parse
-> JSON Schema
-> validación
-> evaluación semántica
```

El problema central es convertir una respuesta generativa en una interfaz consumible por otro componente de software.

#### Fuentes de partida

- Especificación de JSON Schema.
- Documentación de Pydantic v2.
- Un trabajo académico relacionado con **structured output**, que debe ser verificado por el estudiante antes de utilizarse.

#### Pregunta principal

¿Qué cambia cuando una salida libre pasa a ser una salida con contrato, validación y política explícita de reintento?

#### Conceptos que deben explicarse

El estudiante debe diferenciar:

**JSON parseable**, que indica que la sintaxis puede interpretarse.

**Schema-valid**, que indica que el objeto satisface el contrato.

**Semantically correct (semánticamente correcto)**, que indica que el contenido responde correctamente al problema.

Debe quedar claro:

```text
JSON parseable != schema-valid

schema-valid != semanticamente correcto
```

También se debe explicar que un reintento ocurre después de detectar un fallo. Por tanto, sigue siendo una estrategia distinta de restringir la generación durante decoding.

#### Experimento sugerido

Utilizar un conjunto pequeño de textos y extraer tres o cuatro campos.

Comparar:

```text
condición A:
prompt sin schema explícito

condición B:
prompt con contrato estructurado

condición C:
contrato + validación + reintento limitado
```

Medir:

```text
tasa de JSON exacto
tasa de JSON recuperable
schema_valid_rate
exactitud por campo
número de reintentos
errores semánticos
```

#### Qué debe discutirse

Un objeto puede cumplir el schema y contener información incorrecta.

Los reintentos pueden mejorar la tasa de formato válido, pero agregan nuevas llamadas, latencia y costo.

Un esquema demasiado restrictivo puede solucionar el formato sin mejorar la semántica.

#### Preguntas de defensa

- ¿Qué diferencia existe entre JSON válido y respuesta correcta?
- ¿Qué debe hacer el sistema después de un segundo fallo?
- ¿Qué campos deberían ser obligatorios?
- ¿Cuándo conviene permitir `null`, `unknown` o un estado de abstención?

#### Conexión con proyectos posteriores

Este tema constituye la base de las salidas estructuradas utilizadas posteriormente por herramientas y agentes.

### Exposición 3. Decodificación restringida por gramática y máscaras de logits

#### Relación con Semana 3

Esta exposición es el puente directo entre la Semana 2 y la Semana 3.

La Semana 2 estudió logits, softmax y decoding. La Semana 3 estudia salidas estructuradas.

Aquí ambas ideas se unen.

#### Fuentes de partida

- Willard y Louf, *Efficient Guided Generation for Large Language Models*.
- Geng et al., *Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning*.

Las referencias deben verificarse antes de su uso.

#### Pregunta principal

¿Es mejor corregir una salida inválida después de generarla o impedir que el modelo produzca ciertas secuencias inválidas durante decoding?

#### Conceptos que deben explicarse

En generación libre, el modelo conserva su distribución normal de candidatos.

En generación restringida, algunos tokens pueden ser enmascarados porque violarían una gramática, una expresión regular o un conjunto cerrado de etiquetas.

El estudiante debe recuperar de la Semana 2 únicamente lo necesario para explicar que la máscara modifica qué tokens siguen siendo candidatos antes de seleccionar el siguiente token.

Debe quedar clara la diferencia:

```text
prompt-only JSON != constrained generation (generación restringida)
```

#### Experimento sugerido

Realizar una clasificación con un conjunto cerrado de etiquetas.

Comparar:

```text
condición A:
generación libre + post-procesamiento

condición B:
generación restringida
```

Medir:

```text
tasa de salida válida
exactitud
errores semánticos
casos donde una salida válida sigue siendo incorrecta
```

Como evidencia adicional se puede mostrar la lista de candidatos antes y después de aplicar la restricción.

#### Qué debe discutirse

La restricción puede garantizar la forma sin garantizar la verdad.

Una etiqueta incorrecta puede seguir siendo perfectamente válida.

La implementación depende del tokenizador, porque una etiqueta puede corresponder a uno o varios tokens.

#### Preguntas de defensa

- ¿Por qué la restricción debe intervenir durante decoding?
- ¿Qué ocurre si una etiqueta se divide en varios tokens?
- ¿Qué problema resuelve la generación restringida que no resuelve un parser?
- ¿Cuándo sería preferible validar y reintentar?

#### Conexión con proyectos posteriores

Es útil en clasificación, enrutamiento y llamadas a herramientas con conjuntos cerrados de opciones.



### Exposición 4. Ingeniería de contexto y posición de la evidencia

#### Relación con Semana 3

Esta exposición amplía directamente el experimento:

```text
baseline
neutral
conflicting
```

del Cuaderno 3.

El cuaderno estudia qué ocurre cuando cambia el contenido del contexto. Esta exposición agrega otra dimensión: **la posición de la evidencia dentro del contexto**.

#### Fuente de partida

- Liu et al., *Lost in the Middle: How Language Models Use Long Contexts*.

La referencia debe verificarse antes de la exposición.

#### Pregunta principal

¿El modelo utiliza de la misma manera una evidencia relevante cuando aparece al inicio, en el medio o al final del contexto?

#### Conceptos que deben explicarse

La **ingeniería de contexto** no consiste solamente en introducir más información.

También implica decidir:

```text
qué información incluir
cuánta información incluir
en qué orden
en qué posición
qué información excluir
```

La exposición debe reforzar:

```text
más contexto != mejor contexto
```

#### Experimento sugerido

Construir preguntas con una evidencia relevante y varios distractores.

Comparar:

```text
evidencia al inicio
evidencia en posición intermedia
evidencia al final
```

Mantener constantes:

```text
pregunta
modelo
distractores
cantidad total aproximada de información
decoding
```

Medir:

```text
exactitud por posición
tokens de entrada
errores
```

#### Qué debe discutirse

La posición y la longitud pueden estar mezcladas si el experimento no se controla correctamente.

Un resultado observado en una tarea concreta no debe generalizarse a todos los modelos ni a todas las longitudes de contexto.

#### Preguntas de defensa

- ¿Cómo separar el efecto de la posición del efecto de la longitud?
- ¿Qué implica este resultado para ordenar fragmentos recuperados?
- ¿Cómo decidirías cuántos fragmentos incluir?
- ¿Qué error experimental aparecería si cada condición tuviera una longitud distinta?

#### Conexión con proyectos posteriores

Prepara directamente el estudio de embeddings, retrieval, chunking y RAG.



### Exposición 5. Sensibilidad al formato del prompt y robustez de la evaluación

#### Relación con Semana 3

Esta exposición refuerza el principio del curso:

```text
cambiar una variable a la vez
```

También muestra que diferencias aparentemente superficiales en una plantilla pueden convertirse en una variable experimental.

#### Fuente de partida

- Sclar, Choi, Tsvetkov y Suhr, *Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I learned to start worrying about prompt formatting*.

La fuente primaria debe ser leída y las cifras utilizadas deben verificarse directamente en el paper.

#### Pregunta principal

¿Dos prompts que expresan la misma tarea con distinto formato producen resultados suficientemente similares como para considerarlos equivalentes?

#### Conceptos que deben explicarse

Una evaluación basada en una sola plantilla puede confundir:

```text
efecto del método
```

con:

```text
efecto del formato
```

Cambios como separadores, orden visual, etiquetas o disposición de ejemplos pueden convertirse en variables experimentales.

#### Experimento sugerido

Elegir una tarea de clasificación y preparar varias plantillas que mantengan el significado.

Ejemplos de cambios:

```text
separadores
orden de campos
saltos de línea
etiquetas de secciones
forma de presentar ejemplos
```

Mantener constantes:

```text
modelo
casos
contenido semántico
decoding
métrica
```

Medir:

```text
accuracy por plantilla
mejor resultado
peor resultado
media
dispersión
casos que cambian de predicción
```

#### Qué debe discutirse

El estudiante debe explicar por qué reportar únicamente la mejor plantilla puede producir una imagen engañosa del rendimiento.

También debe reconocer que el espacio posible de formatos es grande y que probar algunas variantes no caracteriza todas las formas de prompt.

#### Preguntas de defensa

- ¿Qué cambió realmente entre tus variantes?
- ¿Qué se mantuvo fijo?
- ¿Qué conclusión cambiaría si reportaras únicamente la mejor plantilla?
- ¿Cómo decidirías cuántas variantes son suficientes para tu experimento?

#### Conexión con proyectos posteriores

Ayuda a evitar que una mejora atribuida a retrieval, herramientas u otra arquitectura provenga en realidad de una plantilla de prompt diferente.

### Exposición 6. Inyección de prompt y separación entre instrucciones y datos

#### Relación con Semana 3

Esta exposición estudia una consecuencia directa de:

```text
prompt != context
```

y de utilizar contexto externo.

El alcance debe mantenerse en **ingeniería de contexto y validación**. No es necesario desarrollar todavía una arquitectura completa de seguridad para agentes.

#### Fuentes de partida

- Greshake et al., *Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection*.
- Perez y Ribeiro, *Ignore Previous Prompt* como lectura complementaria.

Las referencias deben verificarse antes de la exposición.

#### Pregunta principal

¿Qué ocurre cuando un fragmento tratado como dato contiene instrucciones que compiten con las instrucciones originales del sistema?

#### Conceptos que deben explicarse

Desde el punto de vista del modelo, instrucciones y datos finalmente forman parte de una secuencia de tokens.

El sistema puede marcar y delimitar diferentes secciones, pero eso no convierte automáticamente los datos externos en contenido incapaz de influir sobre la generación.

Debe distinguirse:

```text
instrucción del sistema
entrada del usuario
contexto externo
salida validada
```

#### Experimento sugerido

Crear un mini corpus con documentos normales y algunos documentos que contengan instrucciones conflictivas.

Comparar:

```text
condición A:
contexto sin defensa adicional

condición B:
contexto delimitado y marcado como datos

condición C:
delimitadores + contrato de salida + validación
```

Medir:

```text
tasa de éxito del ataque
exactitud en la tarea legítima
schema_valid_rate
casos fallidos
```

#### Qué debe discutirse

La validación de schema controla la forma, no la intención del contenido.

Los delimitadores pueden ayudar a estructurar el prompt, pero no constituyen por sí solos una garantía completa.

La exposición debe evitar adelantarse demasiado a permisos, ejecución de herramientas o agentes. Esos temas pueden retomarse posteriormente.

#### Preguntas de defensa

- ¿Por qué marcar una sección como "datos" no garantiza que el modelo ignore sus instrucciones?
- ¿Qué diferencia existe entre impedir una salida inválida y evitar una decisión insegura?
- ¿Qué información del contexto debería considerarse no confiable?
- ¿Qué evidencia mostraría que una mitigación mejoró el sistema sin destruir la utilidad?

#### Conexión con proyectos posteriores

Prepara el análisis de riesgo en sistemas RAG y, más adelante, en agentes con herramientas.

### Evidencia mínima que debe entregar cada estudiante

Cada estudiante debe presentar un pequeño paquete de evidencia.

#### Archivo o cuaderno

Debe contener el código necesario para reproducir la demostración.

#### Tabla de configuración

Ejemplo:

| Elemento | Valor |
| --- | --- |
| Modelo | |
| Dataset o casos | |
| Condición baseline | |
| Modificación | |
| Decoding | |
| Métrica principal | |
| Seed, si corresponde | |

#### Resultados

Debe mostrarse al menos una tabla comparativa.

Ejemplo:

| Condición | Métrica principal | Métrica secundaria | Errores observados |
| --- | ---: | ---: | --- |
| Baseline | | | |
| Variante | | | |

#### Un caso correcto y un caso problemático

El estudiante debe mostrar evidencia concreta, no solamente promedios.

#### Limitación

Debe escribirse explícitamente una frase que empiece de forma similar a:

```text
Este experimento no permite concluir que...
```

#### Conclusión

Debe utilizar una formulación proporcional a la evidencia.

Una forma adecuada es:

```text
Bajo este modelo, estos casos y esta configuración, observamos...
```

Debe evitarse:

```text
Los LLM siempre...
Todos los modelos...
Esta técnica demuestra que...
```

cuando la evidencia no permita sostener esas afirmaciones.

### Puente hacia la Semana 4

En la Semana 3 el contexto sigue siendo seleccionado manualmente.

La siguiente pregunta será:

```text
¿cómo recuperar automáticamente el contexto relevante?
```

Ese problema conduce a:

```text
embeddings
similitud
chunking
dense retrieval
FAISS
```

Por eso esta actividad cierra la Semana 3 preparando el paso desde **ingeniería de contexto manual** hacia **recuperación automática de contexto**.
