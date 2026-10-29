"""Experimento 1: recuperacion densa (A), hibrida con RRF (B) y con reranking (C).

Uso:
    python EP/src/exp1_recuperacion.py

Mismas 20 consultas con qrels, mismas unidades, misma profundidad de
candidatos y mismos modelos en todas las condiciones. A0 (configuracion de la
PC2) se corre como referencia. Las consultas de control (sin qrels) se
recuperan igual porque el experimento 2 las usa, pero no entran en las metricas.

Salidas en EP/results/exp1/.
"""
from __future__ import annotations

import json
import platform
import sys

import numpy as np
import pandas as pd

import benchmark
import config_ep as C
import metricas as M
from recuperacion import Sistema, cross_encoder

CONDICIONES = ["A0", "A", "B", "C"]
OUT = C.RESULTS / "exp1"


def p95(x):
    return float(np.percentile(np.asarray(x, dtype=float), 95))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    congelado = benchmark.verificar_congelado()
    docs, consultas, qrels, _ = benchmark.cargar()

    sis = Sistema(docs)
    print(f"unidades A/B/C: {len(sis.unidades)} pasajes | chunks PC2 (A0): {len(sis.chunks_pc2)}")
    sis.calentar()

    # chequeo: FAISS IndexFlatIP da el mismo orden que el producto interno en numpy
    q = __import__("recuperador").codificar([consultas[0]["query"]], C.PREFIJO_QUERY)
    _, idx = sis.index.search(q, 10)
    np_orden = np.argsort(-(q @ sis.vec.T)[0], kind="stable")[:10]
    assert list(idx[0]) == list(np_orden), "FAISS y numpy no coinciden"

    # tokens del par mas largo que ve el cross-encoder (su ventana es de 512)
    ce = cross_encoder()
    largo = max(len(ce.tokenizer(c["query"], u["text"])["input_ids"]) for c in consultas[:3] for u in sis.unidades)

    filas, rankings = [], []
    for cond in CONDICIONES:
        for c in consultas:
            ranking, t = sis.correr(cond, c["query"])
            pasajes = M.expandir_a_pasajes(ranking)
            rankings.append({"condicion": cond, "query_id": c["query_id"],
                             "unidades": [[u["unit_id"], round(u["score"], 6)] for u in ranking],
                             "pasajes": pasajes})
            if not qrels[c["query_id"]]:
                continue
            fila = {"condicion": cond, "query_id": c["query_id"], "tipo": c["tipo"], "dificultad": c["dificultad"],
                    **M.metricas_consulta(pasajes, qrels[c["query_id"]]), **t,
                    "fallo": M.tipo_fallo(pasajes, qrels[c["query_id"]], len(pasajes))}
            filas.append(fila)
        print(f"{cond}: listo")

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "por_consulta.csv", index=False)
    with (OUT / "rankings.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for r in rankings:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    met = ["recall@1", "recall@3", "recall@5", "mrr", "ndcg@5"]
    resumen = df.groupby("condicion")[met].mean().reindex(CONDICIONES).round(4)
    resumen.to_csv(OUT / "resumen.csv")
    lat = df.groupby("condicion").agg(dense_ms=("dense_ms", "mean"), bm25_ms=("bm25_ms", "mean"),
                                      rrf_ms=("rrf_ms", "mean"), reranker_ms=("reranker_ms", "mean"),
                                      total_ms=("total_ms", "mean"), total_p95_ms=("total_ms", p95))
    lat = lat.reindex(CONDICIONES).round(2)
    lat.to_csv(OUT / "latencia.csv")
    fallos = pd.crosstab(df["condicion"], df["fallo"]).reindex(CONDICIONES).fillna(0).astype(int)
    fallos.to_csv(OUT / "fallos.csv")

    boot = []
    for a, b in [("A", "B"), ("B", "C"), ("A", "C"), ("A0", "A")]:
        for m in ["recall@3", "mrr", "ndcg@5"]:
            xa = df[df.condicion == a].sort_values("query_id")[m].to_numpy()
            xb = df[df.condicion == b].sort_values("query_id")[m].to_numpy()
            boot.append({"comparacion": f"{b} - {a}", "metrica": m,
                         **M.bootstrap_pareado(xa, xb, C.BOOTSTRAP_RESAMPLES, C.SEED)})
    boot = pd.DataFrame(boot)
    boot.to_csv(OUT / "bootstrap.csv", index=False)

    import faiss, rank_bm25, sentence_transformers, torch, transformers  # noqa: E401
    manifiesto = {
        "experimento": 1, "benchmark_congelado": congelado,
        "config": {"unidad": "pasaje + encabezado del proceso", "n_unidades": len(sis.unidades),
                   "n_chunks_pc2": len(sis.chunks_pc2), "candidate_depth": C.CANDIDATE_DEPTH,
                   "rrf_constant": C.RRF_CONSTANT, "bm25": {"k1": C.BM25_K1, "b": C.BM25_B, "epsilon": C.BM25_EPSILON},
                   "encoder": [C.ENCODER_ID, C.ENCODER_REVISION], "reranker": [C.RERANKER_ID, C.RERANKER_REVISION],
                   "pc2_target_words": C.PC2_TARGET_WORDS, "pc2_overlap": C.PC2_OVERLAP,
                   "max_tokens_par_reranker": largo, "seed": C.SEED},
        "versiones": {"python": platform.python_version(), "faiss": faiss.__version__,
                      "rank_bm25": __import__("importlib.metadata").metadata.version("rank-bm25"), "sentence_transformers": sentence_transformers.__version__,
                      "transformers": transformers.__version__, "torch": torch.__version__},
        "maquina": platform.processor() or platform.machine(),
        "resumen": resumen.reset_index().to_dict(orient="records"),
        "latencia": lat.reset_index().to_dict(orient="records"),
    }
    (OUT / "manifiesto.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n", resumen, "\n\n", lat, "\n\n", fallos, "\n\n", boot.round(3).to_string(index=False))
    print(f"\nmax tokens par consulta+pasaje en el reranker (3 consultas): {largo}")


if __name__ == "__main__":
    main()
