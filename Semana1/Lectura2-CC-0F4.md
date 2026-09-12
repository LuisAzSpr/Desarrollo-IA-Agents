### Attention Is All You Need

#### Lectura crítica para CC-0F4

Referencia: Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). *Attention Is All You Need*. Advances in Neural Information Processing Systems, 30.

Fuente primaria: https://arxiv.org/abs/1706.03762

Versión de arXiv consultada para esta lectura: v7.

En esta lectura se utiliza español cuando existe una traducción técnica natural, pero se conservan términos como `query`, `key`, `value`, `embedding`, `head`, `softmax`, `dropout` y `LayerNorm` cuando su denominación forma parte de la literatura o del código.

#### 1. De la recurrencia a una arquitectura basada en atención

Cuando *Attention Is All You Need* apareció en 2017, los sistemas más competitivos para transducción de secuencias se apoyaban principalmente en arquitecturas recurrentes o convolucionales. En una red recurrente, el estado de una posición depende del estado anterior,

$$
h_t=f(h_{t-1},x_t),
$$

de modo que el procesamiento de una secuencia introduce una cadena de dependencias temporales. Esta estructura resulta natural para modelar secuencias, pero limita el paralelismo dentro de un ejemplo y hace que la información entre posiciones distantes tenga que atravesar múltiples operaciones.

Las redes convolucionales reducen parte de esa dependencia secuencial y permiten mayor paralelismo, aunque las posiciones alejadas continúan comunicándose a través de varias capas o mediante kernels de mayor tamaño.

Vaswani et al. parten de una pregunta arquitectónica más radical: ¿es realmente necesario que recurrencia o convolución constituyan el mecanismo principal para relacionar las posiciones de una secuencia?

La respuesta propuesta es el Transformer.

La contribución no consiste simplemente en introducir mecanismos de atención. La atención ya existía y había sido utilizada en modelos encoder-decoder anteriores. El cambio fundamental consiste en convertirla en el mecanismo estructural principal para establecer interacciones entre posiciones.

Esta distinción es importante porque permite entender el paper en su contexto histórico. El Transformer no debe estudiarse como una colección de componentes que posteriormente se hicieron populares, sino como una reorganización de la arquitectura para procesamiento de secuencias.

El modelo presentado en 2017 es un Transformer encoder-decoder. El encoder transforma una secuencia de entrada

$$
(x_1,\ldots,x_n)
$$

en una secuencia de representaciones

$$
(z_1,\ldots,z_n),
$$

mientras que el decoder genera la secuencia de salida de manera autoregresiva,

$$
P(y_1,\ldots,y_m\mid x) =
\prod_{t=1}^{m} P(y_t\mid y_1,\ldots,y_{t-1},x).
$$

Esta arquitectura original no debe confundirse con los modelos decoder-only que dominan buena parte de los LLM generativos actuales. El Transformer de 2017 constituye el fundamento de una familia arquitectónica que posteriormente evolucionó en distintas direcciones.

El modelo base del paper utiliza seis capas en el encoder y seis en el decoder, con una dimensión de representación

$$
d_{\mathrm{model}}=512.
$$

Cada capa combina mecanismos de atención con transformaciones feed-forward, conexiones residuales y normalización. Para comprender por qué esta organización funciona, primero es necesario entender qué operación realiza la atención.

#### 2. Atención como mecanismo de interacción entre posiciones

La pregunta fundamental es cómo puede una posición incorporar información procedente de otras posiciones de la secuencia.

El Transformer construye tres proyecciones aprendidas de las representaciones de entrada:

$$
Q=XW_Q,
\qquad
K=XW_K,
\qquad
V=XW_V.
$$

Estas matrices se denominan `query`, `key` y `value`. Los nombres son útiles, pero no deben interpretarse literalmente como preguntas, claves o valores en lenguaje natural. Se trata de representaciones vectoriales aprendidas.

Una `query` expresa la representación desde la cual una posición busca información. Las `keys` proporcionan las representaciones contra las cuales se calcula compatibilidad y los `values` contienen la información que finalmente será combinada.

El producto

$$
QK^\top
$$

