"""Demostración paso a paso (2 minutos de la exposición).

Ejemplos:
    python src/demo.py --caso C05
    python src/demo.py --caso C08 --contexto C1 --sondeo
    python src/demo.py --texto "ADQUISICIÓN DE EQUIPO DE MICROGOTERO ... PARA EL HOSPITAL REGIONAL CISCO"

Muestra: entrada -> prompt -> respuesta cruda -> JSON -> validación -> resultado guardado.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

from config import CASOS_PATH, DECODING, RESULTS_DIR, SEED
import llm
from prompts import mensajes
from validacion import evaluar


def titulo(t):
    print(f"\n\033[1m== {t} ==\033[0m")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--caso", default="C05")
    ap.add_argument("--texto", help="requerimiento nuevo (sin gold)")
    ap.add_argument("--prompt", default="P1", choices=["P0", "P1", "F1"])
    ap.add_argument("--contexto", default="C0", choices=["C0", "C1"])
    ap.add_argument("--politica", default="greedy", choices=list(DECODING))
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--sondeo", action="store_true", help="muestra p(etiqueta) desde los logits")
    ap.add_argument("--completo", action="store_true", help="imprime el prompt completo")
    args = ap.parse_args()

    casos = {c["id"]: c for c in map(json.loads, CASOS_PATH.read_text(encoding="utf-8").splitlines())}
    if args.texto:
        caso = {"id": "NUEVO", "requerimiento": args.texto, "gold_riesgo": None, "gold_senales": [],
                "contexto_C0": "Sin contexto adicional.", "contexto_C1": "Sin contexto adicional."}
    else:
        caso = casos[args.caso]

    titulo("1. Entrada")
    print("Requerimiento:", caso["requerimiento"])
    if caso.get("ocid"):
        print(f"ocid: {caso['ocid']} | postores: {caso['n_postores']} | ganador: {caso['ganador']}")
        print("Bases:", caso["url_bases"])
        print("Gold:", caso["gold_riesgo"], caso["gold_senales"])

    msgs = mensajes(args.prompt, caso, args.contexto)
    titulo(f"2. Prompt {args.prompt} + contexto {args.contexto} | decoding {args.politica} {DECODING[args.politica]}")
    usuario = msgs[1]["content"]
    print(usuario if args.completo else usuario[:900] + (" [...]" if len(usuario) > 900 else ""))

    titulo("3. Respuesta cruda del modelo")
    gen = llm.generar(msgs, args.politica, args.seed)
    print(gen["raw_text"])
    print(f"[{gen['prompt_tokens']} tokens de prompt, {gen['generated_tokens']} generados, "
          f"{gen['latency_ms'] / 1000:.1f} s]")

    ev = evaluar(gen["raw_text"], caso) if caso["gold_riesgo"] else evaluar(
        gen["raw_text"], {**caso, "gold_riesgo": "-", "gold_senales": []})
    titulo("4. JSON")
    print(json.dumps(ev["parsed"], indent=2, ensure_ascii=False) if ev["parsed"] else "(no se pudo parsear)")

    titulo("5. Validación")
    print(f"JSON exacto: {ev['json_exacto']} | parseable (recuperado): {ev['json_recuperado']}")
    print(f"Schema-valid: {ev['schema_valid']} {ev['errores_schema'] or ''}")
    if ev["schema_valid"]:
        print(f"Coherencia señal->riesgo: {ev['coherente']} | evidencia literal: {ev['evidencia_literal']}")
    if caso["gold_riesgo"]:
        print(f"Riesgo correcto: {ev['riesgo_correcto']} (gold={caso['gold_riesgo']}) | "
              f"señal correcta: {ev['senal_correcta']} -> estado: {ev['estado']}")

    if args.sondeo:
        titulo("6. Logits en la posición de \"riesgo\"")
        s = llm.sondear_etiqueta(msgs)
        print("p(etiqueta) normalizada:", s["p_etiqueta_normalizada"])
        print("p(primer token) T=1.0:", s["p_primer_token_T1.0"], "| T=0.8:", s["p_primer_token_T0.8"])
        print("top-5 tokens:", s["top5_T1.0"])

    destino = RESULTS_DIR / "demo"
    destino.mkdir(parents=True, exist_ok=True)
    archivo = destino / f"{caso['id']}_{args.prompt}_{args.contexto}_{args.politica}_{datetime.now():%Y%m%d-%H%M%S}.json"
    archivo.write_text(json.dumps({"args": vars(args), "caso": caso["id"], "mensajes": msgs, **gen,
                                   **{k: v for k, v in ev.items()}}, indent=2, ensure_ascii=False), encoding="utf-8")
    titulo("Resultado guardado")
    print(archivo)


if __name__ == "__main__":
    main()
