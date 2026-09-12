### Semana 2 - Exposiciones de refuerzo y búsqueda académica asistida

#### Propósito

Las exposiciones de Semana 2 forman parte del bloque final del Laboratorio 2.

No son una actividad adicional ni sustituyen la evaluación formal E1 de Semana 3.

El objetivo tiene dos partes:

```text
aprender a buscar y contrastar literatura -> comprender una técnica de inferencia -> defender un claim con evidencia
```

Esta es la primera actividad del curso que utiliza de manera explícita:

```text
Elicit
ResearchRabbit
Connected Papers
Scite
SciSpace
Consensus
```

Por ello, no se espera que el estudiante ya domine estas herramientas.

La guía explica para qué sirve cada una. **Cada grupo solo debe usar dos herramientas con funciones distintas y verificar la fuente primaria.**

#### Relación con el Laboratorio 2

El Laboratorio 2 reserva al final:

```text
110-210 min
EXPOSE/DEFEND
```

El bloque máximo disponible para exposiciones es de 100 minutos.

Cada grupo dispone de:

```text
7 min exposición
3 min defensa
total: 10 min por grupo
```

Si existen menos grupos, la sesión termina antes.

La búsqueda bibliográfica y la preparación se podrían realizar antes del jueves.

Durante el bloque final del laboratorio se presenta y defiende el trabajo ya preparado.

#### Qué se evalúa realmente

La exposición no consiste en resumir un paper ni en mostrar una respuesta generada por IA.

Debe reconstruir:

```text
problema -> pregunta -> paper primario -> baseline -> mecanismo -> recurso afectado -> evidencia experimental
-> limitación -> conexión con Laboratorio 2
```

El estudiante debe poder distinguir:

```text
lo que afirma una herramienta != lo que demuestra el paper != lo que concluye el grupo
```

#### Regla principal de uso de herramientas

Las seis herramientas no realizan la misma función.

| Rol | Herramientas recomendadas | Pregunta que ayudan a responder |
|---|---|---|
| Descubrimiento y síntesis inicial | Elicit, SciSpace, Consensus | ¿Qué papers podrían ser relevantes? |
| Exploración de red | ResearchRabbit, Connected Papers | ¿Qué trabajos anteriores, relacionados o posteriores debo revisar? |
| Contexto de citación | Scite | ¿Cómo ha sido citado un claim o paper por trabajos posteriores? |
| Verificación | arXiv, DOI, conferencia, journal, repositorio oficial | ¿Qué dice realmente la fuente primaria? |

Regla:

```text
herramienta -> orienta
fuente primaria -> sustenta
```

No se acepta como evidencia final:

```text
"lo dijo Elicit"
"lo dijo SciSpace"
"lo dijo Consensus"
"Scite dice que está supported"
"aparece cerca en Connected Papers"
```

#### Primera vez - tutorial guiado común

Antes de que cada grupo investigue su tema, el docente puede mostrar un recorrido breve con un mismo caso.

Caso de práctica:

```text
Tema:
Grouped-Query Attention

Pregunta:
How does grouped-query attention change decoder inference compared with multi-head attention?

Seed paper:
GQA: Training Generalized Multi-Query Transformer Models
from Multi-Head Checkpoints
Ainslie et al., 2023

Fuente:
https://arxiv.org/abs/2305.13245
```

Objetivo:

```text
misma pregunta -> herramientas diferentes -> funciones diferentes
```

No se busca producir una revisión exhaustiva.

Se busca entender el workflow.

#### Paso 0 - Registro mínimo

Antes de comenzar, registra:

| Campo | Registro |
|---|---|
| Tema | |
| Pregunta | |
| Herramienta 1 | |
| Query o acción | |
| Herramienta 2 | |
| Seed paper | |
| Paper relacionado | |
| Fuente primaria verificada | |
| Claim | |
| Evidencia | |
| Limitación | |

La trazabilidad forma parte de la actividad.

#### Paso 1 - Elicit: descubrir papers

Sitio:

```text
https://elicit.com/
```

Uso:

```text
pregunta en lenguaje natural -> búsqueda semántica -> papers candidatos
```

Procedimiento mínimo:

1. formula una pregunta concreta,
2. identifica el paper primario,
3. selecciona un paper relacionado,
4. abre la fuente original antes de aceptar un claim.

Query de práctica:

```text
How does grouped-query attention affect inference speed,
KV-cache requirements and model quality compared with
multi-head attention in autoregressive Transformers?
```

Producto esperado:

```text
1 seed paper + 1 paper relacionado
```

#### Paso 2 - ResearchRabbit: explorar desde un seed paper

Sitio:

```text
https://www.researchrabbit.ai/
```