compara cada query con todas las keys disponibles. Si

$$
Q\in\mathbb{R}^{T_q\times d_k}
$$

y

$$
K\in\mathbb{R}^{T_k\times d_k},
$$

entonces

$$
QK^\top\in\mathbb{R}^{T_q\times T_k}.
$$

Cada fila representa una query y cada columna una key. En autoatención, queries, keys y values proceden de la misma secuencia y, por tanto,

$$
T_q=T_k=T.
$$

La matriz de compatibilidades tiene entonces dimensión

$$
T\times T.
$$

Esta interacción directa entre todas las posiciones es una de las propiedades centrales de la autoatención, pero también anticipa una de sus principales limitaciones: en atención densa, el número de interacciones crece cuadráticamente con la longitud de la secuencia.

El Transformer no utiliza directamente los productos punto. La operación completa es

$$
\mathrm{Attention}(Q,K,V) =
\mathrm{softmax}
\left(
\frac{QK^\top}{\sqrt{d_k}}
\right)V.
$$

La división por

$$
\sqrt{d_k}
$$

cumple una función específica. Si las componentes de una query y una key tienen aproximadamente media cero y varianza uno, la varianza del producto punto

$$
q\cdot k =
\sum_{i=1}^{d_k}q_i k_i
$$

crece aproximadamente con $d_k$. Escalar el producto por $1/\sqrt{d_k}$ ayuda a controlar la magnitud de los logits antes de aplicar `softmax`.

El factor de escala no introduce causalidad ni determina qué posiciones pueden observarse. Su función consiste en controlar la escala numérica de las compatibilidades.

Después del escalamiento, `softmax` normaliza cada fila y produce pesos de atención. Si

$$
A=
\mathrm{softmax}
\left(
\frac{QK^\top}{\sqrt{d_k}}
\right),
$$

entonces, para cada query,

$$
\sum_j A_{ij}=1.
$$

Finalmente,

$$
O=AV
$$

combina los values utilizando esos pesos.

La ecuación es compacta, pero expresa una modificación arquitectónica importante. Una representación deja de depender necesariamente de una cadena de estados intermedios y puede construirse utilizando directamente información de otras posiciones.

Sin embargo, permitir esta interacción global plantea una nueva cuestión: en un modelo autoregresivo, ¿cómo impedir que una posición utilice información procedente del futuro?

#### 3. Causalidad y generación autoregresiva

En el decoder, la posición $i$ solo puede depender de posiciones anteriores o de sí misma. Una posición futura $j>i$ no puede participar en el cálculo porque, durante generación, ese token todavía no existe.

El Transformer impone esta restricción mediante una máscara causal:

$$
\mathrm{Attention}_{\mathrm{causal}}(Q,K,V) =
\mathrm{softmax}
\left(
\frac{QK^\top}{\sqrt{d_k}}+M
\right)V,
$$

donde

$$
M_{ij} =
\begin{cases}
0, & j\le i,\\
-\infty, & j>i.
\end{cases}
$$

Al aplicar la máscara antes de `softmax`, las posiciones futuras reciben probabilidad aproximadamente nula:

$$
A_{ij}\approx 0
\qquad
\text{para }j>i.
$$

La causalidad, por tanto, no procede de `softmax` ni del factor $1/\sqrt{d_k}$. Procede de restringir explícitamente qué posiciones pueden participar en la atención.

Esta distinción permite resolver una aparente contradicción del Transformer. Durante entrenamiento, toda la secuencia objetivo es conocida y las posiciones pueden procesarse simultáneamente. Sin embargo, el modelo continúa siendo autoregresivo porque la máscara impide que la representación correspondiente a una posición utilice tokens posteriores.

En otras palabras, paralelismo computacional no significa acceso al futuro.

La situación cambia durante inferencia. Allí los tokens futuros todavía no existen. El modelo calcula una distribución para el siguiente token, selecciona un token según la política de decoding, incorpora ese token al contexto y repite la operación.

Por tanto, eliminar recurrencia del bloque Transformer no elimina la secuencialidad de la generación autoregresiva. El entrenamiento puede explotar paralelismo entre posiciones conocidas; la generación continúa produciendo tokens uno después de otro.

