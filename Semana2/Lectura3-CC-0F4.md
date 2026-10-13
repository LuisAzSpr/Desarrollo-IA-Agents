### Lectura 2 - De logits a generación autoregresiva y KV cache

#### Propósito

En la Semana 1 vimos cómo un Transformer causal construye representaciones mediante self-attention y una máscara que impide observar posiciones futuras. Esa arquitectura explica cómo se procesa el contexto, pero no cómo se convierte en texto.

La Semana 2 sigue esa cadena hasta el final:

$$
\text{representación contextual}
\longrightarrow
\text{logits}
\longrightarrow
\mathrm{softmax}
\longrightarrow
\text{política de decoding}
\longrightarrow
\text{siguiente token}
\longrightarrow
\text{contexto ampliado}
\longrightarrow
\text{nueva predicción}
$$

Este ciclo es la generación autoregresiva. A medida que la secuencia crece aparece un problema computacional: recomputar todo el prefijo en cada paso repetiría cálculos ya hechos. El KV cache reutiliza ese estado, a cambio de un costo creciente de memoria.

La pregunta central: ¿qué parte del comportamiento de un modelo generativo pertenece al modelo, qué parte a la política de decoding y qué parte al sistema de inferencia?.

#### 1. Los logits todavía no son probabilidades

Consideremos un modelo autoregresivo con vocabulario de tamaño $V$. Tras procesar un contexto $x_1,...,x_t$, el modelo produce un vector $z \in R^{V}$ cuyos componentes se llaman logits. Un logit no es directamente una probabilidad: puede ser positivo, negativo o mayor que uno, y lo que importa es su valor relativo, no su valor absoluto.

Para convertirlos en una distribución de probabilidad aplicamos softmax:

$$
p_i =
\frac{\exp(z_i)}
{\sum_{j=1}^{V}\exp(z_j)}.
$$

El resultado cumple

$$
p_i \ge 0,
\qquad
\sum_i p_i = 1,
$$

y se interpreta como

$$
p_i =
P(x_{t+1}=i \mid x_1,\ldots,x_t).
$$

Conviene retener dos distinciones: logits y probabilidades no son lo mismo, y la distribución del modelo tampoco es el token finalmente elegido. El modelo entrega una distribución; otra decisión, separada, determina cómo elegir a partir de ella.

#### 2. El decoding es una política sobre la distribución del modelo

Si siempre elegimos el token con mayor probabilidad,

$$
x_{t+1}=\arg\max_i p_i,
$$

usamos greedy decoding. Es determinista, pero que una decisión sea localmente la más probable no garantiza que la secuencia completa sea la mejor posible, y en generación abierta tiende a producir texto repetitivo.

La alternativa es el sampling: se muestrea de la distribución,

$$
x_{t+1}\sim P(\cdot \mid x_{\le t}),
$$

y dos ejecuciones del mismo modelo pueden entonces producir continuaciones distintas.

Este punto es central: el modelo y la política de decoding son cosas distintas. Podemos mantener los mismos pesos y modificar solo la estrategia de selección. Holtzman et al. muestran justamente esto: la política de decoding puede alterar de forma sustancial el comportamiento observado de un mismo modelo, y motivan el nucleus sampling que veremos a través de top-p.

Greedy y sampling no agotan el espacio de políticas de decoding; beam search, contrastive search y las penalizaciones de repetición son otras estrategias con el mismo estatus.

#### 3. La temperatura modifica la forma de la distribución

Antes de aplicar softmax podemos escalar los logits con una temperatura $T$:

$$
p_i(T)=
\frac{\exp(z_i/T)}
{\sum_j \exp(z_j/T)}.
$$

Con $T < 1$, las diferencias entre logits se amplifican y la distribución se concentra; con $T > 1$, se reducen y la distribución se aplana.  En resumen: temperatura baja concentra, temperatura alta dispersa.

La temperatura no añade conocimiento nuevo al modelo ni mejora automáticamente la calidad de una respuesta. Una temperatura mayor aumenta diversidad y también la  probabilidad de elegir tokens poco adecuados; una menor da estabilidad y también favorece la repetición. 
Por eso una conclusión razonable sería: "bajo este modelo, prompt y configuración, subir la temperatura incrementó la diversidad medida", y no "una temperatura alta produce mejores respuestas", que excede lo que la evidencia permite afirmar.

#### 4. Top-k limita el número de candidatos

Top-k conserva únicamente los $k$ tokens con mayor score y descarta el resto; sus probabilidades se renormalizan antes de samplear:

$$
\text{distribución completa}
\longrightarrow
\text{ordenar candidatos}
\longrightarrow
\text{conservar los } k \text{ mejores}
\longrightarrow
\text{renormalizar}
\longrightarrow
\text{samplear}
$$

El problema de fondo es que un valor fijo de $k$ no toma en cuenta la forma real de la distribución: en una posición puede existir un candidato dominante, en otra veinte alternativas igual de plausibles, y usar siempre el mismo número de candidatos trata ambos casos igual.

