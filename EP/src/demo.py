"""Demo del examen: consulta -> evidencia -> respuesta con citas -> metrica -> herramienta.

Uso:
    python EP/src/demo.py                 consulta Q10 (por defecto)
    python EP/src/demo.py Q15             otra consulta del benchmark
    python EP/src/demo.py Q12 --en-vivo   recupera con los modelos en vez de leer results/exp1

Por defecto usa los rankings guardados del experimento 1 y la cache del
experimento 2, asi que corre en segundos. Con --en-vivo carga e5, BM25 y el
Cross-Encoder (necesita los modelos descargados) y, si la respuesta no esta en
cache, genera con Qwen2.5-1.5B (~1 minuto en CPU).

La parte de la herramienta es una llamada fija del script con el ocid del
proceso mejor rankeado. No la decide el LLM: no hay agente.
"""
from __future__ import annotations

import json
import sys
import textwrap

import benchmark
import config_ep as C
import herramienta as H
import metricas as M
import rag


def titulo(t):
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    qid = args[0] if args else "Q10"
    benchmark.verificar_congelado()
    docs, consultas, qrels, refs = benchmark.cargar()
    consulta = next(c for c in consultas if c["query_id"] == qid)
    unidades = rag.unidades(docs)

    titulo(f"1. Consulta {qid} ({consulta['tipo']}, {consulta['dificultad']})")
    print(consulta["query"])

    titulo(f"2. Evidencia recuperada (condicion {C.CONDICION_RAG}: denso + BM25 + RRF + Cross-Encoder)")
    if "--en-vivo" in sys.argv:
        from recuperacion import Sistema
        sis = Sistema(docs)
        ranking, t = sis.correr(C.CONDICION_RAG, consulta["query"])
        ids = [u["unit_id"] for u in ranking]
        print(f"latencia: {t['total_ms']:.0f} ms (reranker {t['reranker_ms']:.0f} ms)")
    else:
        ids = rag.rankings(C.CONDICION_RAG)[qid]
    for r, uid in enumerate(ids[:C.RAG_TOP_K], 1):
        marca = "  <- relevante (qrels)" if uid in qrels[qid] else ""
        cabeza, texto = unidades[uid]["text"].split("\n", 1)
        print(f"{r}. [{uid}]{marca} {textwrap.shorten(cabeza, 60)}\n   {textwrap.shorten(texto, 160)}")

    titulo("3. Metrica de recuperacion de esta consulta")
    if qrels[qid]:
        m = M.metricas_consulta(ids, qrels[qid])
        print(f"qrels: {qrels[qid]}")
        print("  ".join(f"{k}={v:.2f}" for k, v in m.items()))
    else:
        print("consulta de control: no tiene pasajes relevantes (no entra en las metricas)")

    titulo("4. Respuesta RAG (Qwen2.5-1.5B, greedy) con citas")
    ctx_ids = ids[:C.RAG_TOP_K]
    gen = rag.generar(rag.mensajes(consulta["query"], rag.contexto(ctx_ids, unidades)))
    p = rag.parsear(gen["raw_text"])
    print(gen["raw_text"])
    mc = rag.metricas_citas(p["citas"], ctx_ids, qrels[qid])
    origen = "cache" if gen["desde_cache"] else f"{gen['latency_ms']:.0f} ms"
    print(f"\nJSON valido: {p['json_ok']} | abstencion: {p['abstencion']} | "
          f"citas en el contexto: {mc['citas_en_contexto']}/{mc['n_citas']} | "
          f"citas en qrels: {mc['citas_con_soporte']}/{mc['n_citas']} | {origen}")
    if qid in refs:
        print(f"referencia: {refs[qid]['reference_answer']}")

    titulo(f"5. Herramienta {H.NOMBRE}")
    ocid = next(d["ocid"] for d in docs if d["doc_id"] == ids[0].split("-")[0])
    for nombre, argumentos, fallo in [
        ("ocid del primer resultado", {"ocid": ocid}, "ninguno"),
        ("entrada invalida (argumento inventado)", {"ocid": ocid, "riesgo": "alto"}, "ninguno"),
        ("fallo transitorio una vez", {"ocid": ocid}, "transitorio_una_vez"),
    ]:
        r = H.llamar(argumentos, "D", fallo)
        res = r["result"]
        print(f"\n-- {nombre}: {json.dumps(argumentos, ensure_ascii=False)}")
        if res["status"] == "ok":
            d = res["data"]
            print(f"ok | {d['nomenclatura']} | postores={d['n_postores']} ratio={d['ratio_adjudicado_vr']} "
                  f"objeto_equiv={d['objeto_dice_equivalente']} item_equiv={d['item_dice_equivalente']} "
                  f"alertas={d['alertas']}")
        else:
            print("error |", json.dumps(res["error"], ensure_ascii=False))
        print("traza:", [(t["intento"], t["status"], t["kind"]) for t in r["traza"]])


if __name__ == "__main__":
    main()