Esta distinción será importante más adelante en el curso, cuando se estudien logits, políticas de decoding, ventana de contexto y KV cache.

#### 4. De una operación de atención a un bloque Transformer

Una sola operación de atención todavía no constituye un Transformer.

El modelo utiliza Multi-Head Attention, que aplica varias operaciones de atención con proyecciones aprendidas diferentes:

$$
\mathrm{head}_i =
\mathrm{Attention}
\left(
QW_i^Q,
KW_i^K,
VW_i^V
\right).
$$

Las salidas de las distintas heads se concatenan y vuelven a proyectarse:

$$
\mathrm{MultiHead}(Q,K,V) =
\mathrm{Concat}
\left(
\mathrm{head}_1,\ldots,\mathrm{head}_h
\right)W^O.
$$

En el modelo base,

$$
h=8,
$$

y

$$
d_k=d_v=64,
$$

porque

$$
\frac{d_{\mathrm{model}}}{h} =\frac{512}{8} =
64.
$$

El uso de múltiples heads permite proyectar las representaciones en distintos subespacios y aprender diferentes patrones de interacción. No obstante, esto no implica que cada head posea necesariamente una función lingüística única, estable o fácilmente interpretable.

En la arquitectura encoder-decoder original aparecen tres formas distintas de atención.

El encoder utiliza autoatención completa: queries, keys y values proceden de las representaciones del encoder y todas las posiciones de entrada pueden interactuar entre sí.

El decoder utiliza autoatención causal: queries, keys y values proceden del decoder, pero la máscara impide observar posiciones futuras.

Finalmente, el decoder utiliza atención cruzada sobre las representaciones producidas por el encoder. En ese caso,

$$
Q=H_DW_Q,
\qquad
K=H_EW_K,
\qquad
V=H_EW_V,
$$

donde $H_D$ representa estados del decoder y $H_E$ estados del encoder. De esta manera, el decoder puede consultar información de toda la secuencia fuente mientras genera la salida.

Después de la atención, cada posición atraviesa una red feed-forward:

$$
\mathrm{FFN}(x) =
\max(0,xW_1+b_1)W_2+b_2.
$$

En el paper,

$$
d_{\mathrm{model}}=512
$$

y

$$
d_{\mathrm{ff}}=2048.
$$

Atención y FFN cumplen funciones diferentes. La atención permite intercambiar información entre posiciones; la red feed-forward transforma las características de cada posición de manera independiente.

Las subcapas se combinan con conexiones residuales y normalización. El Transformer original utiliza

$$
\mathrm{LayerNorm}
\left(
x+\mathrm{Sublayer}(x)
\right),
$$

es decir, una arquitectura que hoy suele denominarse post-norm.

Esta observación es relevante para CC-0F4 porque el cuaderno de Semana 1 utiliza una variante pre-norm:

$$
Y=
X+
\mathrm{MHA}
\left(
\mathrm{LN}(X)
\right),
$$

$$
Z=
Y+
\mathrm{FFN}
\left(
\mathrm{LN}(Y)
\right).
$$

Ambas pertenecen a la familia Transformer, pero no son la misma arquitectura. Leer código moderno y asumir que reproduce exactamente el modelo de 2017 puede llevar a conclusiones equivocadas.

El modelo original también utiliza `dropout` con probabilidad

$$
P_{\mathrm{drop}}=0.1.
$$

#### 5. El problema del orden

Si la atención permite relacionar directamente todas las posiciones, aparece un problema adicional: la operación por sí sola no contiene información suficiente sobre el orden de la secuencia.

El paper incorpora codificaciones posicionales sinusoidales:

$$
PE(pos,2i)=
\sin
\left(
\frac{pos}
{10000^{2i/d_{\mathrm{model}}}}
\right),
$$

$$
PE(pos,2i+1)=
\cos
\left(
\frac{pos}
{10000^{2i/d_{\mathrm{model}}}}
\right).
$$

La representación de entrada resulta de sumar embedding de token y representación posicional:

$$
X_{\mathrm{entrada}}=
E_{\mathrm{token}}+PE.
$$

