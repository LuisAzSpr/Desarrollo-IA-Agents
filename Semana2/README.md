### Semana 2 - Inferencia: logits, decoding, contexto y KV cache

#### Propósito

La Semana 2 continúa directamente desde la arquitectura causal estudiada en Semana 1. El objetivo ya no es reconstruir attention, sino estudiar qué ocurre cuando un Transformer causal se usa para **inferir el siguiente token y generar una secuencia**.

La cadena conceptual es:

```text
representación contextual
  ->
LM head
  ->
logits
  ->
softmax
  ->
distribución del siguiente token
  ->
decoding
  ->
nuevo token
  ->
contexto ampliado
  ->
autoregresión
```

A medida que el contexto crece aparece un segundo problema:

```text
más contexto -> más K/V históricos -> más memoria y tráfico -> KV cache -> MHA/GQA/SWA/MLA
```

Al finalizar la semana debes poder:

- distinguir logits de probabilidades,
- explicar qué hace `softmax` y qué no hace,
- implementar temperatura, top-k y top-p sin depender de `generate()`,
- diferenciar greedy decoding de sampling,
- explicar la factorización autoregresiva,
- razonar sobre presupuesto de tokens y ventana de contexto,
- explicar qué almacena un KV cache y qué cómputo evita,
- estimar memoria de KV cache bajo supuestos explícitos,
- comparar MHA, GQA, SWA y una aproximación conceptual a MLA,
- distinguir una estimación analítica de un benchmark físico,
- formular conclusiones proporcionales a la evidencia.

#### Material de la semana

| Recurso | Función |
|---|---|
| [`Cuaderno2-CC-0F4.ipynb`](Cuaderno2-CC-0F4.ipynb) | Material canónico del lunes: logits, softmax, decoding, autoregresión, contexto y KV cache |
| [`Laboratorio2-CC-0F4.ipynb`](Laboratorio2-CC-0F4.ipynb) | Laboratorio experimental del jueves |
| [`Exposiciones2-CC-0F4.md`](Exposiciones2-CC-0F4.md) | Guía de búsqueda académica y exposiciones de refuerzo |

Las exposiciones de Semana 2 son de **refuerzo**. No sustituyen la evaluación E1 de Semana 3.

No hay una lectura adicional obligatoria para toda la clase en esta semana. Cada grupo consulta la fuente primaria correspondiente a su tema de exposición.

#### Experimento A - Decoding

Pregunta:

> ¿Cómo cambia la distribución y la diversidad de generación cuando se modifica únicamente la política de decoding?.

Configuración fija:

```text
modelo
prompt
max_new_tokens
número de repeticiones
seed inicial documentada
```

Baseline:

```text
sampling
temperature = 1.0
top_k = desactivado
top_p = 1.0
```

Variantes:

```text
A1
temperature = 0.7

A2
temperature = 1.3

A3
top_k = 3

A4
top_p = 0.85
```

No se deben cambiar simultáneamente las tres variables si se desea atribuir un efecto a una de ellas.

Métricas sugeridas:

- entropía de la distribución inicial,
- entropía media de la trayectoria,
- número de candidatos después del filtrado,
- `distinct-1`,
- `distinct-2`,
- repetición de bigramas,
- proporción de generaciones distintas,
- media y desviación estándar entre repeticiones,
- observación cualitativa breve, separada de las métricas automáticas.

El experimento **no** pretende demostrar calidad general de un modelo.

#### Experimento B - Memoria estimada del KV cache

Pregunta:

> Bajo una configuración fija, ¿cómo cambia la memoria lógica estimada del estado de inferencia al modificar la estrategia de atención/cache?.

Configuración de referencia:

```text
batch = 1
layers = 32
d_model = 4096
query_heads = 32
head_dim = 128
context = 131072
precision = fp16/bf16
bytes_per_value = 2
```

Variantes:

```text
MHA
kv_heads = 32

GQA
kv_heads = 8

SWA
window = 4096
kv_heads = 32

MLA conceptual
latent_rank = 512
```

El laboratorio reporta tanto GB decimal como GiB binario y declara la fórmula usada.

**Advertencia:** Attention AI Lab es un estimador didáctico. Una reducción de memoria lógica estimada no demuestra por sí sola menor latencia real, mayor throughput ni menor memoria pico física de GPU.

#### Exposiciones de refuerzo

Los temas base son:

1. FlashAttention.
2. Multi-Query Attention y Grouped-Query Attention.
3. Multi-Head Latent Attention.
4. Sliding Window Attention y contexto largo.

Si existen más grupos se pueden utilizar:

5. PagedAttention.
6. Speculative Decoding.

Cada exposición debe partir de una fuente primaria y usar **dos herramientas con funciones distintas**.

Por ejemplo:

```text
descubrimiento/síntesis
Elicit/SciSpace/Consensus

exploración de red
ResearchRabbit/Connected Papers

contraste de citas
Scite
```

No es obligatorio utilizar todas las herramientas.

La salida de una herramienta de IA no se considera evidencia primaria.

Consulta [`Exposiciones2-CC-0F4.md`](Exposiciones2-CC-0F4.md).

#### Estándar experimental

Todo experimento debe poder expresarse como:

```text
pregunta -> hipótesis -> baseline -> una modificación -> métrica -> resultado -> error o limitación -> conclusión
```

Para inferencia se añade una distinción obligatoria:

```text
modelo != política de decoding != runtime != hardware
```

#### Entorno

Semana 2 **no crea ni modifica el entorno del curso**.

CC-0F4 utiliza un único entorno reproducible definido en la raíz mediante:

```text
requirements.txt
Makefile
Dockerfile
ENTORNO.md
```

El cuaderno canónico tiene una parte autocontenida y una extensión opcional con `distilgpt2`. Si el modelo no está disponible en cache local, esa extensión puede omitirse sin afectar el desarrollo conceptual de la semana.

Desde la raíz:

```bash
make check-semana2
make execute-cuaderno2
```

Consulta [`../ENTORNO.md`](../ENTORNO.md).

#### Criterio de cierre de Semana 2

La semana está cerrada cuando el estudiante puede explicar y defender:

$$
z_t \longrightarrow p_t =
\mathrm{softmax}(z_t)
\longrightarrow
\hat{x}_{t+1}
\longrightarrow
x_{1:t+1}
$$

y además justificar:

$$
M_{\mathrm{KV}} =
B L T \, 2 H_{\mathrm{KV}} d_h b,
$$

indicando qué representa cada término y bajo qué supuestos la expresión es válida.

La evidencia mínima de cierre es:

```text
decoding implementado + Experimento A + estimación de KV cache + Experimento B + exposición de refuerzo
```
