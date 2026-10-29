"""Indice local de procesos para la herramienta del experimento 3.

Uso:
    python EP/src/armar_indice.py

Una fila por ocid del corpus con los campos estructurados de OCDS que usa la
herramienta (valor referencial, postores, items y adjudicaciones). Sale de los
mismos CSV que el corpus (src/ocds.py::ficha_proceso). Ya queda guardado en
EP/data/indice_procesos.jsonl, asi que la herramienta y sus pruebas no
necesitan los CSV.
"""
from __future__ import annotations

import json

import pandas as pd

import benchmark
import config_ep as C
from ocds import ficha_proceso  # src/ocds.py de la PC1


def valor(x):
    return None if pd.isna(x) else float(x)


def fila(ocid):
    f = ficha_proceso(ocid)
    return {
        "ocid": ocid,
        "nomenclatura": f["nomenclatura"],
        "entidad": f["entidad"],
        "objeto": f["objeto"],
        "valor_referencial_pen": valor(f["valor_referencial_pen"]),
        "n_postores": None if pd.isna(f["n_postores_ocds"]) else int(f["n_postores_ocds"]),
        "postores": list(dict.fromkeys(p["name"] for p in f["postores"])),
        "items": [{"tender_item_id": int(it["id"]), "descripcion": it["description"],
                   "valor": valor(it["totalValue_amount"]), "moneda": it["totalValue_currency"],
                   "estado": it["statusDetails"]} for it in f["items"]],
        "adjudicaciones": [{"proveedor": a["name"], "monto": valor(a["value_amount"]), "moneda": a["value_currency"]}
                           for a in f["adjudicaciones"]],
    }


def main():
    docs, _, _, _ = benchmark.cargar()
    with C.INDICE_PROCESOS_PATH.open("w", encoding="utf-8", newline="\n") as out:
        for d in docs:
            r = fila(d["ocid"])
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"{d['doc_id']} {r['nomenclatura'][:40]:40s} items={len(r['items']):3d} "
                  f"postores={r['n_postores']} adjudicaciones={len(r['adjudicaciones'])}")
    print(f"-> {C.INDICE_PROCESOS_PATH}")


if __name__ == "__main__":
    main()