El paper también compara esta estrategia con embeddings posicionales aprendidos y obtiene resultados similares.

La relevancia de este resultado no consiste en demostrar que las codificaciones sinusoidales sean universalmente superiores. De hecho, buena parte de los modelos posteriores utiliza otros mecanismos de posición.

Lo importante es que la eliminación de recurrencia y convolución obliga a introducir explícitamente información sobre el orden.

Este aspecto ilustra una idea general de diseño arquitectónico: retirar un mecanismo puede eliminar también propiedades que ese mecanismo proporcionaba implícitamente y que deben recuperarse de otra forma.

#### 6. ¿Por qué autoatención?

Una de las argumentaciones centrales del paper compara autoatención, recurrencia y convolución en tres dimensiones: complejidad computacional, cantidad de operaciones necesariamente secuenciales y longitud máxima del camino que conecta dos posiciones.

Para una secuencia de longitud $n$ y representación de dimensión $d$, la autoatención densa tiene complejidad aproximada

$$
O(n^2d),
$$

pero puede calcular sus posiciones en paralelo y conecta directamente cualquier par de posiciones.

Una capa recurrente presenta una complejidad aproximada

$$
O(nd^2),
$$

requiere $O(n)$ operaciones secuenciales y establece caminos más largos entre posiciones distantes.

Las capas convolucionales permiten paralelismo, pero necesitan varias capas para conectar posiciones alejadas cuando el kernel tiene tamaño limitado.

Esta comparación explica buena parte del atractivo inicial de la arquitectura: la autoatención reduce drásticamente la longitud del camino por el cual puede propagarse información y ofrece un alto grado de paralelismo durante entrenamiento.

Sin embargo, sería incorrecto concluir que la atención es siempre computacionalmente más barata.

La atención densa conserva una dependencia cuadrática respecto de la longitud de secuencia:

$$
O(n^2d).
$$

Esta limitación se convertiría posteriormente en una de las principales líneas de investigación sobre atención eficiente, ventanas locales, kernels especializados y diferentes estrategias de reducción de memoria y cómputo.

El paper de 2017 debe leerse, por tanto, como evidencia de una nueva relación entre paralelismo, conectividad y costo, no como demostración de que la atención sea universalmente más eficiente.

#### 7. Entrenamiento y evidencia experimental

Una arquitectura no puede evaluarse únicamente por la elegancia de sus ecuaciones. La pregunta relevante es qué evidencia experimental presentó el paper para sostener sus afirmaciones.

Para WMT 2014 English-German se utilizan aproximadamente 4.5 millones de pares de oraciones y un vocabulario basado en unas 37 000 unidades BPE.

Los experimentos fueron ejecutados utilizando ocho GPU NVIDIA P100.

El modelo base fue entrenado durante 100 000 pasos, aproximadamente 12 horas, mientras que el modelo grande fue entrenado durante 300 000 pasos, aproximadamente 3.5 días.

El optimizador utilizado es Adam, con

$$
\beta_1=0.9,
\qquad
\beta_2=0.98,
\qquad
\epsilon=10^{-9}.
$$

El learning rate sigue la expresión

$$\mathrm{lrate}=
d_{\mathrm{model}}^{-1/2}
\min
\left(
\mathrm{step}^{-1/2},
\mathrm{step}\cdot
\mathrm{warmup}^{-3/2}
\right),
$$

con

$$
\mathrm{warmup}=4000.
$$

El modelo base utiliza además `dropout`

$$
P_{\mathrm{drop}}=0.1
$$

y label smoothing

$$
\epsilon_{\mathrm{ls}}=0.1.
$$

Durante inferencia, los resultados reportados emplean beam search con beam size 4 y una penalización de longitud

$$
\alpha=0.6.
$$

Estos detalles son importantes porque recuerdan que el resultado experimental no depende exclusivamente de la arquitectura. El rendimiento observado surge de la interacción entre modelo, datos, entrenamiento, regularización, selección del checkpoint y política de decoding.

Un Transformer grande alcanza

$$
28.4\ \mathrm{BLEU}
$$

en English-German.

