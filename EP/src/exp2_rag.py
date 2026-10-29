"""Experimento 2: closed-book vs RAG (contexto de la condicion C) con el mismo LLM.

Uso:
    python EP/src/exp2_rag.py prueba     revisa el formato con 2 consultas que NO son del exp. 2
    python EP/src/exp2_rag.py            genera las respuestas de las 12 consultas del exp. 2
    python EP/src/exp2_rag.py resumir    junta la salida automatica con la auditoria manual

Fijo: Qwen2.5-1.5B-Instruct (revision fijada), greedy, max_new_tokens 192,
semilla, prompt (EP/prompts) y las 12 consultas marcadas exp2 en consultas.jsonl.
Cambia: el bloque de contexto (vacio vs top-5 de C).

La correccion, las citas y la faithfulness se auditan a mano en
results/exp2/auditoria_respuestas.csv y auditoria_afirmaciones.csv.
Lo automatico (JSON valido, citas dentro del contexto, citas en qrels,
abstencion) solo sirve de apoyo.
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

import benchmark
import config_ep as C
import rag
from config import DECODING, MODELOS

OUT = C.RESULTS / "exp2"
CONDICIONES = ["closed_book", "rag_C"]
CONSULTAS_PRUEBA = ["Q05", "Q16"]  # fuera del exp. 2: solo para revisar el formato antes de correr


def correr(consultas, qrels, refs, unidades, ranks, condiciones):
    filas = []
    for c in consultas:
        qid = c["query_id"]
        for cond in condiciones:
            ids_ctx = ranks[qid][:C.RAG_TOP_K] if cond == "rag_C" else []
            msgs = rag.mensajes(c["query"], rag.contexto(ids_ctx, unidades))
            gen = rag.generar(msgs)
            p = rag.parsear(gen["raw_text"])
            debe = refs[qid]["debe_abstenerse"] if qid in refs else None
            filas.append({"condicion": cond, "query_id": qid, "query": c["query"], "contexto_ids": ids_ctx,
                          **gen, **p, **rag.metricas_citas(p["citas"], ids_ctx, qrels[qid]),
                          "debe_abstenerse": debe,
                          "abstencion_correcta": None if p["abstencion"] is None or debe is None else p["abstencion"] == debe})
            print(f"{qid} {cond:<11} {gen['latency_ms']:>8.0f} ms  json={p['json_ok']}  citas={p['citas']}  "
                  f"abst={p['abstencion']}  {'(cache)' if gen['desde_cache'] else ''}")
    return filas


def guardar(filas, nombre):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / nombre).open("w", encoding="utf-8", newline="\n") as f:
        for r in filas:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def plantillas(filas):
    """Plantillas de auditoria. No se sobreescriben si ya existe la auditoria hecha."""
    resp = OUT / "auditoria_respuestas.csv"
    if not resp.exists():
        pd.DataFrame([{"condicion": r["condicion"], "query_id": r["query_id"], "respuesta": r["respuesta"] or r["raw_text"],
                       "citas": ";".join(r["citas"]), "abstencion": r["abstencion"], "correccion": "",
                       "citas_que_sustentan": "", "nota": ""}
                      for r in filas]).to_csv(resp, index=False, encoding="utf-8")
    afir = OUT / "auditoria_afirmaciones.csv"
    if not afir.exists():
        pd.DataFrame(columns=["condicion", "query_id", "afirmacion", "estado", "pasaje", "cita_correcta", "nota"]
                     ).to_csv(afir, index=False, encoding="utf-8")


def generar_todo(prueba=False):
    sys.stdout.reconfigure(encoding="utf-8")
    congelado = benchmark.verificar_congelado()
    man1 = json.loads((C.RESULTS / "exp1" / "manifiesto.json").read_text(encoding="utf-8"))
    assert man1["benchmark_congelado"]["sha256"] == congelado["sha256"], "rankings del exp. 1 de otro benchmark"
    docs, consultas, qrels, refs = benchmark.cargar()
    unidades, ranks = rag.unidades(docs), rag.rankings(C.CONDICION_RAG)

    if prueba:
        sel = [c for c in consultas if c["query_id"] in CONSULTAS_PRUEBA]
        assert not any(c["exp2"] for c in sel)
        filas = correr(sel, qrels, refs, unidades, ranks, CONDICIONES)
        guardar(filas, "prueba_formato.jsonl")
        for r in filas:
            print(f"\n--- {r['query_id']} {r['condicion']}\n{r['raw_text']}")
        return

    sel = [c for c in consultas if c["exp2"]]
    filas = correr(sel, qrels, refs, unidades, ranks, CONDICIONES)
    guardar(filas, "salidas.jsonl")
    cols = ["condicion", "query_id", "json_exacto", "json_ok", "formato_ok", "abstencion", "debe_abstenerse",
            "abstencion_correcta", "n_citas", "citas_en_contexto", "citas_con_soporte", "relevantes_en_contexto",
            "relevantes_citados", "prompt_tokens", "generated_tokens", "truncado", "latency_ms"]
    pd.DataFrame(filas)[cols].to_csv(OUT / "automatico.csv", index=False)
    plantillas(filas)

    import torch, transformers  # noqa: E401
    sistema, usuario = rag.prompts()
    manifiesto = {
        "experimento": 2, "benchmark_congelado": congelado,
        "contexto": {"condicion_exp1": C.CONDICION_RAG, "rag_top_k": C.RAG_TOP_K},
        "llm": {"modelo": MODELOS[C.LLM], "politica": rag.POLITICA, "decoding": DECODING[rag.POLITICA], "seed": C.SEED},
        "prompts_sha256": {"system_rag.txt": rag._sha(sistema), "usuario_rag.txt": rag._sha(usuario)},
        "consultas": [c["query_id"] for c in sel],
        "versiones": {"torch": torch.__version__, "transformers": transformers.__version__},
    }
    (OUT / "manifiesto.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")


def resumir():
    sys.stdout.reconfigure(encoding="utf-8")
    auto = pd.read_csv(OUT / "automatico.csv")
    resp = pd.read_csv(OUT / "auditoria_respuestas.csv")
    afir = pd.read_csv(OUT / "auditoria_afirmaciones.csv")
    assert resp["correccion"].notna().all(), "falta auditar respuestas"
    # no_responde = se abstuvo aunque la respuesta si estaba en el corpus (no inventa, pero no ayuda)
    validos = {"correcta", "parcial", "incorrecta", "no_responde", "abstencion_correcta"}
    assert set(resp["correccion"]) <= validos, set(resp["correccion"]) - validos
    assert set(afir["estado"]) <= {"sustentada", "no_sustentada", "contradicha"}

    filas = []
    for cond in CONDICIONES:
        a, r, f = auto[auto.condicion == cond], resp[resp.condicion == cond], afir[afir.condicion == cond]
        n_citas = int(a["n_citas"].sum())
        sust = f[f.estado == "sustentada"]
        filas.append({
            "condicion": cond, "consultas": len(a),
            "json_valido": int(a["json_ok"].sum()), "formato_valido": int(a["formato_ok"].sum()),
            "correctas": int((r.correccion == "correcta").sum()), "parciales": int((r.correccion == "parcial").sum()),
            "incorrectas": int((r.correccion == "incorrecta").sum()),
            "no_responde": int((r.correccion == "no_responde").sum()),
            "abstencion_correcta_en_controles": f"{int((r.correccion == 'abstencion_correcta').sum())}/"
                                                f"{int(a['debe_abstenerse'].sum())}",
            "citas_total": n_citas,
            "citas_en_contexto_auto": f"{int(a['citas_en_contexto'].sum())}/{n_citas}",
            "citas_en_qrels_auto": f"{int(a['citas_con_soporte'].sum())}/{n_citas}",
            "citas_que_sustentan_manual": f"{int(r['citas_que_sustentan'].fillna(0).sum())}/{n_citas}",
            "afirmaciones": len(f), "afirmaciones_sustentadas": len(sust),
            "faithfulness": round(len(sust) / len(f), 3) if len(f) else None,
            "respuestas_con_afirmacion_no_sustentada": int(f[f.estado != "sustentada"]["query_id"].nunique()),
            "afirmaciones_sustentadas_con_su_cita": f"{int((sust.cita_correcta == 'si').sum())}/{len(sust)}"
                                                   if cond == "rag_C" else "-",
            "latencia_media_ms": round(a["latency_ms"].mean(), 0),
            "latencia_p95_ms": round(float(np.percentile(a["latency_ms"], 95)), 0),
            "prompt_tokens_medio": round(a["prompt_tokens"].mean(), 0),
        })
    res = pd.DataFrame(filas)
    res.to_csv(OUT / "resumen.csv", index=False)
    print(res.T.to_string())


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    if modo == "resumir":
        resumir()
    else:
        generar_todo(prueba=(modo == "prueba"))
