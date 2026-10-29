"""Carga y valida el benchmark del EP (corpus, consultas, qrels, referencias).

Uso:
    python EP/src/benchmark.py            valida y muestra un resumen
    python EP/src/benchmark.py congelar   ademas guarda los hashes en data/congelamiento.json

El benchmark se congela ANTES de correr los experimentos. Si algo cambia
despues, los hashes ya no coinciden y los experimentos se detienen.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys

import config_ep as C

ARCHIVOS = [C.CORPUS_PATH, C.CONSULTAS_PATH, C.QRELS_PATH, C.REFERENCIAS_PATH]


def leer_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def sha256(path):
    # se ignora el fin de linea (git en windows puede cambiar LF por CRLF al hacer checkout)
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def cargar():
    docs = leer_jsonl(C.CORPUS_PATH)
    consultas = leer_jsonl(C.CONSULTAS_PATH)
    qrels = json.loads(C.QRELS_PATH.read_text(encoding="utf-8"))
    refs = {r["query_id"]: r for r in leer_jsonl(C.REFERENCIAS_PATH)}
    return docs, consultas, qrels, refs


def pasajes(docs):
    return {p["passage_id"]: {**p, "doc_id": d["doc_id"]} for d in docs for p in d["passages"]}


def validar(docs, consultas, qrels, refs):
    ids = [c["query_id"] for c in consultas]
    assert len(ids) == len(set(ids)), "query_id repetido"
    assert set(ids) == set(qrels), "consultas y qrels no tienen los mismos ids"
    todos = pasajes(docs)
    assert len(todos) == sum(len(d["passages"]) for d in docs), "passage_id repetido"
    for qid, rel in qrels.items():
        faltan = set(rel) - set(todos)
        assert not faltan, f"{qid}: pasajes inexistentes {faltan}"
    con_evidencia = [q for q in ids if qrels[q]]
    sin_evidencia = [q for q in ids if not qrels[q]]
    for qid, r in refs.items():
        assert qid in qrels, f"referencia sin consulta: {qid}"
        assert set(r["supporting_passage_ids"]) <= set(qrels[qid]), f"{qid}: soporte fuera de qrels"
        assert r["debe_abstenerse"] == (not qrels[qid]), f"{qid}: abstencion no coincide con qrels"
    exp2 = [c["query_id"] for c in consultas if c["exp2"]]
    assert set(exp2) <= set(refs), "consultas del exp. 2 sin referencia"
    return con_evidencia, sin_evidencia, exp2


def congelar():
    info = {"congelado_en": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "nota": "benchmark fijado antes de correr los experimentos 1 y 2",
            "sha256": {p.name: sha256(p) for p in ARCHIVOS}}
    C.CONGELAMIENTO_PATH.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    return info


def verificar_congelado():
    """Los experimentos llaman a esta funcion: falla si el benchmark cambio."""
    info = json.loads(C.CONGELAMIENTO_PATH.read_text(encoding="utf-8"))
    for p in ARCHIVOS:
        if sha256(p) != info["sha256"][p.name]:
            raise RuntimeError(f"{p.name} cambio despues de congelar el benchmark")
    return info


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    docs, consultas, qrels, refs = cargar()
    con, sin, exp2 = validar(docs, consultas, qrels, refs)
    n_rel = [len(qrels[q]) for q in con]
    print(f"documentos: {len(docs)} | pasajes: {sum(len(d['passages']) for d in docs)}")
    print(f"consultas: {len(consultas)} ({len(con)} con qrels, {len(sin)} sin evidencia: {sin})")
    print(f"pasajes relevantes por consulta: min {min(n_rel)}, max {max(n_rel)}, total {sum(n_rel)}")
    print(f"consultas del experimento 2: {len(exp2)} -> {exp2}")
    if len(sys.argv) > 1 and sys.argv[1] == "congelar":
        print("congelado:", json.dumps(congelar(), indent=2))


if __name__ == "__main__":
    main()
