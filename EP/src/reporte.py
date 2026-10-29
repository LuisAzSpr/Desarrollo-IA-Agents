"""Figuras del README y de las diapositivas a partir de los CSV de results/.

Uso:
    python EP/src/reporte.py
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import config_ep as C  # noqa: E402

COLORES = {"A0": "#2a78d6", "A": "#eb6834", "B": "#1baf7a", "C": "#eda100"}
COND = ["A0", "A", "B", "C"]
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})


def metricas():
    res = pd.read_csv(C.RESULTS / "exp1" / "resumen.csv", index_col=0)
    met = ["recall@1", "recall@3", "recall@5", "mrr", "ndcg@5"]
    x = np.arange(len(met))
    fig, ax = plt.subplots(figsize=(8, 3.6))
    w = 0.2
    for i, c in enumerate(COND):
        ax.bar(x + (i - 1.5) * w, res.loc[c, met], w * 0.9, label=c, color=COLORES[c])
    for j, m in enumerate(met):  # solo se rotula C, la mejor en casi todo
        ax.text(x[j] + 1.5 * w, res.loc["C", m] + 0.02, f"{res.loc['C', m]:.2f}", ha="center", fontsize=8)
    ax.set_xticks(x, ["Recall@1", "Recall@3", "Recall@5", "MRR", "nDCG@5"])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("media en 20 consultas")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(ncol=4, frameon=False, loc="upper left", fontsize=9)
    ax.set_title("Exp. 1: A0 = PC2, A = denso, B = A + BM25 + RRF, C = B + Cross-Encoder", fontsize=10)
    fig.tight_layout()
    fig.savefig(C.FIGS / "exp1_metricas.png", dpi=160)
    plt.close(fig)


def latencia():
    lat = pd.read_csv(C.RESULTS / "exp1" / "latencia.csv", index_col=0).loc[COND]
    etapas = [("dense_ms", "denso", "#2a78d6"), ("bm25_ms", "BM25", "#1baf7a"),
              ("rrf_ms", "RRF", "#6250d6"), ("reranker_ms", "Cross-Encoder", "#eda100")]
    fig, ax = plt.subplots(figsize=(8, 2.6))
    izq = np.zeros(len(COND))
    for col, nombre, color in etapas:
        ax.barh(COND, lat[col], left=izq, color=color, label=nombre, edgecolor="white", linewidth=1)
        izq += lat[col].to_numpy()
    for i, c in enumerate(COND):
        ax.text(lat.loc[c, "total_ms"] + 15, i, f"{lat.loc[c, 'total_ms']:.0f} ms (p95 {lat.loc[c, 'total_p95_ms']:.0f})",
                va="center", fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, lat["total_ms"].max() * 1.35)
    ax.set_xlabel("latencia media por consulta (ms, CPU)")
    ax.legend(ncol=4, frameon=False, fontsize=8, loc="upper right")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(C.FIGS / "exp1_latencia.png", dpi=160)
    plt.close(fig)


def por_consulta():
    df = pd.read_csv(C.RESULTS / "exp1" / "por_consulta.csv")
    tab = df.pivot(index="query_id", columns="condicion", values="recall@3")[COND]
    tipo = df.drop_duplicates("query_id").set_index("query_id")["tipo"]
    fig, ax = plt.subplots(figsize=(4.6, 7))
    ax.imshow(tab.to_numpy(), cmap="Blues", vmin=0, vmax=1.15, aspect="auto")
    for i in range(tab.shape[0]):
        for j in range(tab.shape[1]):
            v = tab.iat[i, j]
            ax.text(j, i, f"{v:.2g}", ha="center", va="center", fontsize=8, color="white" if v > 0.6 else "black")
    ax.set_xticks(range(4), COND)
    ax.set_yticks(range(len(tab)), [f"{q} {tipo[q]}" for q in tab.index], fontsize=8)
    ax.xaxis.tick_top()
    ax.set_title("Recall@3 por consulta", fontsize=10, pad=22)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(C.FIGS / "exp1_recall3_por_consulta.png", dpi=160)
    plt.close(fig)


def rag():
    aud = pd.read_csv(C.RESULTS / "exp2" / "auditoria_respuestas.csv")
    cats = [("correcta", "correcta", "#1baf7a"), ("parcial", "parcial", "#eda100"),
            ("incorrecta", "incorrecta (afirma algo falso)", "#e34948"),
            ("no_responde", "no responde (habia evidencia)", "#9e9e9e"),
            ("abstencion_correcta", "abstencion correcta (control)", "#2a78d6")]
    conds = [("closed_book", "closed-book"), ("rag_C", "RAG (top-5 de C)")]
    fig, ax = plt.subplots(figsize=(8, 2.4))
    izq = np.zeros(len(conds))
    for cat, nombre, color in cats:
        n = np.array([(aud[aud.condicion == c].correccion == cat).sum() for c, _ in conds])
        ax.barh([e for _, e in conds], n, left=izq, color=color, label=nombre, edgecolor="white", linewidth=2)
        for i, v in enumerate(n):
            if v:
                ax.text(izq[i] + v / 2, i, str(v), ha="center", va="center", fontsize=9, color="white")
        izq += n
    ax.invert_yaxis()
    ax.set_xlabel("consultas (12 por condicion, auditoria manual)")
    ax.legend(ncol=3, frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.35))
    fig.tight_layout()
    fig.savefig(C.FIGS / "exp2_auditoria.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main():
    C.FIGS.mkdir(parents=True, exist_ok=True)
    metricas()
    latencia()
    por_consulta()
    rag()
    print("figuras en", C.FIGS)


if __name__ == "__main__":
    main()
