"""Experimento 3: contratos de la herramienta ocds.indicadores_proceso.

Uso:
    python EP/src/exp3_herramienta.py

Mismos 16 casos (entradas y fallos inyectados) bajo cuatro politicas:
    A  sin contratos: se ejecuta lo que llegue, errores sin tipo, sin reintento
    B  contratos de entrada y salida + ToolError tipado, sin reintento ni timeout
    C  B + timeout + reintento de CUALQUIER error (reintento ingenuo)
    D  B + timeout por intento + deadline + reintento SOLO de transient/timeout

Para cada caso se fija antes el resultado que pide la especificacion
(status y tipo de error). Salidas en EP/results/exp3/.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import platform
import sys

import pandas as pd
import pydantic

import config_ep as C
import herramienta as H

OUT = C.RESULTS / "exp3"
E03, E11, E36, E49, E50, E02 = (f"ocds-dgv273-seacev3-{x}" for x in
                                ("1095541", "2025-42031-2", "2025-200121-10", "1201784", "1228163", "1184513"))

# (id, argumentos, fallo inyectado, resultado esperado: "ok" + alertas o el kind del error)
CASOS = [
    ("valido_equivalente_solo_en_objeto", {"ocid": E36}, "ninguno", ("ok", ["equivalente_solo_en_objeto"])),
    ("valido_unico_postor", {"ocid": E50}, "ninguno", ("ok", ["unico_postor"])),
    ("valido_adjudicado_sobre_vr", {"ocid": E11}, "ninguno", ("ok", ["adjudicado_sobre_vr"])),
    ("valido_item_de_proceso_con_6_items", {"ocid": E49, "tender_item_id": 21238780}, "ninguno", ("ok", ["unico_postor"])),
    ("invalido_ocid_mal_formado", {"ocid": "2025-42031-2"}, "ninguno", ("validation", None)),
    ("invalido_item_como_texto", {"ocid": E50, "tender_item_id": "21314522"}, "ninguno", ("validation", None)),
    ("invalido_argumento_extra", {"ocid": E50, "entidad": "HOSPITAL GENERAL DE JAEN"}, "ninguno", ("validation", None)),
    ("dominio_ocid_inexistente", {"ocid": "ocds-dgv273-seacev3-9999999"}, "ninguno", ("domain", None)),
    ("dominio_item_de_otro_proceso", {"ocid": E03, "tender_item_id": 21314522}, "ninguno", ("domain", None)),
    ("dominio_falta_item_en_proceso_de_104_items", {"ocid": E02}, "ninguno", ("domain", None)),
    ("transitorio_una_vez", {"ocid": E03}, "transitorio_una_vez", ("ok", ["unico_postor"])),
    ("transitorio_siempre", {"ocid": E03}, "transitorio_siempre", ("transient", None)),
    ("lento_una_vez", {"ocid": E03}, "lento_una_vez", ("ok", ["unico_postor"])),
    ("lento_siempre", {"ocid": E03}, "lento_siempre", ("timeout", None)),
    ("error_interno", {"ocid": E03}, "error_interno", ("execution", None)),
    ("salida_mal_formada", {"ocid": E03}, "salida_mal_formada", ("output_contract", None)),
]
NO_REINTENTABLES = {"validation", "domain", "execution", "output_contract", "protocol"}


def cumple(res, esperado):
    status, detalle = esperado
    r = res["result"]
    if status == "ok":
        return r["status"] == "ok" and sorted(r["data"]["alertas"]) == sorted(detalle)
    return r["status"] == "error" and r["error"]["kind"] == status


def reintentos_inutiles(traza):
    """Intentos hechos despues de un error que no se arregla reintentando."""
    return sum(1 for prev in traza[:-1] if prev["status"] == "error" and prev["kind"] in NO_REINTENTABLES) \
        if len(traza) > 1 else 0


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    filas, trazas = [], []
    for pol in H.POLITICAS.values():
        for cid, args, fallo, esperado in CASOS:
            res = asyncio.run(H.ejecutar(H.NOMBRE, args, pol, fallo))
            r = res["result"]
            filas.append({"politica": pol.nombre, "caso": cid, "fallo": fallo,
                          "esperado": esperado[0], "status": r["status"],
                          "error_kind": r["error"]["kind"] if r["error"] else None,
                          "error_code": r["error"]["code"] if r["error"] else None,
                          "retryable": r["error"]["retryable"] if r["error"] else None,
                          "alertas": ";".join(r["data"]["alertas"]) if r["status"] == "ok" and "alertas" in r["data"] else None,
                          "cumple_especificacion": cumple(res, esperado), "intentos": res["intentos"],
                          "reintentos_inutiles": reintentos_inutiles(res["traza"]),
                          "entrada_invalida_ejecutada": res["entrada_invalida_ejecutada"],
                          "salida_invalida_aceptada": res["salida_invalida_aceptada"],
                          "latency_ms": res["latency_ms"]})
            trazas.append({"politica": pol.nombre, "caso": cid, "argumentos": args, "fallo": fallo, **res})

    df = pd.DataFrame(filas)
    df.to_csv(OUT / "casos.csv", index=False)
    with (OUT / "trazas.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for t in trazas:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    res = df.groupby("politica").agg(
        casos=("caso", "count"), cumplen_especificacion=("cumple_especificacion", "sum"),
        entradas_invalidas_ejecutadas=("entrada_invalida_ejecutada", "sum"),
        salidas_invalidas_aceptadas=("salida_invalida_aceptada", "sum"),
        intentos_totales=("intentos", "sum"), reintentos_inutiles=("reintentos_inutiles", "sum"),
        latencia_media_ms=("latency_ms", "mean"), latencia_max_ms=("latency_ms", "max")).round(1)
    res.to_csv(OUT / "resumen.csv")
    tabla = df.pivot(index="caso", columns="politica", values="cumple_especificacion")
    tabla = tabla.reindex([c[0] for c in CASOS])
    tabla.to_csv(OUT / "cumplimiento_por_caso.csv")

    manifiesto = {
        "experimento": 3, "herramienta": H.NOMBRE,
        "politicas": {k: vars(p) for k, p in H.POLITICAS.items()},
        "indice_sha256": hashlib.sha256(C.INDICE_PROCESOS_PATH.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "schema_entrada": H.IndicadoresEntrada.model_json_schema(),
        "schema_salida": H.IndicadoresSalida.model_json_schema(),
        "versiones": {"python": platform.python_version(), "pydantic": pydantic.__version__},
    }
    (OUT / "manifiesto.json").write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")
    print(res.to_string(), "\n")
    print(tabla.to_string())


if __name__ == "__main__":
    main()
