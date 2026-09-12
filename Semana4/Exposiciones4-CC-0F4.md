### **Exposiciones de refuerzo - Semana 4**

#### **Propósito**

Las exposiciones complementan embeddings y retrieval sin convertir la sesión en un recorrido por librerías.

Formato recomendado para cuatro grupos:

```text
15 min exposición
5 min preguntas x 4 grupos = 80 min

10 min
transiciones y cierre
```

Cada grupo debe partir de al menos una **fuente primaria** y explicar:

```text
problema -> idea central -> estructura o algoritmo -> trade-off -> ejemplo o mini-experimento -> limitación
```

El objetivo no es resumir un paper diapositiva por diapositiva, sino comprender qué problema intenta resolver, cómo lo hace y qué evidencia presenta.


#### **Uso simplificado de herramientas de apoyo**

Para preparar la exposición puedes/pueden utilizar herramientas de búsqueda, exploración y análisis de literatura científica.

Estas herramientas sirven para:

```text
encontrar papers -> descubrir trabajos relacionados -> entender rápidamente su contenido -> contrastar citas -> seleccionar la fuente primaria ->
leer y verificar el paper original
```

No sustituyen la lectura de la fuente primaria.

##### **Elicit**

Uso recomendado:

```text
pregunta de investigación -> buscar papers relevantes -> comparar objetivo, método y resultados -> seleccionar candidatos
```

Puede utilizarse para comenzar con una pregunta en lenguaje natural y localizar trabajos relacionados aunque no se conozcan exactamente las palabras clave utilizadas por los autores. Elicit emplea búsqueda semántica y permite comparar información extraída de los papers.

Ejemplo:

```text
How does HNSW trade recall for search latency?
```

Uso en la exposición:

> localizar dos o tres papers relacionados y justificar por qué se eligió el paper principal.

##### **ResearchRabbit**

Uso recomendado:

```text
paper inicial -> trabajos similares -> trabajos anteriores -> trabajos posteriores -> red de citas
```

Es especialmente útil cuando ya se encontró un buen **paper semilla**. Permite navegar por relaciones entre trabajos y encontrar literatura que una búsqueda solamente por palabras clave podría omitir.

Ejemplo:

```text
Sentence-BERT -> trabajos similares -> E5/BGE/otros modelos de embeddings
```

Uso en la exposición:

> identificar un antecedente y un trabajo posterior relacionado con la técnica presentada.


##### **Connected Papers**

Uso recomendado:

```text
paper semilla -> grafo visual -> papers cercanos -> prior works -> derivative works
```

Connected Papers construye un grafo de trabajos relacionados a partir de un paper inicial. La proximidad del grafo representa similitud basada, entre otros elementos, en co-citación y acoplamiento bibliográfico; no debe interpretarse simplemente como un árbol de citas.

Ejemplo:

```text
HNSW -> grafo -> métodos anteriores de ANN -> trabajos posteriores
```

Uso en la exposición:

> mostrar cómo el paper se ubica dentro de una línea de investigación.

No es necesario colocar todo el grafo en las diapositivas.


##### **Scite**

Uso recomendado:

```text
paper -> citas recibidas -> contexto de la cita -> supporting/contrasting/mentioning
```

Scite permite inspeccionar **cómo** otros trabajos citan un artículo mediante sus Smart Citations, incluyendo contexto de la cita y clasificación como evidencia de apoyo, contraste o simple mención.

Ejemplo:

```text
paper de HNSW -> ¿qué trabajos posteriores lo utilizan? -> ¿existen resultados que contrasten sus conclusiones?
```

Uso en la exposición:

> comprobar si una afirmación importante del paper ha sido posteriormente apoyada, discutida o contrastada.

No debe interpretarse:

```text
muchas citas = paper correcto
```

##### **SciSpace**

Uso recomendado:

```text
paper -> leer PDF -> preguntar por método -> identificar resultados -> localizar limitaciones
```

SciSpace permite buscar literatura, filtrar resultados y utilizar `Chat with PDF` para consultar aspectos como metodología, resultados o posibles limitaciones del documento.

Ejemplos de preguntas:

```text
What is the main contribution of this paper?

What baseline does the paper compare against?

Which metric is used to evaluate retrieval?

What limitations do the authors report?
```

Uso en la exposición:

> utilizarlo para acelerar la lectura inicial y después comprobar las respuestas directamente en el PDF.

La respuesta de SciSpace no debe citarse como si fuera la fuente científica.


##### **Consensus**

Uso recomendado:

```text
pregunta concreta -> buscar evidencia científica -> observar resultados de varios papers -> identificar acuerdo o desacuerdo
```

Consensus busca literatura académica a partir de preguntas en lenguaje natural y genera síntesis vinculadas a papers. Para determinadas preguntas de tipo sí/no puede mostrar el `Consensus Meter`, que resume el grado de acuerdo entre los trabajos recuperados.

Ejemplo:

```text
Do approximate nearest-neighbor methods reduce search latency while preserving high recall?
```

Uso en la exposición:

> obtener una primera visión del problema y localizar papers que después deben revisarse individualmente.

El propio sistema advierte que el `Consensus Meter` se construye a partir de un subconjunto de los trabajos recuperados y no representa necesariamente toda la literatura existente.

#### **Flujo recomendado para preparar una exposición**

No es necesario utilizar todas las herramientas.

Una ruta simple es:

```text
1. formular la pregunta técnica
          |
          v
2. Elicit/Consensus/SciSpace
   encontrar papers candidatos
          |
          v
3. elegir un paper semilla
          |
          v
4. ResearchRabbit/Connected Papers
   explorar trabajos relacionados
          |
          v
5. Scite
   revisar cómo ha sido citado
          |
          v
6. leer el paper original
          |
          v
7. preparar la exposición
```

