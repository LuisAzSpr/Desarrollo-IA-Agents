"""Perfil del negocio y verificación del esquema OCDS.

Uso:
    python src/perfil_datos.py

Salidas:
    results/perfil_datos.json   métricas de integridad y de negocio
    results/perfil_datos.md     resumen legible
    results/figs/perfil_*.png   figuras para README y diapositivas
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

from config import FIGS_DIR, OCDS_DIR, RESULTS_DIR
from ocds import ESQUEMA, leer
import graficos as g

COLUMNAS_CLAVE = {
    "main": ["id"], "sources": ["main_id"],
    "parties": ["main_id", "id", "roles"],
    "parties_additionalIdentifiers": ["main_id", "parties_id"],
    "tender_documents": ["main_id", "id", "title", "documentType"],
    "tender_items": ["main_id", "id", "statusDetails"],
    "tender_items_additionalClassifications": ["main_id", "tender_items_id"],
    "tender_items_totalValue_exchangeRates": ["main_id", "tender_items_id"],
    "tender_tenderers": ["main_id", "id", "name"],
    "awards": ["main_id", "id", "value_amount", "value_currency"],
    "awards_suppliers": ["main_id", "awards_id", "id", "name"],
    "awards_items": ["main_id", "awards_id"],
    "awards_items_additionalClassifications": ["main_id", "awards_id"],
    "awards_items_totalValue_exchangeRates": ["main_id", "awards_id"],
    "awards_value_exchangeRates": ["main_id", "awards_id"],
    "contracts": ["main_id", "id", "awardID"],
    "contracts_documents": ["main_id", "contracts_id"],
    "contracts_items": ["main_id", "contracts_id"],
    "contracts_items_additionalClassifications": ["main_id", "contracts_id"],
    "contracts_items_totalValue_exchangeRates": ["main_id", "contracts_id"],
    "contracts_value_exchangeRates": ["main_id", "contracts_id"],
}

MAIN_COLS = ["id", "ocid", "buyer_id", "buyer_name", "tender_procurementMethodDetails",
             "tender_mainProcurementCategory", "tender_numberOfTenderers", "tender_value_amount_PEN",
             "tender_datePublished"]


def integridad(tablas: dict) -> dict:
    out = {}
    for nombre, (pk, fks) in ESQUEMA.items():
        df = tablas[nombre]
        info = {"filas": int(len(df))}
        if pk:
            info["pk"] = pk
            info["pk_unica"] = bool(not df.duplicated(pk).any())
        info["fk"] = []
        for cols, padre, pcols in fks:
            hijo = pd.MultiIndex.from_frame(df[cols].astype(str))
            ref = pd.MultiIndex.from_frame(tablas[padre][pcols].astype(str))
            cobertura = float(hijo.isin(ref).mean()) if len(df) else float("nan")
            info["fk"].append({"columnas": cols, "referencia": f"{padre}({', '.join(pcols)})",
                               "cobertura": round(cobertura, 4)})
        out[nombre] = info
    return out


def perfil_negocio(t: dict) -> dict:
    main = t["main"]
    n = len(main)
    fechas = pd.to_datetime(main["tender_datePublished"].str[:10], errors="coerce")
    nt = main["tender_numberOfTenderers"]

    # Adjudicaciones y ganadores (join por main_id + id: los ids no son globales).
    aw = t["awards"]
    sup = t["awards_suppliers"]
    ganes = aw.merge(sup, left_on=["main_id", "id"], right_on=["main_id", "awards_id"],
                     suffixes=("_award", "_prov"))
    con_award = set(aw["main_id"])
    adjudicados = main[main["id"].isin(con_award)]

    # Postor único por procedimiento (procesos adjudicados con dato de postores).
    base_pu = adjudicados[adjudicados["tender_numberOfTenderers"].notna()]
    por_metodo = (base_pu.groupby("tender_procurementMethodDetails")["tender_numberOfTenderers"]
                  .agg(n="size", postor_unico=lambda s: float((s == 1).mean()))
                  .query("n >= 1000").sort_values("n", ascending=False).head(10))
    por_categoria = (base_pu.groupby("tender_mainProcurementCategory")["tender_numberOfTenderers"]
                     .agg(n="size", postor_unico=lambda s: float((s == 1).mean())))

    # Monto adjudicado (PEN) / valor referencial.
    aw_pen = aw[aw["value_currency"] == "PEN"].groupby("main_id")["value_amount"].sum()
    ref = main.set_index("id")["tender_value_amount_PEN"]
    ratio = (aw_pen / ref.reindex(aw_pen.index)).replace([np.inf, -np.inf], np.nan)
    ratio = ratio[(ref.reindex(aw_pen.index) > 0)].dropna()

    # Documentos de la convocatoria.
    docs = t["tender_documents"]
    procesos_con = lambda titulo: float(docs.loc[docs["title"] == titulo, "main_id"].nunique() / n)

    # Participación y éxito de proveedores.
    tt = t["tender_tenderers"]
    participaciones = tt.groupby(["id", "name"]).size().sort_values(ascending=False)
    victorias = ganes.groupby(["id_prov", "name"])["main_id"].nunique().sort_values(ascending=False)
    monto_ganado = (ganes[ganes["value_currency"] == "PEN"].groupby(["id_prov", "name"])["value_amount"]
                    .sum().sort_values(ascending=False))
    k_tt = pd.MultiIndex.from_frame(tt[["main_id", "id"]])
    ganador_es_postor = float(pd.MultiIndex.from_frame(sup[["main_id", "id"]]).isin(k_tt).mean())
    coincide_n = main.set_index("id")["tender_numberOfTenderers"].to_frame().join(
        tt.groupby("main_id").size().rename("n_tt"))
    coincide_n = coincide_n.dropna()

    items = t["tender_items"]
    return {
        "procesos": n,
        "entidades": int(main["buyer_id"].nunique()),
        "convocatorias_desde": str(fechas.min().date()),
        "convocatorias_hasta": str(fechas.max().date()),
        "procesos_2025_2026": int(fechas.dt.year.isin([2025, 2026]).sum()),
        "por_categoria": main["tender_mainProcurementCategory"].value_counts().to_dict(),
        "valor_referencial_pen_por_categoria": main.groupby("tender_mainProcurementCategory")[
            "tender_value_amount_PEN"].sum().round(0).to_dict(),
        "top_procedimientos": main["tender_procurementMethodDetails"].value_counts().head(10).to_dict(),
        "top_entidades": main["buyer_name"].value_counts().head(10).to_dict(),
        "documentos_por_tipo": docs["title"].value_counts().to_dict(),
        "procesos_con_bases_administrativas": round(procesos_con("Bases Administrativas"), 4),
        "procesos_con_bases_integradas": round(procesos_con("Bases Integradas"), 4),
        "procesos_con_pliego_absolucion": round(procesos_con("Pliego de absolución de consultas y observaciones"), 4),
        "postores_con_dato": int(nt.notna().sum()),
        "postores_mediana": float(nt.median()),
        "postores_distribucion": {str(k): int(v) for k, v in pd.cut(
            nt.dropna(), [0, 1, 2, 3, 5, 10, 20, 1000],
            labels=["1", "2", "3", "4-5", "6-10", "11-20", "21+"]).value_counts().sort_index().items()},
        "tasa_postor_unico_con_dato": round(float((nt.dropna() == 1).mean()), 4),
        "tasa_postor_unico_adjudicados": round(float((base_pu["tender_numberOfTenderers"] == 1).mean()), 4),
        "postor_unico_por_metodo": por_metodo.round(4).reset_index().to_dict("records"),
        "postor_unico_por_categoria": por_categoria.round(4).reset_index().to_dict("records"),
        "n_numberOfTenderers_igual_conteo_tenderers": round(float((coincide_n.iloc[:, 0] == coincide_n["n_tt"]).mean()), 4),
        "procesos_adjudicados": int(len(con_award)),
        "adjudicaciones": int(len(aw)),
        "contratos": int(len(t["contracts"])),
        "proveedores_distintos_que_participaron": int(tt["id"].nunique()),
        "proveedores_distintos_ganadores": int(sup["id"].nunique()),
        "ganador_figura_entre_postores": round(ganador_es_postor, 4),
        "top_participantes": [{"ruc": i[0], "nombre": i[1], "procesos": int(v)} for i, v in participaciones.head(10).items()],
        "top_ganadores_por_procesos": [{"ruc": i[0], "nombre": i[1], "procesos": int(v)} for i, v in victorias.head(10).items()],
        "top_ganadores_por_monto_pen": [{"ruc": i[0], "nombre": i[1], "monto": float(round(v, 0))} for i, v in monto_ganado.head(10).items()],
        "ratio_adjudicado_referencial": {
            "n": int(len(ratio)), "mediana": round(float(ratio.median()), 4),
            "p_entre_0.99_y_1.00": round(float(ratio.between(0.99, 1.0).mean()), 4),
            "p_mayor_1": round(float((ratio > 1.0001).mean()), 4),
        },
        "estado_items": items["statusDetails"].value_counts(normalize=True).round(4).head(8).to_dict(),
        "_ratio_serie": ratio,  # solo para la figura
        "_por_metodo": por_metodo,
    }


def figuras(p: dict):
    FIGS_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Distribución del número de postores.
    dist = p["postores_distribucion"]
    etiquetas = list(dist)
    vals = [dist[k] / 1000 for k in etiquetas]
    fig, ax = plt_subplots(6.4, 3.2)
    ax.set_xlim(-0.6, len(etiquetas) - 0.4)
    ax.set_ylim(0, max(vals) * 1.18)
    g.limpiar_ejes(ax)
    colores = [g.SERIE_2 if k == "1" else g.SERIE_1 for k in etiquetas]
    for i, (v, c) in enumerate(zip(vals, colores)):
        g.barras(ax, [i], [v], 0.55, c)
        ax.text(i, v + max(vals) * 0.02, f"{v:.1f}k", ha="center", va="bottom", fontsize=9, color=g.TINTA_2)
    ax.set_xticks(range(len(etiquetas)), etiquetas)
    ax.set_xlabel("Número de postores registrados en el proceso")
    ax.set_ylabel("Procesos (miles)")
    ax.set_title(f"{p['tasa_postor_unico_con_dato']:.0%} de los procesos con dato tuvo un solo postor "
                 f"(n = {p['postores_con_dato']:,})".replace(",", " "), pad=10)
    fig.savefig(FIGS_DIR / "perfil_postores.png")

    # 2) Postor único por procedimiento.
    pm = p["_por_metodo"].sort_values("postor_unico")
    fig, ax = plt_subplots(6.4, 3.6)
    ax.set_xlim(0, max(pm["postor_unico"]) * 100 * 1.18)
    ax.set_ylim(-0.6, len(pm) - 0.4)
    g.limpiar_ejes(ax, grilla="x")
    g.barras(ax, range(len(pm)), (pm["postor_unico"] * 100).tolist(), 0.55, g.SERIE_1, horizontal=True)
    for i, v in enumerate(pm["postor_unico"] * 100):
        ax.text(v + 0.6, i, f"{v:.0f}%", va="center", fontsize=9, color=g.TINTA_2)
    ax.set_yticks(range(len(pm)), pm.index)
    ax.set_xlabel("% de procesos adjudicados con un solo postor")
    ax.set_title("Postor único según tipo de procedimiento (≥1 000 procesos)", pad=10)
    fig.savefig(FIGS_DIR / "perfil_postor_unico_metodo.png")


def plt_subplots(w, h):
    import matplotlib.pyplot as plt
    return plt.subplots(figsize=(w, h))


def a_markdown(integ: dict, p: dict) -> str:
    L = ["# Perfil de los datos OCDS (SEACE)", "", f"Fuente: `{OCDS_DIR}`", "",
         "## Integridad del esquema", "", "| Tabla | Filas | PK | PK única | FK -> referencia (cobertura) |",
         "|---|---:|---|---|---|"]
    for nombre, info in integ.items():
        fks = "<br>".join(f"{', '.join(f['columnas'])} -> {f['referencia']} ({f['cobertura']:.1%})" for f in info["fk"]) or "-"
        pk = ", ".join(info.get("pk", [])) or "-"
        L.append(f"| {nombre} | {info['filas']:,} | {pk} | {info.get('pk_unica', '-')} | {fks} |")
    L += ["", "## Negocio", ""]
    for k, v in p.items():
        if k.startswith("_"):
            continue
        L.append(f"- **{k}**: {json.dumps(v, ensure_ascii=False, default=str)}")
    return "\n".join(L) + "\n"


def main():
    tablas = {}
    for nombre in ESQUEMA:
        cols = MAIN_COLS if nombre == "main" else COLUMNAS_CLAVE[nombre]
        tablas[nombre] = leer(nombre, usecols=cols)
        print(f"{nombre:45s} {len(tablas[nombre]):>9,}")
    integ = integridad(tablas)
    p = perfil_negocio(tablas)
    figuras(p)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    limpio = {k: v for k, v in p.items() if not k.startswith("_")}
    (RESULTS_DIR / "perfil_datos.json").write_text(
        json.dumps({"integridad": integ, "negocio": limpio}, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    (RESULTS_DIR / "perfil_datos.md").write_text(a_markdown(integ, p), encoding="utf-8")
    print(json.dumps(limpio, indent=2, ensure_ascii=False, default=str)[:6000])


if __name__ == "__main__":
    main()
