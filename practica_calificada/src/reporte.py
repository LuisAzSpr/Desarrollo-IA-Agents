"""Métricas, tablas y figuras a partir de results/*.jsonl.

Uso:
    python src/reporte.py

Salidas:
    results/metricas.json
    results/resumen_experimentos.md
    results/figs/*.png
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

sys.stdout.reconfigure(encoding="utf-8")

from config import CASOS_PATH, FIGS_DIR, LABELS, ORDEN_RIESGO, RESULTS_DIR
import graficos as g

EXPS = ["exp1_prompt", "exp2_contexto", "exp3_decoding", "exp4_fewshot"]


def leer_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def pred_para_metricas(v):
    return v if v in LABELS else "invalido"


def metricas(df: pd.DataFrame) -> dict:
    valid = df[df["schema_valid"]]
    # Estricto: una salida que no cumple el schema cuenta como "invalido",
    # aunque su campo riesgo tenga un valor del enum.
    pred = df["pred_riesgo"].where(df["schema_valid"], "invalido").map(pred_para_metricas)
    return {
        "n": int(len(df)),
        "json_exacto_rate": round(df["json_exacto"].mean(), 3),
        "json_parseable_rate": round(df["json_recuperado"].mean(), 3),
        "schema_valid_rate": round(df["schema_valid"].mean(), 3),
        "accuracy": round(df["riesgo_correcto"].mean(), 3),
        "macro_f1": round(f1_score(df["gold_riesgo"], pred, labels=LABELS, average="macro", zero_division=0), 3),
        "senal_accuracy": round(df["senal_correcta"].mean(), 3),
        "coherencia_rate": round(valid["coherente"].mean(), 3) if len(valid) else None,
        "evidencia_literal_rate": round(valid["evidencia_literal"].mean(), 3) if len(valid) else None,
        "confianza_media": round(valid["confianza"].mean(), 3) if len(valid) else None,
        "distribucion_pred": dict(Counter(pred)),
        "prompt_tokens_medio": round(df["prompt_tokens"].mean(), 1),
        "tokens_generados_medio": round(df["generated_tokens"].mean(), 1),
        "latencia_media_s": round(df["latency_ms"].mean() / 1000, 1),
        "truncados": int(df["truncado"].sum()),
    }


def tabla_md(filas: list[dict], columnas: list[str]) -> str:
    L = ["| " + " | ".join(columnas) + " |", "|" + "|".join("---" for _ in columnas) + "|"]
    for f in filas:
        L.append("| " + " | ".join(str(f.get(c, "")) for c in columnas) + " |")
    return "\n".join(L)


def df_md(df: pd.DataFrame) -> str:
    return tabla_md(df.to_dict("records"), list(df.columns))


def etiqueta_corta(fila) -> str:
    if not fila["json_recuperado"]:
        return "json✗"
    if not fila["schema_valid"]:
        return "schema✗"
    return fila["pred_riesgo"]


def por_caso(df: pd.DataFrame, cond_a: str, cond_b: str) -> pd.DataFrame:
    a = df[df["condicion"] == cond_a].drop_duplicates("id").set_index("id")
    b = df[df["condicion"] == cond_b].drop_duplicates("id").set_index("id")
    t = pd.DataFrame({
        "gold": a["gold_riesgo"],
        cond_a: a.apply(etiqueta_corta, axis=1),
        cond_b: b.apply(etiqueta_corta, axis=1),
        f"senal_{cond_a}": a["pred_senal"],
        f"senal_{cond_b}": b["pred_senal"],
        f"ok_{cond_a}": a["riesgo_correcto"],
        f"ok_{cond_b}": b["riesgo_correcto"],
    })
    t["cambio"] = np.where(t[f"ok_{cond_a}"] == t[f"ok_{cond_b}"],
                           np.where(t[cond_a] == t[cond_b], "igual", "cambia (mismo acierto)"),
                           np.where(t[f"ok_{cond_b}"], "mejora", "empeora"))
    return t


def resumen_exp3(df: pd.DataFrame, sondeo: pd.DataFrame | None) -> tuple[pd.DataFrame, dict]:
    greedy = df[df["condicion"] == "D0_greedy"]
    samp = df[df["condicion"] == "D1_sampling"]
    filas = []
    for cid, grp in samp.groupby("id"):
        etiquetas = grp.apply(etiqueta_corta, axis=1).tolist()
        cnt = Counter(etiquetas)
        moda, n_moda = cnt.most_common(1)[0]
        g_rows = greedy[greedy["id"] == cid]
        g_labels = g_rows.apply(etiqueta_corta, axis=1).tolist()
        just = [(p or {}).get("justificacion", "") if isinstance(p, dict) else "" for p in grp["parsed"]]
        fila = {
            "id": cid, "gold": grp["gold_riesgo"].iloc[0],
            "greedy": g_labels[0], "greedy_repetible": len(set(g_rows["raw_text"])) == 1,
            "sampling": " ".join(etiquetas), "moda": moda,
            "estabilidad": round(n_moda / len(etiquetas), 2),
            "acuerdo_con_greedy": round(sum(e == g_labels[0] for e in etiquetas) / len(etiquetas), 2),
            "etiquetas_distintas": len(cnt),
            "schema_valid_sampling": round(grp["schema_valid"].mean(), 2),
            "justificaciones_distintas": len(set(j.strip().lower() for j in just if j)),
            "acc_sampling": round(grp["riesgo_correcto"].mean(), 2),
        }
        if sondeo is not None:
            s = sondeo[(sondeo["prompt"] == "P1") & (sondeo["contexto"] == "C0") & (sondeo["id"] == cid)]
            if len(s):
                fila["margen_logits"] = s["margen_top1_top2"].iloc[0]
        filas.append(fila)
    t = pd.DataFrame(filas).set_index("id")
    # ¿Qué explica más la etiqueta muestreada: el caso o la semilla? Si la
    # distribución no dependiera del caso, la misma semilla daría la misma
    # salida en casos distintos (mismos números aleatorios, prompts parecidos).
    samp_lab = samp.assign(lab=samp.apply(etiqueta_corta, axis=1))
    por_semilla = samp_lab.groupby("seed")["lab"].agg(lambda s: s.value_counts().iloc[0] / len(s))
    por_semilla_moda = samp_lab.groupby("seed")["lab"].agg(lambda s: s.value_counts().index[0])
    agg = {
        "acuerdo_entre_casos_misma_semilla": round(float(por_semilla.mean()), 3),
        "etiqueta_modal_por_semilla": por_semilla_moda.to_dict(),
        "greedy_schema_valid_rate": round(greedy["schema_valid"].mean(), 3),
        "sampling_schema_valid_rate": round(samp["schema_valid"].mean(), 3),
        "greedy_accuracy": round(greedy[greedy["seed"] == greedy["seed"].min()]["riesgo_correcto"].mean(), 3),
        "sampling_accuracy_media": round(samp["riesgo_correcto"].mean(), 3),
        "greedy_repetible_casos": int(t["greedy_repetible"].sum()),
        "estabilidad_media": round(t["estabilidad"].mean(), 3),
        "acuerdo_con_greedy_medio": round(t["acuerdo_con_greedy"].mean(), 3),
        "casos_con_2_o_mas_etiquetas": int((t["etiquetas_distintas"] >= 2).sum()),
        "justificaciones_distintas_media": round(t["justificaciones_distintas"].mean(), 2),
    }
    if "margen_logits" in t and t["margen_logits"].notna().sum() >= 3:
        agg["corr_margen_vs_estabilidad"] = round(float(t["margen_logits"].corr(t["estabilidad"], method="spearman")), 3)
    return t, agg


def desplazamiento_contexto(sondeo: pd.DataFrame, casos: dict) -> pd.DataFrame:
    """E[riesgo ordinal] con C1 menos con C0, orientado por la dirección de la señal."""
    filas = []
    for cid, c in casos.items():
        p0 = sondeo[(sondeo["prompt"] == "P1") & (sondeo["contexto"] == "C0") & (sondeo["id"] == cid)]
        p1 = sondeo[(sondeo["prompt"] == "P1") & (sondeo["contexto"] == "C1") & (sondeo["id"] == cid)]
        if not len(p0) or not len(p1):
            continue
        e = lambda d: sum(ORDEN_RIESGO[k] * v for k, v in d.items())
        e0, e1 = e(p0["p_etiqueta_normalizada"].iloc[0]), e(p1["p_etiqueta_normalizada"].iloc[0])
        filas.append({"id": cid, "direccion_senal": c["direccion_senal_C1"], "E_riesgo_C0": round(e0, 3),
                      "E_riesgo_C1": round(e1, 3), "delta": round(e1 - e0, 3),
                      "hacia_la_senal": round((e1 - e0) * c["direccion_senal_C1"], 3)})
    return pd.DataFrame(filas).set_index("id")


# ---------------------------------------------------------------- figuras

def fig_metricas(m_a: dict, m_b: dict, nombre_a: str, nombre_b: str, titulo: str, archivo: str):
    import matplotlib.pyplot as plt
    claves = [("json_exacto_rate", "JSON exacto"), ("schema_valid_rate", "Schema-valid"),
              ("accuracy", "Accuracy"), ("macro_f1", "Macro-F1"),
              ("coherencia_rate", "Coherencia\nseñal→riesgo"), ("evidencia_literal_rate", "Evidencia\nliteral")]
    va = [m_a.get(k) or 0 for k, _ in claves]
    vb = [m_b.get(k) or 0 for k, _ in claves]
    fig, ax = plt.subplots(figsize=(7.4, 3.3))
    x = np.arange(len(claves))
    w = 0.34
    ax.set_xlim(-0.6, len(claves) - 0.4)
    ax.set_ylim(0, 1.18)
    g.limpiar_ejes(ax)
    g.barras(ax, x - w / 2 - 0.01, va, w, g.SERIE_1)
    g.barras(ax, x + w / 2 + 0.01, vb, w, g.SERIE_2)
    etiqueta = lambda v: "0" if v == 0 else ("1" if v == 1 else f"{v:.2f}".rstrip("0"))
    for xi, v in zip(x - w / 2 - 0.01, va):
        ax.text(xi, v + 0.02, etiqueta(v), ha="center", fontsize=8, color=g.TINTA_2)
    for xi, v in zip(x + w / 2 + 0.01, vb):
        ax.text(xi, v + 0.02, etiqueta(v), ha="center", fontsize=8, color=g.TINTA_2)
    ax.set_xticks(x, [c for _, c in claves], fontsize=9)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    leg = g.leyenda(ax, [(nombre_a, g.SERIE_1), (nombre_b, g.SERIE_2)], loc="lower left")
    leg.set_bbox_to_anchor((0.0, 1.0))
    leg._ncols = 2
    ax.set_title(titulo, pad=26)
    fig.savefig(FIGS_DIR / archivo)
    plt.close(fig)


def fig_matriz(columnas: dict[str, dict], casos: dict, archivo: str):
    """Filas = casos, columnas = condiciones; celda = etiqueta predicha."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    ids = list(casos)
    nombres = ["Gold", *columnas]
    fig, ax = plt.subplots(figsize=(1.05 * len(nombres) + 2.6, 0.36 * len(ids) + 1.1))
    ax.set_xlim(-0.5, len(nombres) - 0.5)
    ax.set_ylim(len(ids) - 0.5, -0.9)
    ax.axis("off")
    for j, n in enumerate(nombres):
        ax.text(j, -0.75, n, ha="center", va="center", fontsize=9, color=g.TINTA, fontweight="semibold")
    for i, cid in enumerate(ids):
        ax.text(-0.62, i, f"{cid}  {casos[cid]['corto']}", ha="right", va="center", fontsize=8.5, color=g.TINTA_2)
        for j, n in enumerate(nombres):
            v = casos[cid]["gold_riesgo"] if n == "Gold" else columnas[n].get(cid, "")
            clave = v if v in LABELS else "inválido"
            color = g.RIESGO_COLOR[clave]
            ax.add_patch(FancyBboxPatch((j - 0.44, i - 0.38), 0.88, 0.76, boxstyle="round,pad=0,rounding_size=0.08",
                                        linewidth=0, facecolor=color))
            tinta = "white" if clave in ("medio", "alto") else g.TINTA
            marca = ""
            if n != "Gold" and v in LABELS:
                marca = " ✓" if v == casos[cid]["gold_riesgo"] else " ✗"
            ax.text(j, i, f"{v}{marca}", ha="center", va="center", fontsize=8, color=tinta)
    ax.axvline(0.5, color=g.EJE, linewidth=1)
    fig.savefig(FIGS_DIR / archivo)
    plt.close(fig)


