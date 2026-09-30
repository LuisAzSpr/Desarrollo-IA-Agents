"""Ejecuta los experimentos de la PC1 y guarda cada generación.

Uso:
    python src/experimentos.py                 # todo (exp1, exp2, exp3, exp4, sondeo, kv)
    python src/experimentos.py --solo exp1     # uno solo
    python src/experimentos.py --casos C01,C05 # prueba rápida con algunos casos

Condición = (prompt, contexto, política de decoding, semilla). Cada experimento
cambia UNA de esas variables y deja fijas las demás.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

from config import (CACHE_PATH, CASOS_PATH, DECODING, MAX_NEW_TOKENS, MODEL_ID, PROMPTS_DIR,
                    RESULTS_DIR, SAMPLING_SEEDS, SCHEMA_PATH, SEED)
import llm
from prompts import mensajes
from validacion import evaluar

EXPERIMENTOS = {
    # nombre: [(etiqueta de condición, prompt, contexto, política, semillas)]
    "exp1_prompt": [("P0", "P0", "C0", "greedy", [SEED]),
                    ("P1", "P1", "C0", "greedy", [SEED])],
    "exp2_contexto": [("C0", "P1", "C0", "greedy", [SEED]),
                      ("C1", "P1", "C1", "greedy", [SEED])],
    "exp3_decoding": [("D0_greedy", "P1", "C0", "greedy", [SEED, SEED + 1]),
                      ("D1_sampling", "P1", "C0", "sampling", SAMPLING_SEEDS)],
    "exp4_fewshot": [("F0_zeroshot", "P1", "C0", "greedy", [SEED]),
                     ("F1_fewshot", "F1", "C0", "greedy", [SEED])],
}
SONDEO = [("P0", "C0"), ("P1", "C0"), ("P1", "C1"), ("F1", "C0")]


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def sha_archivo(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cargar_cache() -> dict:
    cache = {}
    if CACHE_PATH.exists():
        for linea in CACHE_PATH.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                d = json.loads(linea)
                cache[d["key"]] = d["gen"]
    return cache


def generar_con_cache(cache, msgs, politica, seed) -> dict:
    # En greedy la semilla no cambia el resultado, pero se incluye en la clave
    # para poder repetir la corrida y comprobar el determinismo.
    key = sha({"model": MODEL_ID, "rev": llm.MODEL_REVISION, "msgs": msgs,
               "decoding": DECODING[politica], "seed": seed})
    if key not in cache:
        gen = llm.generar(msgs, politica, seed)
        cache[key] = gen
        with CACHE_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"key": key, "gen": gen}, ensure_ascii=False) + "\n")
    return {**cache[key], "cache_key": key}


def guardar_prompt(prompt, contexto, caso, msgs):
    d = RESULTS_DIR / "prompts_renderizados"
    d.mkdir(parents=True, exist_ok=True)
    texto = "\n\n".join(f"<<{m['role']}>>\n{m['content']}" for m in msgs)
    (d / f"{prompt}_{contexto}_{caso['id']}.txt").write_text(texto, encoding="utf-8")


def correr(nombre, condiciones, casos, cache):
    filas = []
    total = sum(len(s) for *_, s in condiciones) * len(casos)
    paso = 0
    for etiqueta, prompt, contexto, politica, semillas in condiciones:
        for caso in casos:
            msgs = mensajes(prompt, caso, contexto)
            guardar_prompt(prompt, contexto, caso, msgs)
            for seed in semillas:
                paso += 1
                gen = generar_con_cache(cache, msgs, politica, seed)
                ev = evaluar(gen["raw_text"], caso)
                filas.append({
                    "experimento": nombre, "condicion": etiqueta, "prompt": prompt, "contexto": contexto,
                    "politica": politica, "seed": seed, "id": caso["id"], "gold_riesgo": caso["gold_riesgo"],
                    "gold_senales": caso["gold_senales"], "dificultad": caso["dificultad"],
                    "direccion_senal_C1": caso["direccion_senal_C1"], "prompt_sha": sha(msgs)[:16],
                    **gen, **ev,
                })
                print(f"[{nombre} {paso:03d}/{total:03d}] {etiqueta:12s} {caso['id']} seed={seed} "
                      f"-> {ev['pred_riesgo']!s:6s} ({ev['estado']}) {gen['latency_ms'] / 1000:.1f}s", flush=True)
    with (RESULTS_DIR / f"{nombre}.jsonl").open("w", encoding="utf-8") as f:
        for fila in filas:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")
    return filas


def correr_sondeo(casos):
    filas = []
    for prompt, contexto in SONDEO:
        for caso in casos:
            s = llm.sondear_etiqueta(mensajes(prompt, caso, contexto))
            filas.append({"prompt": prompt, "contexto": contexto, "id": caso["id"],
                          "gold_riesgo": caso["gold_riesgo"], **s})
            p = s["p_etiqueta_normalizada"]
            print(f"[sondeo] {prompt}/{contexto} {caso['id']} alto={p['alto']:.2f} medio={p['medio']:.2f} "
                  f"bajo={p['bajo']:.2f}", flush=True)
    with (RESULTS_DIR / "sondeo_logits.jsonl").open("w", encoding="utf-8") as f:
        for fila in filas:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def correr_kv(casos):
    caso = next(c for c in casos if c["id"] == "C05") if any(c["id"] == "C05" for c in casos) else casos[0]
    r = {"caso": caso["id"], "prompt": "P1", "contexto": "C0", **llm.medir_kv_cache(mensajes("P1", caso, "C0"))}
    (RESULTS_DIR / "kv_cache.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[kv] con cache {r['con_cache']['ms']:.0f} ms | sin cache {r['sin_cache']['ms']:.0f} ms | "
          f"x{r['aceleracion']} | mismo texto: {r['mismo_texto']}", flush=True)


def guardar_config(casos):
    import torch
    import transformers
    cfg = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "modelo": MODEL_ID,
        "revision": llm.revision_resuelta(),
        "dtype": llm.DTYPE,
        "device": "cpu",
        "torch_threads": torch.get_num_threads(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "python": platform.python_version(),
        "plataforma": platform.platform(),
        "max_new_tokens": MAX_NEW_TOKENS,
        "decoding": DECODING,
        "semilla_base": SEED,
        "semillas_sampling": SAMPLING_SEEDS,
        "experimentos": {k: [c[:4] + (list(c[4]),) for c in v] for k, v in EXPERIMENTOS.items()},
        "casos": [c["id"] for c in casos],
        "sha256_casos": sha_archivo(CASOS_PATH),
        "sha256_schema": sha_archivo(SCHEMA_PATH),
        "sha256_prompts": {p.name: sha_archivo(p) for p in sorted(PROMPTS_DIR.glob("*.txt"))},
    }
    (RESULTS_DIR / "run_config.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", help="exp1 | exp2 | exp3 | exp4 | sondeo | kv")
    ap.add_argument("--casos", help="ids separados por coma")
    args = ap.parse_args()
    corre = lambda nombre: args.solo is None or nombre.startswith(args.solo)

    casos = [json.loads(l) for l in CASOS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.casos:
        ids = set(args.casos.split(","))
        casos = [c for c in casos if c["id"] in ids]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    cache = cargar_cache()
    llm.cargar()
    if not args.casos:
        guardar_config(casos)

    for nombre, condiciones in EXPERIMENTOS.items():
        if corre(nombre):
            correr(nombre, condiciones, casos, cache)
    if corre("sondeo"):
        correr_sondeo(casos)
    if corre("kv"):
        correr_kv(casos)


if __name__ == "__main__":
    main()