Uso:

```text
seed paper -> trabajos anteriores/similares/posteriores
```

Procedimiento mínimo:

1. busca el seed paper,
2. revisa trabajos relacionados,
3. selecciona uno cuya relación puedas explicar,
4. abre el paper seleccionado.

Producto esperado:

```text
1 paper relacionado + explicación de la relación
```

Una conexión sirve para descubrir qué leer, no para demostrar un claim.

#### Paso 3 - Connected Papers: observar el vecindario conceptual

Sitio:

```text
https://www.connectedpapers.com/
```

Uso:

```text
seed paper -> grafo de similitud -> prior works/derivative works
```

Importante:

```text
grafo de Connected Papers != árbol exacto de citaciones
```

Producto esperado:

```text
1 prior work o 1 derivative work
```

No se acepta seleccionar un paper únicamente porque aparece cerca en el grafo.

#### Paso 4 - Scite: revisar el contexto de citación

Sitio:

```text
https://scite.ai/
```

Uso:

```text
paper -> citation statements -> contexto
```

Puede mostrar categorías como:

```text
supporting
mentioning
contrasting
```

Importante:

```text
supporting != paper correcto
contrasting != paper incorrecto
```

La clasificación orienta la revisión. No sustituye la lectura del paper citante.

Producto esperado:

```text
1 cita relevante + interpretación del grupo
```

#### Paso 5 - SciSpace: leer y extraer evidencia

Sitio:

```text
https://scispace.com/
```

Puede utilizarse para búsqueda o para consultar un PDF.

No preguntes solamente:

```text
Summarize this paper.
```

Usa una pregunta estructurada:

```text
Using only this paper, identify:

1. the problem,
2. the baseline,
3. the method,
4. the metric,
5. the main result,
6. one limitation.

Indicate the section, table or figure
that should be checked in the original paper.
```

Después:

```text
respuesta -> sección/tabla/figura -> verificación manual
```

#### Paso 6 - Consensus: contrastar una pregunta

Sitio:

```text
https://consensus.app/
```

Uso:

```text
pregunta científica -> papers relevantes -> síntesis inicial
```

Ejemplo:

```text
What evidence compares grouped-query attention with
multi-head attention for inference efficiency and model quality?
```

Producto esperado:

```text
1 paper relevante + 1 claim para verificar en la fuente primaria
```

No interpretes la síntesis automática como consenso definitivo del campo.

#### Qué debes recordar de las seis herramientas

| Herramienta | Uso principal | No confundir con |
|---|---|---|
| Elicit | descubrimiento semántico | fuente primaria |
| ResearchRabbit | navegación por literatura | prueba de un claim |
| Connected Papers | mapa de similitud | árbol exacto de citaciones |
| Scite | contexto de citación | score universal de calidad |
| SciSpace | búsqueda y lectura asistida | verificación final |
| Consensus | búsqueda y síntesis | consenso definitivo |

La idea central es:

```text
Elicit/SciSpace/Consensus -> encontrar y orientar
ResearchRabbit/Connected Papers -> explorar relaciones
Scite -> revisar contexto de citación
paper original -> verificar
```

#### Workflow obligatorio para la exposición real

Cada grupo utiliza:

```text
1 herramienta de descubrimiento + 1 herramienta de exploración o contraste + fuente primaria
```

Ejemplos válidos:

```text
Elicit -> ResearchRabbit -> arXiv
```

```text
SciSpace -> Scite -> paper de conferencia
```

```text
Consensus -> Connected Papers -> DOI
```

No es obligatorio utilizar las seis herramientas.

#### Temas de exposición

Los temas base son:

| # | Tema | Seed paper sugerido | Pregunta central |
|---:|---|---|---|
| 1 | FlashAttention | Dao et al. (2022), arXiv:2205.14135 | ¿Cómo puede attention exacta reducir IO sin cambiar su resultado matemático? |
| 2 | MQA/GQA | Ainslie et al. (2023), arXiv:2305.13245 | ¿Qué cambia al reducir KV heads y cuál es el trade-off? |
| 3 | MLA | DeepSeek-V2 (2024), arXiv:2405.04434 | ¿Qué significa comprimir K/V en una representación latente? |
| 4 | SWA y contexto largo | Mistral 7B (2023), arXiv:2310.06825 | ¿Qué se gana y qué se restringe al limitar el rango visible? |
| 5 | PagedAttention/vLLM | Kwon et al. (2023), arXiv:2309.06180 | ¿Por qué administrar KV cache es también un problema de sistemas? |
| 6 | Speculative Decoding | Leviathan et al. (2022/2023), arXiv:2211.17192 | ¿Cómo reducir pasos seriales preservando la distribución objetivo? |