Una combinación suficiente sería, por ejemplo:

```text
Elicit + Connected Papers + Scite
```

o:

```text
SciSpace + ResearchRabbit + Scite
```

El resultado final debe basarse en el **paper original**, no en los textos generados por estas herramientas.

#### **Evidencia mínima del proceso de búsqueda**

Cada grupo añadirá una sola diapositiva final denominada:

### **Ruta de búsqueda bibliográfica**

Debe contener únicamente:

```text
Pregunta utilizada:

Paper semilla:

Herramientas utilizadas:

Un paper relacionado encontrado:

¿Por qué fue útil?

```

No se calificará quién utilizó más herramientas.

Se evaluará si el grupo puede explicar:

```text
cómo encontró la literatura -> por qué seleccionó el paper -> qué verificó en la fuente primaria
```


### **Tema 1 - Modern text embedding models**

Pregunta guía:

> ¿Qué cambia cuando pasamos de usar hidden states de un Transformer a un encoder entrenado específicamente para similitud y retrieval?

Puntos mínimos:

* bi-encoder,
* sentence embeddings,
* contrastive learning,
* normalización,
* semantic search,
* multilingüismo,
* limitaciones.

Fuente primaria sugerida:

```text
Reimers, N. y Gurevych, I. (2019).
Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks.
https://arxiv.org/abs/1908.10084
```

Extensión opcional:

```text
E5
BGE
embeddings multilingües modernos
```

Ruta sugerida:

```text
SBERT -> ResearchRabbit o Connected Papers -> modelos posteriores -> Scite -> contrastar impacto y citas
```


### **Tema 2 - HNSW y Approximate Nearest Neighbors**

Pregunta guía:

> ¿Por qué aceptar una búsqueda aproximada puede ser útil cuando el índice crece?

Puntos mínimos:

* exact search vs ANN,
* grafo de proximidad,
* construcción multicapa,
* búsqueda,
* recall vs latencia,
* parámetros principales,
* costo de memoria.

Fuente primaria sugerida:

```text
Malkov, Y. A. y Yashunin, D. A. (2018).
Efficient and robust approximate nearest neighbor search
using Hierarchical Navigable Small World graphs.
https://arxiv.org/abs/1603.09320
```

Debe quedar explícito:

```text
FAISS IndexFlatIP != HNSW
```

Ruta sugerida:

```text
HNSW -> Connected Papers -> métodos ANN relacionados -> Scite -> evidencia posterior
```


### **Tema 3 - Product Quantization**

Pregunta guía:

> ¿Cómo reducir el costo de almacenar y comparar millones de vectores?

Puntos mínimos:

* partición del vector,
* codebooks,
* códigos compactos,
* reducción de memoria,
* error de cuantización,
* trade-off memoria vs calidad.

Fuente primaria sugerida:

```text
Jégou, H., Douze, M. y Schmid, C. (2011).
Product Quantization for Nearest Neighbor Search.
IEEE TPAMI.
```

No es necesario implementar PQ desde cero.

Ruta sugerida:

```text
Product Quantization -> Elicit o SciSpace -> identificar contribución y métricas -> ResearchRabbit -> métodos posteriores
```


### **Tema 4 - ColBERT y late interaction**

Pregunta guía:

> ¿Qué información pierde un único vector por documento y cómo intenta recuperarla late interaction?

Puntos mínimos:

* bi-encoder,
* cross-encoder,
* representaciones por token,
* MaxSim,
* indexación,
* costo,
* relación con retrieval y reranking.

Fuente primaria sugerida:

```text
Khattab, O. y Zaharia, M. (2020).
ColBERT: Efficient and Effective Passage Search
via Contextualized Late Interaction over BERT.
https://arxiv.org/abs/2004.12832
```

Ruta sugerida:

```text
ColBERT -> SciSpace -> comprender MaxSim -> Connected Papers o ResearchRabbit -> ColBERTv2 y trabajos relacionados -> Scite -> revisar uso posterior
```

#### **Evidencia mínima de la exposición**

Cada grupo debe incluir al menos una de estas opciones:

1. diagrama técnico reconstruido por el grupo,
2. tabla pequeña reconstruida desde la fuente primaria,
3. mini-experimento reproducible,
4. comparación controlada de dos configuraciones.

Debe aparecer una limitación explícita.

Además, se incluye la diapositiva breve:

```text
Ruta de búsqueda bibliográfica
```

indicando cómo se llegó al paper principal y a un trabajo relacionado.


#### **Regla sobre herramientas de IA para investigación**

Las herramientas:

```text
Elicit
ResearchRabbit
Connected Papers
Scite
SciSpace
Consensus
```

pueden utilizarse para:

```text
buscar
descubrir
organizar
comparar
explorar citas
acelerar lectura
```

pero no sustituyen:

```text
leer la fuente primaria
verificar el método
comprobar las métricas
interpretar los resultados
identificar las limitaciones
```

Una afirmación técnica presentada en la exposición debe poder rastrearse hasta el paper correspondiente.


#### **Preguntas de defensa comunes**

1. ¿Qué problema intenta resolver el trabajo?
2. ¿Cuál es el baseline principal?
3. ¿Qué variable controla el trade-off de la técnica?
4. ¿Qué métrica utiliza el paper para demostrar una mejora?
5. ¿Qué evidencia respalda la conclusión principal?
6. ¿Qué limitación reconocen los autores?
7. ¿Qué parte del resultado no puede generalizarse automáticamente a nuestro corpus?
8. ¿Qué paper relacionado encontraron y mediante qué herramienta?
9. ¿Qué información obtenida mediante una herramienta de IA verificaron directamente en el paper?
10. ¿Qué componente de CC-0F4 cambiaría si incorporáramos esta técnica?.