La versión v7 de arXiv reporta en el abstract y en la tabla principal

$$
41.8\ \mathrm{BLEU}.
$$

para English-French. Esta cifra requiere una precisión adicional que se discute más adelante, porque la oración correspondiente de la sección de resultados conserva el valor 41.0 de versiones anteriores del manuscrito.

El paper también evalúa la arquitectura en constituency parsing, proporcionando evidencia adicional de que el enfoque podía transferirse a una tarea distinta de traducción.

Estos resultados contribuyeron a demostrar que una arquitectura basada principalmente en atención podía competir con sistemas recurrentes y convolucionales de alto rendimiento y, al mismo tiempo, aprovechar mejor el paralelismo disponible durante entrenamiento.

Sin embargo, los resultados agregados no responden por sí solos a la pregunta de por qué funciona cada componente. Para eso son especialmente importantes las ablaciones.

#### 8. Qué enseñan las ablaciones

El modelo base utiliza seis capas, $d_{\mathrm{model}}=512$, $d_{\mathrm{ff}}=2048$, ocho heads, $d_k=d_v=64$, `dropout` 0.1, label smoothing 0.1 y aproximadamente 65 millones de parámetros.

El paper modifica distintas decisiones arquitectónicas y observa cómo cambia el rendimiento.

Una de las comparaciones estudia el número de heads. Con una sola head se reporta una perplexity de 5.29 y BLEU de 24.9. Con cuatro heads, BLEU aumenta a 25.5. Con ocho y dieciséis heads se obtiene 25.8, mientras que con treinta y dos heads el resultado desciende a 25.4.

Esta evidencia permite afirmar que el número de heads y la dimensión asignada a cada una influyen en el comportamiento del modelo bajo la configuración experimental estudiada.

No permite afirmar que más heads produzcan siempre mejores modelos.

Este punto es metodológicamente importante para CC-0F4. Una tendencia observada dentro de algunas configuraciones no constituye una ley general y una ablación solo permite atribuir conclusiones dentro de las condiciones realmente comparadas.

Lo mismo ocurre con muchas decisiones que posteriormente se asociaron al Transformer. El paper muestra que funcionaron en sus experimentos; no demuestra que sean las únicas elecciones posibles ni que continúen siendo óptimas al cambiar escala, datos, tarea o régimen de entrenamiento.

#### 9. Una lectura crítica de los resultados

Incluso una fuente primaria debe leerse críticamente y, cuando existen varias revisiones de un manuscrito, también es necesario identificar qué versión se está consultando.

Esta lectura utiliza la versión v7 de arXiv. En esa versión existe una inconsistencia en el resultado de English-French: el abstract y la tabla principal reportan 41.8 BLEU, mientras que una oración de la sección 6.1 mantiene 41.0 BLEU.

La discrepancia no estuvo presente durante toda la historia del artículo. La versión publicada en NeurIPS y las primeras versiones de arXiv, de v1 a v4, utilizaban 41.0 de manera consistente en el abstract y en el cuerpo. En revisiones posteriores se actualizó el valor del abstract a 41.8, coherente con la tabla principal, pero la oración de la sección de resultados conservó 41.0.

Por esta razón, cuando esta lectura se refiere al resultado mostrado por la tabla principal de la versión v7 utiliza 41.8 BLEU. La observación no pretende resolver editorialmente la discrepancia, sino dejar explícita la versión consultada y evitar presentar como universal un valor que depende de la revisión del manuscrito que se examine.

El detalle es pequeño, pero la lección metodológica es importante: trabajar con una fuente primaria no significa aceptar automáticamente cada oración de esa fuente. Los datos, tablas, metodología y afirmaciones deben contrastarse entre sí, y en trabajos con varias revisiones también puede ser necesario comprobar el historial de versiones.

La lectura crítica exige además separar lo que el paper demuestra de afirmaciones que resultan tentadoras pero no están sustentadas por sus experimentos.

El trabajo aporta evidencia de que una arquitectura basada principalmente en atención puede sustituir recurrencia y convolución en las tareas estudiadas, reducir la cantidad de operaciones necesariamente secuenciales durante entrenamiento y alcanzar resultados competitivos.

