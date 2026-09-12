### Datos de Semana 4

#### Archivos

```text
corpus_semana4.jsonl
queries_semana4.jsonl
qrels_semana4.json
```

El corpus contiene 12 documentos y 72 passages. Las 24 consultas tienen relevancias conocidas definidas sobre `passage_id`.

La relevancia se define sobre passages, no sobre chunks, porque los chunks cambian cuando cambia `target_words`. Algunas consultas tienen más de un passage relevante, por lo que `Recall@k` puede tomar valores intermedios y no se reduce siempre a `Hit@k`.

Los textos son material didáctico creado para el curso. No son tickets reales ni contienen información privada.

#### Regla experimental

No modificar después de observar resultados:

```text
corpus
queries
qrels
```

Si cambia cualquiera de estos elementos, debe registrarse como una nueva versión del benchmark.
