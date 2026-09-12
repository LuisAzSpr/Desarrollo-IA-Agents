### Sobre los Transformers


La arquitectura Transformer cambió de forma decisiva el procesamiento de secuencias al sustituir la recurrencia por mecanismos de atención que pueden operar sobre múltiples posiciones en paralelo durante el entrenamiento. Un Transformer recibe representaciones de tokens y necesita incorporar información de orden o posición. En el diseño original, esa información se añade a los embeddings mediante codificación posicional sinusoidal, en arquitecturas posteriores puede incorporarse de otras formas, por ejemplo mediante embeddings aprendidos, sesgos relativos, RoPE o ALiBi. Por tanto, no toda arquitectura Transformer moderna suma necesariamente una codificación posicional a los embeddings.

La **codificación posicional sinusoidal** del Transformer original se define, para posición $i$ y dimensión $k$, como

$$
\text{PE}(i,2k) = \sin\bigl(i/10000^{2k/d}\bigr),\quad
\text{PE}(i,2k+1) = \cos\bigl(i/10000^{2k/d}\bigr),
$$

donde $d$ es la dimensión del embedding. Una alternativa absoluta consiste en aprender un vector por posición. Estas dos estrategias se suman a las representaciones de entrada. En cambio, RoPE modifica Q y K dentro de la atención, y ALiBi añade un sesgo a los logits de atención, ambas ilustran que la información posicional puede inyectarse en lugares distintos del bloque Transformer.

El **mecanismo de atención de producto punto escalado** parte de proyecciones lineales que producen queries ($Q$), keys ($K$) y values ($V$). Los logits de atención se calculan como

$$
\frac{QK^T}{\sqrt{d_k}},
$$

se aplica una máscara cuando corresponde, luego `softmax`, y finalmente los pesos normalizados se multiplican por $V$. En un decodificador causal, la máscara impide que la posición $i$ atienda a posiciones futuras $j>i$.

La **multi-head attention** repite este mecanismo en varios subespacios de representación. Sus salidas se concatenan y se proyectan nuevamente. Los bloques Transformer combinan atención, redes feed-forward, conexiones residuales y normalización. La ubicación exacta de `LayerNorm` depende de la variante: existen diseños post-norm y pre-norm, los LLM modernos suelen emplear variantes pre-norm y, con frecuencia, normalizaciones como RMSNorm.

#### Encoder, decoder y modelos autoregresivos

Un Transformer **encoder-only** utiliza atención bidireccional y es apropiado para tareas de representación, clasificación o etiquetado. BERT es el ejemplo clásico: su preentrenamiento original incluye Masked Language Modeling y Next Sentence Prediction.

Un Transformer **encoder-decoder** codifica una secuencia fuente y genera una secuencia destino. El decodificador utiliza auto-atención causal y cross-attention sobre las representaciones del encoder. Durante el entrenamiento, las posiciones de una secuencia destino conocida pueden procesarse en paralelo gracias a la máscara causal, durante la inferencia autoregresiva, los tokens de salida se generan secuencialmente. Los embeddings de fuente y destino pueden compartirse, pero no es un requisito de la arquitectura.

Un Transformer **decoder-only**, como las familias GPT y Llama, modela la probabilidad del siguiente token condicionada al prefijo. En entrenamiento se utilizan secuencias desplazadas y una máscara causal para predecir simultáneamente los siguientes tokens de todas las posiciones disponibles. En inferencia, la generación es autoregresiva. Las implementaciones modernas no dependen necesariamente de `torch.nn.Transformer`, suelen usar bloques personalizados, kernels de atención optimizados y mecanismos específicos de posición, normalización y cache.

#### Tokenización y preparación de datos

La tokenización convierte texto en unidades discretas y luego en IDs. Para BERT, una forma correcta de cargar su tokenizador en Hugging Face es, por ejemplo, `AutoTokenizer.from_pretrained("bert-base-uncased")`. BERT utiliza WordPiece y tokens especiales como `[CLS]`, `[SEP]`, `[MASK]` y `[PAD]`. SentencePiece corresponde a otras familias de modelos y no debe presentarse como si fuera el tokenizador de BERT original.

#### Eficiencia de entrenamiento