def fig_matriz_compacta(columnas: dict[str, dict], casos: dict, archivo: str):
    """Versión transpuesta para diapositivas: filas = condiciones, columnas = casos."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    ids = list(casos)
    filas = ["Gold", *columnas]
    fig, ax = plt.subplots(figsize=(0.78 * len(ids) + 1.0, 0.42 * len(filas) + 0.55))
    ax.set_xlim(-1.3, len(ids) - 0.5)
    ax.set_ylim(len(filas) - 0.5, -0.95)
    ax.axis("off")
    for j, cid in enumerate(ids):
        ax.text(j, -0.72, cid, ha="center", va="center", fontsize=9, color=g.TINTA, fontweight="semibold")
    for i, n in enumerate(filas):
        ax.text(-0.62, i, n, ha="right", va="center", fontsize=9, color=g.TINTA, fontweight="semibold")
        for j, cid in enumerate(ids):
            v = casos[cid]["gold_riesgo"] if n == "Gold" else columnas[n].get(cid, "")
            clave = v if v in LABELS else "inválido"
            ax.add_patch(FancyBboxPatch((j - 0.45, i - 0.4), 0.9, 0.8, boxstyle="round,pad=0,rounding_size=0.08",
                                        linewidth=0, facecolor=g.RIESGO_COLOR[clave]))
            marca = ""
            if n != "Gold" and v in LABELS:
                marca = " ✓" if v == casos[cid]["gold_riesgo"] else " ✗"
            ax.text(j, i, f"{v}{marca}", ha="center", va="center", fontsize=7.5,
                    color="white" if clave in ("medio", "alto") else g.TINTA)
    ax.axhline(0.5, color=g.EJE, linewidth=1)
    fig.savefig(FIGS_DIR / archivo)
    plt.close(fig)


def fig_sondeo(sondeo: pd.DataFrame, paneles: list[tuple[str, str, str]], casos: dict, archivo: str,
               figsize=None):
    import matplotlib.pyplot as plt
    ids = list(casos)
    figsize = figsize or (3.0 * len(paneles) + 1.4, 0.3 * len(ids) + 1.4)
    fig, axes = plt.subplots(1, len(paneles), figsize=figsize, sharey=True)
    for k, (ax, (prompt, ctx, titulo)) in enumerate(zip(axes, paneles)):
        ax.set_xlim(0, 1)
        ax.set_ylim(len(ids) - 0.5, -0.5)
        g.limpiar_ejes(ax, grilla=None)
        ax.spines["left"].set_visible(False)
        for i, cid in enumerate(ids):
            s = sondeo[(sondeo["prompt"] == prompt) & (sondeo["contexto"] == ctx) & (sondeo["id"] == cid)]
            if not len(s):
                continue
            p = s["p_etiqueta_normalizada"].iloc[0]
            izq = 0.0
            for lab in ["bajo", "medio", "alto"]:
                ancho = p[lab]
                ax.barh(i, max(ancho - 0.006, 0), left=izq + 0.003, height=0.62, color=g.RIESGO_COLOR[lab], linewidth=0)
                izq += ancho
        ax.set_title(titulo, fontsize=10, pad=6)
        ax.set_xticks([0, 0.5, 1], ["0", "0.5", "1"])
        if k == 0:
            ax.set_yticks(range(len(ids)), [f"{c} ({casos[c]['gold_riesgo']})" for c in ids], fontsize=8.5)
    from matplotlib.patches import Patch
    fig.suptitle("p(etiqueta) leída de los logits en la posición de \"riesgo\" (T = 1)", x=0.02, ha="left",
                 fontsize=11, fontweight="semibold", color=g.TINTA)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.legend(handles=[Patch(facecolor=g.RIESGO_COLOR[l], label=l) for l in ("bajo", "medio", "alto")],
               loc="upper right", ncol=3, frameon=False, fontsize=9, labelcolor=g.TINTA_2,
               handlelength=1.0, handleheight=1.0, bbox_to_anchor=(0.99, 1.0))
    fig.savefig(FIGS_DIR / archivo)
    plt.close(fig)


def fig_exp3(t: pd.DataFrame, archivo: str):
    import matplotlib.pyplot as plt
    ids = list(t.index)
    fig, ax = plt.subplots(figsize=(6.6, 0.34 * len(ids) + 1.2))
    ax.set_xlim(0, 5.6)
    ax.set_ylim(len(ids) - 0.5, -0.5)
    g.limpiar_ejes(ax, grilla=None)
    orden = ["bajo", "medio", "alto", "schema✗", "json✗"]
    for i, cid in enumerate(ids):
        cnt = Counter(t.loc[cid, "sampling"].split())
        izq = 0
        for lab in orden:
            n = cnt.get(lab, 0)
            if n:
                color = g.RIESGO_COLOR.get(lab, g.NEUTRO)
                ax.barh(i, n - 0.06, left=izq + 0.03, height=0.62, color=color, linewidth=0)
                izq += n
        ax.text(5.1, i, t.loc[cid, "greedy"], va="center", fontsize=8.5, color=g.TINTA_2)
    ax.text(5.1, -0.95, "greedy", fontsize=8.5, color=g.TINTA, fontweight="semibold", va="center")
    ax.set_yticks(range(len(ids)), [f"{c} ({t.loc[c, 'gold']})" for c in ids], fontsize=8.5)
    ax.set_xticks(range(0, 6), [str(k) for k in range(0, 6)])
    ax.set_xlabel("Generaciones con sampling (T = 0.8, top-p = 0.9, 5 semillas)")
    ax.set_title("Etiqueta obtenida en cada muestra vs. greedy", pad=18)
    g.leyenda(ax, [("bajo", g.RIESGO_COLOR["bajo"]), ("medio", g.RIESGO_COLOR["medio"]),
                   ("alto", g.RIESGO_COLOR["alto"]), ("inválido", g.NEUTRO)], loc="lower left")
    ax.legend_.set_bbox_to_anchor((0.0, -0.42))
    ax.legend_._ncols = 4
    fig.savefig(FIGS_DIR / archivo)
    plt.close(fig)


def main():
    casos = {c["id"]: c for c in leer_jsonl(CASOS_PATH)}
    for c in casos.values():
        corto = re.sub(r"^(ADQUISICI[ÓO]N|Adquisici[óo]n|CONTRATACI[ÓO]N|Contrataci[óo]n|SERVICIO|Servicio)( ANUAL)? (DE|del|DEL|de) ",
                       "", c["requerimiento"])
        c["corto"] = (corto[:34] + "…") if len(corto) > 35 else corto

    datos = {e: pd.DataFrame(leer_jsonl(RESULTS_DIR / f"{e}.jsonl")) for e in EXPS if (RESULTS_DIR / f"{e}.jsonl").exists()}
    sondeo = pd.DataFrame(leer_jsonl(RESULTS_DIR / "sondeo_logits.jsonl")) if (RESULTS_DIR / "sondeo_logits.jsonl").exists() else None
    kv = json.loads((RESULTS_DIR / "kv_cache.json").read_text(encoding="utf-8")) if (RESULTS_DIR / "kv_cache.json").exists() else None

    M = {}
    md = ["# Resumen de experimentos", "",
          "Generado por `src/reporte.py` a partir de `results/*.jsonl`. Todas las métricas son sobre 10 casos "
          "(Exp. 3: 10 casos × 5 semillas en sampling).", ""]
    cols_m = ["condicion", "n", "json_exacto_rate", "schema_valid_rate", "accuracy", "macro_f1", "senal_accuracy",
              "coherencia_rate", "evidencia_literal_rate", "confianza_media", "prompt_tokens_medio",
              "latencia_media_s", "distribucion_pred"]

    for e, df in datos.items():
        M[e] = {cond: metricas(grp) for cond, grp in df.groupby("condicion", sort=False)}
        md += [f"## {e}", "", tabla_md([{"condicion": k, **v} for k, v in M[e].items()], cols_m), ""]

    matriz = {}
    if "exp1_prompt" in datos:
        t1 = por_caso(datos["exp1_prompt"], "P0", "P1")
        md += ["### Exp. 1 por caso", "", df_md(t1.reset_index()), ""]
        M["exp1_prompt"]["por_caso"] = t1.reset_index().to_dict("records")
        fig_metricas(M["exp1_prompt"]["P0"], M["exp1_prompt"]["P1"], "P0 baseline", "P1 con criterios",
                     "Exp. 1 · Prompt baseline vs prompt con criterios (C0, greedy)", "exp1_metricas.png")
        matriz["P0"] = t1["P0"].to_dict()
        matriz["P1"] = t1["P1"].to_dict()
    if "exp2_contexto" in datos:
        t2 = por_caso(datos["exp2_contexto"], "C0", "C1")
        t2["direccion_senal"] = [casos[i]["direccion_senal_C1"] for i in t2.index]
        ord_ = lambda v: ORDEN_RIESGO.get(v)
        t2["hacia_la_senal"] = [
            None if ord_(a) is None or ord_(b) is None else int(np.sign((ord_(b) - ord_(a)) * d))
            for a, b, d in zip(t2["C0"], t2["C1"], t2["direccion_senal"])]
        md += ["### Exp. 2 por caso", "", df_md(t2.reset_index()), ""]
        M["exp2_contexto"]["por_caso"] = t2.reset_index().to_dict("records")
        fig_metricas(M["exp2_contexto"]["C0"], M["exp2_contexto"]["C1"], "C0 contexto base", "C1 contexto conflictivo",
                     "Exp. 2 · Contexto base vs contexto con resultado OCDS (P1, greedy)", "exp2_metricas.png")
        matriz["C1"] = t2["C1"].to_dict()
        if sondeo is not None:
            dz = desplazamiento_contexto(sondeo, casos)
            md += ["### Exp. 2 · desplazamiento en probabilidad (sondeo de logits)", "",
                   "E[riesgo] = 0·p(bajo) + 1·p(medio) + 2·p(alto). `hacia_la_senal` > 0 significa que C1 movió "
                   "la distribución en la dirección que sugiere el resultado del proceso.", "",
                   df_md(dz.reset_index()), ""]
            M["exp2_contexto"]["desplazamiento_logits"] = dz.reset_index().to_dict("records")
            M["exp2_contexto"]["desplazamiento_medio_hacia_senal"] = round(dz["hacia_la_senal"].mean(), 4)
    if "exp4_fewshot" in datos:
        t4 = por_caso(datos["exp4_fewshot"], "F0_zeroshot", "F1_fewshot")
        md += ["### Exp. 4 (opcional) por caso", "", df_md(t4.reset_index()), ""]
        M["exp4_fewshot"]["por_caso"] = t4.reset_index().to_dict("records")
        fig_metricas(M["exp4_fewshot"]["F0_zeroshot"], M["exp4_fewshot"]["F1_fewshot"], "F0 zero-shot", "F1 few-shot",
                     "Exp. 4 (opcional) · Zero-shot vs 2 ejemplos (P1, C0, greedy)", "exp4_metricas.png")
        matriz["F1"] = t4["F1_fewshot"].to_dict()
    if "exp3_decoding" in datos:
        t3, agg3 = resumen_exp3(datos["exp3_decoding"], sondeo)
        M["exp3_decoding"]["por_caso"] = t3.reset_index().to_dict("records")
        M["exp3_decoding"]["agregado"] = agg3
        md += ["### Exp. 3 por caso", "", df_md(t3.reset_index()), "",
               "### Exp. 3 agregado", "", "```json", json.dumps(agg3, indent=2, ensure_ascii=False), "```", ""]
        fig_exp3(t3, "exp3_estabilidad.png")
        d3 = datos["exp3_decoding"]
        g3 = d3[d3["condicion"] == "D0_greedy"]
        cols3 = {"Greedy": {r["id"]: etiqueta_corta(r) for _, r in g3[g3["seed"] == g3["seed"].min()].iterrows()}}
        for seed, grp in d3[d3["condicion"] == "D1_sampling"].groupby("seed"):
            cols3[f"Semilla {seed}"] = {r["id"]: etiqueta_corta(r) for _, r in grp.iterrows()}
        fig_matriz(cols3, casos, "exp3_semillas.png")
    if matriz:
        fig_matriz(matriz, casos, "matriz_etiquetas.png")
        fig_matriz_compacta(matriz, casos, "matriz_etiquetas_compacta.png")
    if sondeo is not None:
        fig_sondeo(sondeo, [("P0", "C0", "P0 · C0"), ("P1", "C0", "P1 · C0"), ("P1", "C1", "P1 · C1"),
                            ("F1", "C0", "F1 · C0")], casos, "sondeo_probabilidades.png")
        fig_sondeo(sondeo, [("P0", "C0", "P0 (baseline)"), ("P1", "C0", "P1 (con criterios)")], casos,
                   "sondeo_p0_p1.png", figsize=(7.2, 3.5))
        tabla_s = sondeo[["prompt", "contexto", "id", "gold_riesgo", "p_etiqueta_normalizada", "margen_top1_top2",
                          "p_primer_token_T1.0", "p_primer_token_T0.8"]]
        md += ["## Sondeo de logits", "", df_md(tabla_s), ""]
        M["sondeo"] = tabla_s.to_dict("records")
    if kv is not None:
        M["kv_cache"] = {k: v for k, v in kv.items() if k not in ("con_cache", "sin_cache")} | {
            "ms_con_cache": kv["con_cache"]["ms"], "ms_sin_cache": kv["sin_cache"]["ms"]}
        md += ["## KV cache", "", "```json", json.dumps(M["kv_cache"], indent=2, ensure_ascii=False), "```", ""]

    (RESULTS_DIR / "metricas.json").write_text(json.dumps(M, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    (RESULTS_DIR / "resumen_experimentos.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md)[:12000])


if __name__ == "__main__":
    main()
