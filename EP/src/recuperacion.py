"""Recuperacion del EP: denso (e5 + FAISS), BM25, RRF y Cross-Encoder.

Condiciones del experimento 1 (mismas consultas, qrels y unidades):
    A  = denso e5-small + FAISS IndexFlatIP
    B  = A + BM25 + fusion RRF (k = 60)
    C  = B + reranking con Cross-Encoder sobre los candidatos de B
    A0 = referencia: configuracion de la PC2 (chunks de 180 palabras, solo denso)

Unidad de recuperacion de A/B/C: un pasaje con el encabezado de su proceso
(nomenclatura, objeto y entidad). Asi cada unidad lleva la evidencia y lo que
la identifica (ver README, seccion de segmentacion).
"""
from __future__ import annotations

import re
import time
from functools import lru_cache

import numpy as np

import config_ep as C
import recuperador as pc2  # pc2/src/recuperador.py: chunker, encoder e indice de la PC2

# tokenizacion BM25 de las semanas 5 y 7
TOKEN_RE = re.compile(r"[a-záéíóúñü0-9]+", re.IGNORECASE)
TERMINOS_QUE_SE_QUEDAN = frozenset({"no", "sin", "si", "puede", "pueden", "debe", "más"})
STOPWORDS = frozenset({
    "a", "al", "algo", "como", "con", "cuando", "de", "del", "donde", "e", "el", "ella", "ellas",
    "ellos", "en", "entre", "era", "es", "esa", "ese", "eso", "esta", "este", "esto", "ha", "hay",
    "la", "las", "le", "les", "lo", "los", "o", "para", "pero", "por", "que", "qué", "se", "su",
    "sus", "también", "un", "una", "uno", "unos", "unas", "y", "ya",
})


def tokenizar(texto):
    tokens = [m.group(0).lower() for m in TOKEN_RE.finditer(texto)]
    return [t for t in tokens if t in TERMINOS_QUE_SE_QUEDAN or t not in STOPWORDS]


def encabezado(doc):
    return f"{doc['title']} | {doc['entidad']}"


def unidades_pasaje(docs):
    """Una unidad por pasaje: encabezado del proceso + texto del pasaje."""
    out = []
    for d in docs:
        for p in d["passages"]:
            out.append({"unit_id": p["passage_id"], "doc_id": d["doc_id"], "passage_ids": [p["passage_id"]],
                        "text": encabezado(d) + "\n" + p["text"]})
    return out


def ms(t0):
    return (time.perf_counter() - t0) * 1000


@lru_cache(maxsize=1)
def cross_encoder():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(C.RERANKER_ID, revision=C.RERANKER_REVISION, device="cpu")


class Sistema:
    def __init__(self, docs):
        from rank_bm25 import BM25Okapi

        self.unidades = unidades_pasaje(docs)
        self.por_id = {u["unit_id"]: u for u in self.unidades}
        # denso sobre las unidades (mismo encoder, prefijos y minusculas que la PC2)
        self.vec = pc2.codificar([u["text"] for u in self.unidades], C.PREFIJO_PASSAGE)
        self.index = pc2.indice(self.vec)
        # BM25Okapi: los idf negativos se reemplazan por epsilon * idf promedio
        self.bm25 = BM25Okapi([tokenizar(u["text"]) for u in self.unidades],
                              k1=C.BM25_K1, b=C.BM25_B, epsilon=C.BM25_EPSILON)
        # referencia A0: chunks de la PC2 (180 palabras, 1 pasaje de overlap)
        self.chunks_pc2 = pc2.construir_chunks(docs, C.PC2_TARGET_WORDS, C.PC2_OVERLAP)
        pc2.validar_overlap(self.chunks_pc2)
        for ch in self.chunks_pc2:
            ch["unit_id"] = ch["chunk_id"]
        self.index_pc2 = pc2.indice(pc2.codificar([c["text"] for c in self.chunks_pc2], C.PREFIJO_PASSAGE))

    # ---- piezas
    def denso(self, consulta, depth, index=None, unidades=None):
        index = index or self.index
        unidades = unidades or self.unidades
        q = pc2.codificar([consulta], C.PREFIJO_QUERY)
        scores, idx = index.search(q, min(depth, len(unidades)))
        return [{**unidades[int(i)], "score": float(s)} for i, s in zip(idx[0], scores[0])]

    def lexico(self, consulta, depth):
        s = self.bm25.get_scores(tokenizar(consulta))
        orden = np.argsort(-s, kind="stable")[:depth]
        return [{**self.unidades[int(i)], "score": float(s[i])} for i in orden]

    def rrf(self, rankings, depth):
        fusion = {}
        for ranking in rankings:
            for r, u in enumerate(ranking, 1):
                fusion[u["unit_id"]] = fusion.get(u["unit_id"], 0.0) + 1.0 / (C.RRF_CONSTANT + r)
        orden = sorted(fusion.items(), key=lambda kv: (-kv[1], kv[0]))[:depth]
        return [{**self.por_id[uid], "score": s} for uid, s in orden]

    def rerank(self, consulta, candidatos):
        scores = cross_encoder().predict([[consulta, u["text"]] for u in candidatos], show_progress_bar=False)
        filas = [{**u, "score_rrf": u["score"], "score": float(s)} for u, s in zip(candidatos, scores)]
        return sorted(filas, key=lambda u: (-u["score"], u["unit_id"]))

    # ---- condiciones
    def correr(self, condicion, consulta, depth=C.CANDIDATE_DEPTH):
        t = {"dense_ms": 0.0, "bm25_ms": 0.0, "rrf_ms": 0.0, "reranker_ms": 0.0}
        t_total = time.perf_counter()
        if condicion == "A0":
            t0 = time.perf_counter()
            ranking = self.denso(consulta, depth, self.index_pc2, self.chunks_pc2)
            t["dense_ms"] = ms(t0)
        else:
            t0 = time.perf_counter()
            densa = self.denso(consulta, depth)
            t["dense_ms"] = ms(t0)
            ranking = densa
            if condicion in ("B", "C"):
                t0 = time.perf_counter()
                lex = self.lexico(consulta, depth)
                t["bm25_ms"] = ms(t0)
                t0 = time.perf_counter()
                ranking = self.rrf([densa, lex], depth)
                t["rrf_ms"] = ms(t0)
            if condicion == "C":
                t0 = time.perf_counter()
                ranking = self.rerank(consulta, ranking)
                t["reranker_ms"] = ms(t0)
            elif condicion not in ("A", "B"):
                raise ValueError(f"condicion desconocida: {condicion}")
        t["total_ms"] = ms(t_total)
        return ranking, t

    def calentar(self):
        """Primera llamada fuera de la medicion (carga de modelos y caches)."""
        for cond in ("A0", "A", "B", "C"):
            self.correr(cond, "consulta de calentamiento")