La acumulación de gradientes permite aproximar un batch efectivo mayor sin mantener todas las muestras simultáneamente en memoria. La precisión mixta reduce almacenamiento y ancho de banda mediante formatos de menor precisión, en PyTorch actual suele gestionarse con AMP y escalado de gradientes cuando el formato lo requiere. Para modelos de gran escala se combinan paralelismo de datos, tensor, pipeline y otras estrategias de partición.

AdamW desacopla el weight decay de la actualización basada en gradiente. LAMB fue diseñado para entrenamiento con batches grandes y adapta el tamaño de actualización por capa. Estas técnicas son complementarias a las decisiones arquitectónicas del Transformer.

### Técnicas actuales

#### Posición absoluta, relativa, RoPE y ALiBi

Los **embeddings posicionales aprendidos** asignan un vector entrenable a cada posición. Las **representaciones relativas** modifican la interacción entre posiciones para que la atención dependa explícitamente de distancias o desplazamientos.

**RoPE (Rotary Position Embedding)** rota pares de dimensiones de Q y K según la posición. La propiedad relevante es que el producto interno entre queries y keys rotadas depende naturalmente de la diferencia de posiciones. En un baseline moderno que usa RoPE, no es necesario sumar además una PE sinusoidal absoluta. Una combinación RoPE + PE absoluta puede estudiarse como ablation, pero no debe aparecer accidentalmente como configuración canónica.

**ALiBi (Attention with Linear Biases)** no añade embeddings posicionales a las representaciones de entrada. Introduce una penalización lineal dependiente de la distancia directamente sobre los logits de atención. Las pendientes de las heads siguen una progresión geométrica definida por el algoritmo oficial, para números de heads que no son potencia de dos, el código oficial especifica una construcción adicional. Esto debe distinguirse de aproximaciones didácticas con pendientes arbitrarias.

#### Optimización de atención: FlashAttention, MQA y GQA

La atención densa conserva complejidad computacional cuadrática en la longitud de secuencia. **FlashAttention** calcula atención exacta pero reorganiza el cómputo para reducir tráfico de memoria y evitar materializar la matriz completa de atención en memoria de alto nivel, logrando una huella de memoria mucho menor y mejoras sustanciales de rendimiento en hardware compatible.

**Multi-Query Attention (MQA)** mantiene múltiples query heads pero comparte una sola key head y una sola value head. **Grouped-Query Attention (GQA)** utiliza un número de key/value heads menor que el número de query heads, compartiéndolos por grupos. Estas variantes reducen el tamaño del KV cache y el ancho de banda durante inferencia autoregresiva. En la familia Llama, GQA aparece en configuraciones modernas, no conviene afirmar que todos los modelos de Llama 2 usan exactamente la misma variante de atención.

#### Contexto largo: Longformer, BigBird y Reformer

Longformer emplea atención local por ventana con posiciones de atención global seleccionadas. BigBird combina patrones locales, globales y aleatorios para obtener atención dispersa con mejores propiedades de escalabilidad.

**Reformer debe distinguirse de ambos.** Su contribución central para atención eficiente es **Locality-Sensitive Hashing (LSH) attention**, que agrupa queries/keys similares mediante hashing y aproxima la atención reduciendo la complejidad respecto de la atención densa. Además utiliza capas residuales reversibles para disminuir memoria de activaciones. Por tanto, agrupar Reformer simplemente bajo "ventanas locales + tokens globales" borra una diferencia arquitectónica esencial.

#### Memoria de contexto y Compressive Transformer

Una estrategia para extender contexto consiste en reutilizar estados ocultos de segmentos anteriores, como en Transformer-XL. **Compressive Transformer** añade una memoria comprimida para conservar información más antigua que la memoria inmediata. El paper correcto es *Compressive Transformers for Long-Range Sequence Modelling*, arXiv:1911.05507.

#### Memoria externa no diferenciable y kNN-LM

Los sistemas de memoria externa pueden almacenar representaciones en un datastore e incorporar búsqueda de vecinos cercanos. **kNN-LM** interpola la distribución del LM paramétrico con una distribución derivada de vecinos recuperados en el espacio de representaciones del modelo. El datastore puede cambiarse sin reentrenar el LM, lo que permite adaptación de dominio y recuperación explícita de patrones poco frecuentes.

#### SPALM: Adaptive Semiparametric Language Models

