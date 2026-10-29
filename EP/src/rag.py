"""Generacion RAG y closed-book con el mismo LLM, prompt y decoding.

El contexto RAG son las RAG_TOP_K primeras unidades de la condicion C del
experimento 1 (ya guardadas en results/exp1/rankings.jsonl). En closed-book el
mismo prompt recibe un contexto vacio. Asi lo unico que cambia entre las dos
condiciones es la evidencia.
"""
from __future__ import annotations

import hashlib
import json

import config_ep as C
import llm  # src/llm.py de la PC1 (carga Qwen y aplica greedy sin el generation_config del modelo)
from config import DECODING, MODELOS  # src/config.py de la PC1
from recuperacion import unidades_pasaje
from validacion import parse_exacto, recuperar_objeto  # parseo en dos niveles de la PC1

POLITICA = "greedy"
SIN_PASAJES = "(no se entregan pasajes)"
CACHE = C.RESULTS / "exp2" / "cache_llm.jsonl"


def prompts():
    sistema = (C.PROMPTS / "system_rag.txt").read_text(encoding="utf-8").strip()
    usuario = (C.PROMPTS / "usuario_rag.txt").read_text(encoding="utf-8").strip()
    return sistema, usuario


def rankings(condicion=C.CONDICION_RAG):
    """query_id -> lista de unit_id en el orden de la condicion del experimento 1."""
    out = {}
    for l in (C.RESULTS / "exp1" / "rankings.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(l)
        if r["condicion"] == condicion:
            out[r["query_id"]] = [uid for uid, _ in r["unidades"]]
    return out


def contexto(unit_ids, unidades_por_id, k=C.RAG_TOP_K):
    """Bloques '[passage_id] encabezado + texto'. En A/B/C la unidad es un pasaje."""
    bloques = [f"[{uid}] {unidades_por_id[uid]['text']}" for uid in unit_ids[:k]]
    return "\n\n".join(bloques) if bloques else SIN_PASAJES


def mensajes(pregunta, ctx):
    sistema, usuario = prompts()
    return [{"role": "system", "content": sistema},
            {"role": "user", "content": usuario.replace("{pregunta}", pregunta).replace("{contexto}", ctx)}]


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _leer_cache():
    cache = {}
    if CACHE.exists():
        for l in CACHE.read_text(encoding="utf-8").splitlines():
            if l.strip():
                d = json.loads(l)
                cache[d["key"]] = d["gen"]
    return cache


def generar(msgs, seed=C.SEED):
    """Generacion greedy con cache en disco (clave: modelo, revision, mensajes, decoding y semilla)."""
    model_id, revision = MODELOS[C.LLM]
    key = _sha({"model": model_id, "rev": revision, "msgs": msgs, "decoding": DECODING[POLITICA], "seed": seed})
    cache = _leer_cache()
    if key not in cache:
        gen = llm.generar(msgs, POLITICA, seed, modelo=C.LLM)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        with CACHE.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"key": key, "gen": gen}, ensure_ascii=False) + "\n")
        return {**gen, "cache_key": key, "desde_cache": False}
    return {**cache[key], "cache_key": key, "desde_cache": True}


def parsear(raw):
    """JSON exacto o recuperado del texto; revisa que los tres campos tengan el tipo esperado."""
    exacto = parse_exacto(raw)
    obj = exacto if exacto is not None else recuperar_objeto(raw)
    r = {"json_exacto": exacto is not None, "json_ok": obj is not None,
         "respuesta": None, "citas": [], "abstencion": None, "formato_ok": False}
    if obj is None:
        return r
    respuesta, citas, abst = obj.get("respuesta"), obj.get("citas"), obj.get("abstencion")
    r["respuesta"] = respuesta if isinstance(respuesta, str) else None
    r["citas"] = [str(c).strip("[] ") for c in citas] if isinstance(citas, list) else []
    r["abstencion"] = abst if isinstance(abst, bool) else None
    r["formato_ok"] = (isinstance(respuesta, str) and isinstance(citas, list) and isinstance(abst, bool))
    return r


def metricas_citas(citas, ids_contexto, relevantes):
    """Citas dentro del contexto entregado y citas que apuntan a un pasaje relevante (qrels).

    Adaptado de citation_metrics del Cuaderno 7. Sin citas las tasas quedan en
    None (no en 0) para no mezclar 'no cito' con 'cito mal'.
    """
    citas = list(dict.fromkeys(citas))
    en_ctx = [c for c in citas if c in set(ids_contexto)]
    soporte = [c for c in en_ctx if c in set(relevantes)]
    n = len(citas)
    return {"n_citas": n, "citas_en_contexto": len(en_ctx), "citas_con_soporte": len(soporte),
            "tasa_en_contexto": len(en_ctx) / n if n else None,
            "tasa_soporte": len(soporte) / n if n else None,
            "relevantes_en_contexto": len(set(relevantes) & set(ids_contexto)),
            "relevantes_citados": len(set(relevantes) & set(citas))}


def unidades(docs):
    return {u["unit_id"]: u for u in unidades_pasaje(docs)}


def _pruebas():
    assert parsear('{"respuesta": "x", "citas": ["E01-P02"], "abstencion": false}')["formato_ok"]
    p = parsear('Respuesta: {"respuesta": "x", "citas": "E01-P02", "abstencion": false} fin')
    assert p["json_ok"] and not p["json_exacto"] and not p["formato_ok"] and p["citas"] == []
    m = metricas_citas(["E01-P02", "E09-P01", "E01-P02"], ["E01-P01", "E01-P02"], ["E01-P02"])
    assert (m["n_citas"], m["citas_en_contexto"], m["citas_con_soporte"]) == (2, 1, 1)
    assert metricas_citas([], ["E01-P01"], [])["tasa_soporte"] is None


_pruebas()