No demuestra que la atención densa sea siempre la alternativa más eficiente. No demuestra que ocho heads sean universalmente óptimas ni que incrementar el número de heads mejore necesariamente el rendimiento. Tampoco demuestra que cada head tenga una interpretación lingüística causal única y estable.

El paper no establece que todo Transformer deba ser encoder-decoder, que post-norm sea obligatorio o que las codificaciones posicionales sinusoidales sean la única forma apropiada de representar posición.

Finalmente, una matriz de atención tampoco debe identificarse automáticamente con una explicación completa del razonamiento interno de un modelo.

Estas restricciones no reducen la importancia del trabajo. Al contrario, permiten delimitar con precisión cuál fue su contribución.

#### 10. Del Transformer de 2017 a los modelos actuales

El Transformer contemporáneo no es una reproducción exacta de la arquitectura publicada en 2017.

Muchas familias modernas utilizan pre-norm en lugar del post-norm original. `LayerNorm` convive con variantes como RMSNorm. La codificación sinusoidal absoluta ha sido sustituida en numerosos modelos por mecanismos como RoPE u otras representaciones de posición.

Multi-Head Attention continúa siendo un mecanismo fundamental, pero comparte espacio con Multi-Query Attention, Grouped-Query Attention y otras variantes destinadas, entre otras cosas, a modificar los costos de inferencia y del KV cache.

Las redes feed-forward con ReLU del Transformer original han evolucionado hacia activaciones y estructuras como GELU o SwiGLU en numerosas familias de modelos.

La arquitectura encoder-decoder sigue siendo importante, pero los modelos decoder-only adquirieron un papel dominante en gran parte de los LLM generativos.

Asimismo, la atención estándar ha dado lugar a implementaciones altamente optimizadas como FlashAttention.

Por ello, *Attention Is All You Need* no debe estudiarse como la especificación de un LLM moderno. Debe estudiarse como el fundamento arquitectónico a partir del cual se desarrolló buena parte de esa evolución.

Esa perspectiva también ayuda a evitar un error frecuente: leer retrospectivamente el paper como si sus autores hubieran diseñado directamente los sistemas actuales. El trabajo resolvía problemas concretos de su momento y proporcionó un mecanismo arquitectónico que posteriormente fue escalado, modificado y combinado con numerosos avances adicionales.

#### 11. Por qué sigue siendo un paper fundamental

La importancia de *Attention Is All You Need* no reside únicamente en una ecuación.

La operación

$$
\mathrm{softmax}
\left(
\frac{QK^\top}{\sqrt{d_k}}
\right)V
$$

es central, pero el impacto del trabajo proviene de una decisión arquitectónica más amplia: reorganizar el procesamiento de secuencias alrededor de interacciones directas entre posiciones y mostrar que esa estrategia podía reemplazar a recurrencia y convolución como mecanismos estructurales principales en las tareas estudiadas.

Esta decisión altera simultáneamente el paralelismo, la longitud del camino de información y la forma de construir representaciones contextuales.

También introduce nuevos costos y problemas. La atención densa escala cuadráticamente con la longitud de secuencia; la ausencia de recurrencia obliga a representar explícitamente el orden; la generación autoregresiva continúa siendo secuencial durante inferencia; y muchas elecciones concretas del modelo original fueron posteriormente modificadas.

Esa combinación de contribución y limitaciones explica por qué el paper continúa siendo relevante.

Para CC-0F4, comprenderlo no significa memorizar sus hiperparámetros ni reproducir mecánicamente una implementación. Significa poder relacionar una afirmación arquitectónica con su formulación matemática, reconocer cómo esa formulación se materializa en tensores y código, identificar qué evidencia experimental respalda las conclusiones y distinguir esas conclusiones de afirmaciones que los experimentos no permiten sostener.

Leído de esta manera, *Attention Is All You Need* no es simplemente el paper que introdujo el Transformer. Es un ejemplo de cómo una decisión arquitectónica puede formularse, implementarse, compararse experimentalmente y, finalmente, convertirse en el punto de partida de una nueva familia de sistemas.