**SPALM no significa "Sparse and Local Memory Augmented LM".** El trabajo de Yogatama, de Masson d'Autume y Kong se titula *Adaptive Semiparametric Language Models*. La arquitectura combina tres fuentes de información:

1. un Transformer para el contexto local,
2. memoria de corto plazo mediante cache de estados ocultos, siguiendo la idea de Transformer-XL,
3. memoria episódica global basada en recuperación aproximada de vecinos en una base key-value.

Un mecanismo de gating dependiente del contexto decide cuánto utilizar de cada fuente para cada predicción. La propuesta es, por tanto, una arquitectura semiparamétrica con combinación adaptativa de contexto local, memoria corta y memoria larga, no un esquema de atención local/dispersa en el sentido de Longformer o BigBird.

#### Memorizing Transformer

**Memorizing Transformer** extiende un Transformer decoder-only con una memoria **no diferenciable** de pares `(key, value)` procedentes de entradas recientes. Durante la inferencia, una búsqueda kNN aproximada recupera memorias relevantes y las integra con la atención local. El paper demuestra que el rendimiento mejora al aumentar la memoria hasta cientos de miles de tokens y que el modelo puede utilizar información nueva observada durante el test sin actualizar sus pesos.

Esta descripción es distinta de una "memoria jerárquica y diferenciable" o de extraer activaciones de neuronas específicas: esas formulaciones no describen el mecanismo central del paper de Wu et al.

### Referencias fundamentales

#### Arquitectura base y modelos

- Vaswani, A., et al. (2017). *Attention Is All You Need*. arXiv:1706.03762.
- Devlin, J., et al. (2018). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. arXiv:1810.04805.
- Radford, A., et al. (2018). *Improving Language Understanding by Generative Pre-Training*.

#### Posición

- Shaw, P., Uszkoreit, J., & Vaswani, A. (2018). *Self-Attention with Relative Position Representations*. arXiv:1803.02155.
- Su, J., et al. (2021). *RoFormer: Enhanced Transformer with Rotary Position Embedding*. arXiv:2104.09864.
- Press, O., Smith, N. A., & Lewis, M. (2022). *Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation*. ICLR 2022, arXiv:2108.12409.

#### Atención eficiente

- Dao, T., et al. (2022). *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness*. arXiv:2205.14135.
- Shazeer, N. (2019). *Fast Transformer Decoding: One Write-Head is All You Need*. arXiv:1911.02150.
- Ainslie, J., et al. (2023). *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints*. arXiv:2305.13245.

#### Contexto largo y memoria

- Dai, Z., et al. (2019). *Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context*. arXiv:1901.02860.
- Beltagy, I., Peters, M. E., & Cohan, A. (2020). *Longformer: The Long-Document Transformer*. arXiv:2004.05150.
- Zaheer, M., et al. (2020). *Big Bird: Transformers for Longer Sequences*. arXiv:2007.14062.
- Kitaev, N., Kaiser, L., & Levskaya, A. (2020). *Reformer: The Efficient Transformer*. arXiv:2001.04451.
- Rae, J. W., Potapenko, A., Jayakumar, S. M., & Lillicrap, T. P. (2019). *Compressive Transformers for Long-Range Sequence Modelling*. arXiv:1911.05507.
- Khandelwal, U., Levy, O., Jurafsky, D., Zettlemoyer, L., & Lewis, M. (2020). *Generalization through Memorization: Nearest Neighbor Language Models*. ICLR 2020, arXiv:1911.00172.
- Yogatama, D., de Masson d'Autume, C., & Kong, L. (2021). *Adaptive Semiparametric Language Models*. TACL 9:362-373, arXiv:2102.02557.
- Wu, Y., Rabe, M. N., Hutchins, D. S., & Szegedy, C. (2022). *Memorizing Transformers*. ICLR 2022, arXiv:2203.08913.

#### Optimización de entrenamiento

- Loshchilov, I., & Hutter, F. (2019). *Decoupled Weight Decay Regularization*. arXiv:1711.05101.
- You, Y., et al. (2020). *Large Batch Optimization for Deep Learning: Training BERT in 76 minutes*. arXiv:1904.00962.
- Micikevicius, P., et al. (2018). *Mixed Precision Training*. arXiv:1710.03740.
