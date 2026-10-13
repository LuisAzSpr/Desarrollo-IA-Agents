### Resultados generados - Semana 7

Este directorio recibe artefactos producidos por `Cuaderno7-CC-0F4.ipynb`.

Archivos esperados:

```text
retrieval_summary.csv
retrieval_per_query.csv
latency_by_stage.csv
bootstrap_pairwise_ci.csv
generation_outputs.csv
faithfulness_audit_template.csv
latest_run.json
```

`generation_outputs.csv` solo aparece cuando se activa el generador real.

Los resultados generados no deben versionarse automáticamente como si fueran evidencia universal. La corrida canónica debe registrar configuración, hashes y modo real/offline.

#### Modo de validación de software

```bash
CC0F4_RUN_REAL_RETRIEVAL=0 \
CC0F4_RUN_REAL_RERANKER=0 \
CC0F4_RUN_REAL_LLM=0 \
make execute-cuaderno7
```

Los números de este modo no sustituyen el experimento con modelos canónicos.
#### Nuevos artefactos metodológicos

`bootstrap_pairwise_ci.csv` contiene diferencias pareadas e IC 95% para `Recall@3`, `MRR` y `nDCG@5` en A->B y B->C.

`latency_by_stage.csv` descompone el costo medio en `dense`, `BM25`, `RRF` y `reranker`, además de latencia total media y p95.
