"""Metricas de recuperacion (adaptadas del Cuaderno 7).

Los qrels son binarios y estan sobre passage_id. Si la unidad recuperada
contiene varios pasajes (chunks de la PC2), primero se expande el ranking de
unidades a un ranking de pasajes sin repetir.
"""
from __future__ import annotations

import math

import numpy as np


def expandir_a_pasajes(ranking):
    orden, vistos = [], set()
    for u in ranking:
        for pid in u["passage_ids"]:
            if pid not in vistos:
                orden.append(pid)
                vistos.add(pid)
    return orden


def recall_at_k(ranking, relevantes, k):
    rel = set(relevantes)
    return len(rel & set(ranking[:k])) / len(rel)


def reciprocal_rank(ranking, relevantes):
    rel = set(relevantes)
    for i, pid in enumerate(ranking, 1):
        if pid in rel:
            return 1.0 / i
    return 0.0


def dcg_at_k(ranking, relevantes, k):
    rel = set(relevantes)
    total = 0.0
    for i, pid in enumerate(ranking[:k], 1):
        ganancia = 1.0 if pid in rel else 0.0  # 2^rel - 1 con rel binaria
        total += ganancia / math.log2(i + 1)
    return total


def ndcg_at_k(ranking, relevantes, k):
    ideal = dcg_at_k(list(relevantes), relevantes, k)
    return dcg_at_k(ranking, relevantes, k) / ideal if ideal > 0 else 0.0


def metricas_consulta(ranking_pasajes, relevantes, ks=(1, 3, 5)):
    fila = {f"recall@{k}": recall_at_k(ranking_pasajes, relevantes, k) for k in ks}
    fila["mrr"] = reciprocal_rank(ranking_pasajes, relevantes)
    fila["ndcg@5"] = ndcg_at_k(ranking_pasajes, relevantes, 5)
    return fila


def tipo_fallo(ranking_pasajes, relevantes, profundidad, k=3):
    """Taxonomia de la semana 7 para recuperacion."""
    if recall_at_k(ranking_pasajes, relevantes, profundidad) == 0:
        return "RETRIEVAL_MISS"
    r = recall_at_k(ranking_pasajes, relevantes, k)
    if r == 0:
        return "RANKING_ERROR"
    if r < 1:
        return "PARTIAL_RECALL"
    return "RETRIEVAL_OK"


def bootstrap_pareado(a, b, n=5000, seed=42, alpha=0.05):
    """IC 95 % de la diferencia media b - a sobre las mismas consultas."""
    d = np.asarray(b, dtype=float) - np.asarray(a, dtype=float)
    rng = np.random.default_rng(seed)
    medias = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)])
    lo, hi = np.quantile(medias, [alpha / 2, 1 - alpha / 2])
    return {"delta_media": float(d.mean()), "ic95_bajo": float(lo), "ic95_alto": float(hi),
            "cruza_cero": bool(lo <= 0 <= hi), "consultas_mejoran": int((d > 0).sum()),
            "consultas_empeoran": int((d < 0).sum())}


def _pruebas():
    a, b, rel = ["R", "X", "Y", "Z"], ["X", "Y", "R", "Z"], ["R"]
    assert recall_at_k(a, rel, 4) == recall_at_k(b, rel, 4) == 1.0
    assert reciprocal_rank(a, rel) > reciprocal_rank(b, rel)
    assert ndcg_at_k(a, rel, 4) > ndcg_at_k(b, rel, 4)
    assert expandir_a_pasajes([{"passage_ids": ["P1", "P2"]}, {"passage_ids": ["P2", "P3"]}]) == ["P1", "P2", "P3"]
    assert ndcg_at_k(["R1", "R2"], ["R1", "R2"], 5) == 1.0


_pruebas()