#### 5. Top-p adapta el conjunto de candidatos a la distribución

Top-p, o nucleus sampling, ordena los tokens por probabilidad,

$$
p_1 \ge p_2 \ge \cdots \ge p_V,
$$

y selecciona el conjunto mínimo cuya probabilidad acumulada alcance un umbral $p$:

$$
\sum_{i=1}^{m} p_i \ge p.
$$

Si $top\_p = 0.9$, el tamaño de ese conjunto cambia en cada paso: pocos tokens bastan cuando la distribución está concentrada, y muchos más cuando está dispersa. La diferencia con top-k es clara: top-k fija el número máximo de candidatos, mientras que top-p lo adapta a la distribución en cada paso.

Holtzman et al. proponen nucleus sampling como respuesta al comportamiento degenerativo observado con otras estrategias, sin que esto convierta a $top\_p = 0.9$ en un valor universalmente óptimo. Su conveniencia depende de la tarea, del modelo y del comportamiento buscado, igual que ocurre con la temperatura.

#### 6. La generación autoregresiva es un ciclo

Una vez elegido el siguiente token, este se incorpora al contexto:

$$ [x_1,\ldots,x_t]
\longrightarrow
\text{modelo}
\longrightarrow
P(x_{t+1}\mid x_1,\ldots,x_t)
\longrightarrow
\text{decoding}
\longrightarrow
x_{t+1}.
$$

En el siguiente paso:

$$
[x_1,\ldots,x_t,x_{t+1}]
\longrightarrow
\text{modelo}
\longrightarrow
P(x_{t+2}\mid x_1,\ldots,x_t,x_{t+1}).
$$

La secuencia completa se factoriza como

$$
P(x_1,\ldots,x_T) =
\prod_{t=1}^{T}
P(x_t \mid x_1,\ldots,x_{t-1}).
$$

Eliminar la recurrencia de la arquitectura Transformer no elimina esta dependencia secuencial. En entrenamiento, muchas posiciones se evalúan en paralelo gracias a la máscara causal, porque ya tenemos toda la secuencia objetivo; en inferencia esto no es posible, porque el token $x\_t$ es necesario para producir $x_{t+1}$.

#### 7. El problema de recomputar el pasado

Supongamos que ya procesamos $A,B,C,D$ y queremos producir el siguiente token. Tras elegir $E$, el contexto pasa a ser $A,B,C,D,E$. Una implementación ingenua volvería a calcular las keys y values de $A,B,C,D$ desde cero, aunque no hayan cambiado, repitiendo ese trabajo en cada iteración.

En un Transformer causal, las keys y values de los tokens anteriores no cambian por la aparición de un nuevo token. Esa propiedad permite almacenarlas y reutilizarlas durante la inferencia. La documentación de Transformers describe justamente el KV cache como el mecanismo que conserva estas representaciones por capa para evitar recalcularlas en cada paso.

#### 8. Qué almacena el KV cache

Cada capa mantiene $K_{\text{past}}$ y $V_{\text{past}}$. Cuando aparece un nuevo token, solo se calculan $q_t$, $k_t$ y $v_t$ para ese token, y el cache se actualiza así:

$$
K_{\text{cache}}
\leftarrow
[K_{\text{past}};k_t],
\qquad
V_{\text{cache}}
\leftarrow
[V_{\text{past}};v_t].
$$

La atención del nuevo token usa entonces

$$
\mathrm{Attention}
\left(
q_t,
K_{\text{cache}},
V_{\text{cache}}
\right).
$$

La idea que hay que retener no es memorizar una API, sino entender el intercambio de fondo: menos recomputación a cambio de más estado almacenado. El KV cache acelera la generación evitando recalcular las K/V históricas, pero su tamaño crece con la cantidad de tokens conservados.

#### 9. El KV cache también cuesta memoria

Una aproximación útil para atención multi-head convencional es

$$
M_{\text{KV}}
\approx
B
\times
L
\times
T
\times
H_{\text{KV}}
\times
D_h
\times
2
\times
S,
$$

donde $B$ es el batch, $L$ el número de capas, $T$ la longitud almacenada, $H_{\text{KV}}$ el número de heads de keys/values, $D_h$ la dimensión por head, el factor $2$ corresponde a almacenar K y V, y $S$ representa los bytes por elemento; por ejemplo, **fp16** y **bf16** usan dos bytes.

Más contexto, más capas o más KV heads significan más memoria de cache.

No hay que confundir esta estimación lógica con la memoria física total de una GPU, que además incluye pesos del modelo, activaciones temporales, buffers y overhead del allocator.

Como ampliación, existen técnicas como la cuantización del KV cache y PagedAttention para gestionar mejor este costo. No forman parte del núcleo experimental de esta semana, pero conviene saber que existen.

#### 10. MHA, GQA y MQA cambian el costo del cache

