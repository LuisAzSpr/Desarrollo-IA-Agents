"""Construye el corpus del EP a partir de los CSV OCDS del SEACE (2024-2026).

Uso:
    python EP/src/armar_corpus.py

Cada documento es el expediente OCDS de un proceso real (un ocid). Se divide en
pasajes con la misma funcion de la PC2 (pc2/src/construir_corpus.py):
convocatoria, items (texto literal publicado por la entidad), cronograma,
documentos, postores, resultado (buena pro) y contrato.

Procesos incluidos (55, sin repetir ocid):
  E01-E10  los 10 documentos del corpus de la PC2 (continuidad)
  E11-E55  el resto de los 54 procesos del benchmark v2 de la PC1

Necesita los CSV OCDS (ver data/README.md). El corpus ya generado esta en
EP/data/corpus.jsonl, asi que los experimentos corren sin los CSV.
"""
from __future__ import annotations

import json

import config_ep as C
from construir_corpus import passages_de  # pc2/src/construir_corpus.py

P = "ocds-dgv273-seacev3-"
SENAL_TXT = {
    "marca_sin_equivalente": "marca sin equivalente",
    "marca_con_equivalente": "marca con 'o equivalente'",
    "compatibilidad_equipo_existente": "bien o servicio para un equipo que la entidad ya tiene",
    "ninguna": "sin marca",
}


def leer_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def lista_procesos():
    pc2 = leer_jsonl(C.REPO / "pc2" / "data" / "corpus.jsonl")
    casos = leer_jsonl(C.REPO / "data" / "casos_v2.jsonl")
    caso_por_ocid = {c["ocid"]: c for c in casos}
    # ítem objetivo de la PC2 cuando el proceso tiene muchos items
    objetivo_pc2 = {P + "1184513": 21194858, P + "1042389": 20782034}

    procesos = []
    for d in pc2:
        caso = caso_por_ocid.get(d["ocid"])
        objetivo = objetivo_pc2.get(d["ocid"], caso["tender_item_id"] if caso else None)
        procesos.append((d["ocid"], objetivo, f"pc2:{d['doc_id']}" + (f", v2:{caso['id']}" if caso else ""),
                         d["motivo"]))
    vistos = {p[0] for p in procesos}
    for c in casos:
        if c["ocid"] in vistos:
            continue
        senales = " / ".join(SENAL_TXT[s] for s in c["gold_senales"])
        motivo = f"{senales}; {c['n_postores']} postor(es). Caso {c['id']} del benchmark v2 de la PC1."
        procesos.append((c["ocid"], c["tender_item_id"], f"v2:{c['id']}", motivo))
        vistos.add(c["ocid"])
    return procesos


def main():
    C.DATA.mkdir(parents=True, exist_ok=True)
    docs = []
    for i, (ocid, objetivo, origen, motivo) in enumerate(lista_procesos(), 1):
        doc_id = f"E{i:02d}"
        meta, passages = passages_de(doc_id, ocid, objetivo)
        docs.append({**meta, "origen": origen, "motivo": motivo, "passages": passages})
        palabras = sum(len(p["text"].split()) for p in passages)
        print(f"{doc_id} {origen:18s} pasajes={len(passages):2d} palabras={palabras:4d} | {meta['title'][:60]}")
    with C.CORPUS_PATH.open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    n = sum(len(d["passages"]) for d in docs)
    print(f"\n{len(docs)} documentos, {n} pasajes -> {C.CORPUS_PATH}")


if __name__ == "__main__":
    main()