Si existen más grupos pueden utilizarse:

| # | Tema | Seed paper sugerido |
|---:|---|---|
| 7 | RoPE vs ALiBi | RoFormer/ALiBi |
| 8 | KV Cache Quantization | KIVI |
| 9 | Prefill vs Decode | DistServe |
| 10 | Decoding y Neural Text Degeneration | Holtzman et al. |

Cada grupo trabaja únicamente su tema.

#### Pregunta de investigación por tema

No uses como pregunta:

```text
What is FlashAttention?
```

Usa una pregunta que permita comparar y defender.

Ejemplos:

```text
FlashAttention
->
Under what hardware and sequence-length conditions does
FlashAttention reduce runtime or memory traffic compared with
a standard exact-attention implementation?
```

```text
GQA
->
What inference resource changes when the number of KV heads is
reduced, and what evidence exists about the quality trade-off?
```

```text
PagedAttention
->
How does paging the KV cache address fragmentation and batching
problems in LLM serving?
```

```text
Speculative Decoding
->
How can a draft model reduce serial target-model decoding while
preserving the target distribution?
```

#### Prompt base para descubrimiento

```text
Research question:

[QUESTION]

Find primary research papers relevant to this question.

For each candidate identify:
1. title and year,
2. whether it is a primary method paper or later evaluation,
3. baseline,
4. proposed mechanism,
5. evaluation metric,
6. main reported result,
7. stated limitation.

Prioritize original papers and verifiable sources.
Do not strengthen a claim beyond what the paper reports.
```

#### Prompt para leer el paper primario

```text
Using only the supplied primary paper, extract:

1. problem,
2. baseline,
3. method,
4. variable modified,
5. resource affected,
6. metric,
7. main result,
8. limitation.

Indicate the section, table or figure that should be verified manually.

If the paper does not support an item, write:
NOT ESTABLISHED BY THIS PAPER.
```

#### Producto de la exposición

La presentación tiene como máximo cuatro bloques conceptuales:

```text
1. problema + baseline
2. mecanismo
3. evidencia
4. limitación + conexión con Laboratorio 2
```

Debe contener una tabla final:

| Campo | Contenido |
|---|---|
| Problema | |
| Baseline | |
| Método | |
| Variable modificada | |
| Nivel del sistema | arquitectura/kernel/runtime/decoding |
| Recurso afectado | |
| Métrica | |
| Resultado principal | |
| Limitación | |
| Relación con Experimento A o B | |

#### Preguntas que se debe tener en cuenta

1. ¿Por qué elegiste ese seed paper?
2. ¿Qué encontró la primera herramienta?
3. ¿Qué añadió la segunda herramienta?
4. ¿Qué tabla, figura o sección respalda tu resultado principal?
5. ¿Contra qué baseline se compara?
6. ¿La mejora es analítica, estimada o medida?
7. ¿El método cambia arquitectura, kernel, runtime o decoding?
8. ¿El resultado depende del hardware?
9. ¿Qué afirmación no podrías defender solo con el abstract?
10. ¿Qué parte conecta directamente con Experimento A o Experimento B?
11. ¿Qué claim tuviste que reducir después de revisar la fuente primaria?
12. ¿Qué herramienta fue menos útil para tu pregunta y por qué?.

#### Criterio de calidad

Una exposición fuerte muestra:

```text
pregunta precisa + fuente primaria + mecanismo entendido + evidencia + limitación + conexión experimental
```

No se considera suficiente:

```text
prompt -> respuesta de IA -> diapositiva
```

Tampoco:

```text
muchos papers -> sin pregunta -> sin baseline -> sin evidencia verificable
```

#### Checklist antes de exponer

El grupo debe poder responder "sí":

- ¿Tenemos una pregunta concreta?
- ¿Identificamos el paper primario?
- ¿Usamos dos herramientas con funciones distintas?
- ¿Abrimos la fuente original?
- ¿Podemos señalar una tabla, figura, sección o ecuación?
- ¿Tenemos un baseline?
- ¿Podemos nombrar la métrica?
- ¿Conocemos al menos una limitación?
- ¿Nuestro claim es proporcional a la evidencia?
- ¿Podemos conectarlo con el Laboratorio 2?.

#### Regla final

Las herramientas aceleran partes distintas del proceso.

No reemplazan el juicio científico.

```text
buscar != leer
leer != verificar
verificar != generalizar
muchas citas != evidencia suficiente
```

La responsabilidad final del grupo es poder defender:

> Esta es nuestra afirmación, esta es la fuente que la sustenta, estas son las condiciones bajo las que se obtuvo y esta es la limitación que impide generalizarla sin más evidencia.