En Multi-Head Attention (MHA), cada query head tiene su propia key head y value head. Por ejemplo, con $query\_{heads} = 32$ y $kv\_{heads} = 32$, el cache almacena K y V para las $32$ heads.

Grouped-Query Attention (GQA) mantiene muchas query heads, pero usa menos key/value heads compartidas entre grupos. Con $query\_{heads} = 32$ y $kv\_{heads} = 8$, se reduce aproximadamente por un factor de cuatro la parte del cache que depende del número de KV heads.

Multi-Query Attention (MQA) lleva ese compartimiento al extremo, usando una única head de keys y values. Reduce todavía más el estado almacenado, aunque puede introducir trade-offs de capacidad o calidad que dependen de la arquitectura y del entrenamiento.

Menos KV heads significa menor estado almacenado, pero no implica necesariamente una latencia proporcionalmente menor: eso depende también de los kernels, el hardware, el ancho de banda de memoria y el tamaño de batch. Estimación analítica y benchmark físico son cosas distintas.

#### 11. Contexto largo no significa memoria gratuita

El tamaño de la ventana de contexto define cuánto historial puede considerar una arquitectura, pero contextos más largos tienen consecuencias computacionales: un cache dinámico convencional crece junto con la secuencia. Algunas arquitecturas usan sliding window attention, que mantiene solo una ventana local en ciertas capas, de modo que el cache de esas capas deja de crecer al alcanzar ese tamaño; Transformers contempla explícitamente este comportamiento en sus estrategias de cache.

Por eso conviene separar tres ideas: ventana de contexto no equivale a información realmente útil, no equivale a KV cache gratuito y no equivale a mejor respuesta automática.

#### 12. Qué observar en el laboratorio

Los experimentos de la Semana 2 estudian dos preguntas distintas.

**Decoding.** Con el modelo, el prompt y $max_{\mathrm{new\ tokens}}$ fijos, se modifica una sola política ($temperature$, $top\text{-}k$ , $top\text{-}p$) y se observan diversidad, repetición y entropía. El objetivo no es la "mejor configuración universal", sino determinar qué comportamiento cambia al modificar una sola decisión.

**KV cache.** Se mantienen constantes los supuestos del modelo y se modifica la estrategia de atención o cache. La pregunta no es qué arquitectura es mejor, sino cómo cambia el costo lógico de memoria bajo supuestos explícitos.

Esta distinción entre pregunta, variable modificada, métrica y conclusión se usará durante todo el curso.

#### 13. Cierre

La Semana 2 introduce tres separaciones que deben quedar claras: el modelo, la política de decoding y el runtime de inferencia son cosas distintas. El modelo produce logits, softmax los interpreta como una distribución, el decoding decide cómo seleccionar el siguiente token y la autoregresión repite ese proceso paso a paso. El KV cache evita recomputar keys y values del pasado a cambio de memoria, y arquitecturas como GQA y MQA reducen ese estado disminuyendo el número de KV heads.

Por eso, observar una generación rápida, diversa o estable no permite atribuir esa propiedad al modelo sin más. Conviene preguntarse siempre qué produjo el modelo, qué decidió el decoding, qué reutilizó el runtime, qué costo introdujo esa decisión y qué evidencia tenemos para afirmarlo. Esta separación será importante cuando el curso incorpore retrieval, RAG, herramientas y agentes: el comportamiento de un sistema compuesto no debe atribuirse automáticamente a un único componente.

#### Preguntas de lectura

1. ¿Por qué un logit no puede interpretarse directamente como una probabilidad?
2. ¿Qué diferencia existe entre greedy decoding y sampling?
3. ¿Por qué cambiar la temperatura no modifica los pesos del modelo?
4. ¿Qué diferencia conceptual existe entre top-k y top-p?
5. ¿Por qué dos ejecuciones del mismo modelo pueden producir textos distintos?
6. ¿Por qué un Transformer sin recurrencia arquitectónica continúa generando secuencialmente?
7. ¿Qué cálculos reutiliza un KV cache?
8. ¿Por qué el KV cache reduce recomputación pero aumenta consumo de memoria?
9. ¿Por qué GQA y MQA pueden reducir el tamaño del cache respecto de MHA?
10. ¿Por qué una reducción estimada del KV cache no demuestra automáticamente una reducción proporcional de latencia?.

#### Referencias principales

* Holtzman, A., Buys, J., Du, L., Forbes, M., & Choi, Y. *The Curious Case of Neural Text Degeneration*. arXiv:1904.09751.
* Hugging Face Transformers. *Caching / Cache strategies*. Documentación técnica de Transformers.

#### Ampliación opcional

* Kwon, W. et al. *Efficient Memory Management for Large Language Model Serving with PagedAttention*. SOSP 2023.
* Ainslie, J. et al. *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints*. arXiv:2305.13245.
* Hugging Face Transformers. *Generation strategies*. Documentación sobre greedy search, sampling y estrategias de generación.
