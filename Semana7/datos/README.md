### Datos de Semana 7

Semana 7 no reemplaza el benchmark de Semanas 4 y 5.

#### Datos heredados

Se reutilizan directamente:

```text
Semana4/datos/corpus_semana4.jsonl
Semana4/datos/queries_semana4.jsonl
Semana4/datos/qrels_semana4.json
```

El benchmark contiene 24 consultas y qrels definidos sobre `passage_id`.

#### Archivo nuevo: `reference_answers_semana7.jsonl`

Añade anotaciones para evaluar la etapa de generación.

Cada registro contiene:

```text
query_id
reference_answer
supporting_passage_ids
required_facts
```

`supporting_passage_ids` debe ser consistente con los qrels existentes.

`required_facts` sirve como guía de auditoría y para construir proxies de depuración. No convierte automáticamente una comparación léxica en una evaluación semántica perfecta.

#### Regla de congelamiento

Durante el experimento canónico no se modifican después de observar resultados:

```text
corpus
queries
qrels
reference_answers
```

Si se corrige una anotación, debe registrarse como una nueva versión del benchmark y regenerarse el manifiesto de resultados.

#### Unidad de relevancia

La relevancia permanece definida sobre passages.

Los chunks son unidades construidas por el sistema:

```text
chunk_id
-> passage_ids
```

El notebook convierte rankings de chunks en rankings de passages sin duplicados para evitar que el overlap cuente dos veces la misma evidencia.

#### Limitación

Las 24 consultas constituyen un benchmark docente pequeño.

Sirven para:

```text
comparar configuraciones
aprender métricas
hacer análisis de errores
practicar reproducibilidad
```

No sirven para afirmar rendimiento general de un sistema RAG de producción.
