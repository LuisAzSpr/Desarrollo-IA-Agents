"""Configuracion del examen parcial (EP).

Todo lo que se mantiene fijo entre condiciones vive aqui: rutas, modelos con
su revision, segmentacion, parametros de BM25 / RRF / reranker, top-k,
decoding y semillas. El EP reutiliza el codigo de la PC1 (src/) y de la PC2
(pc2/src/), por eso se agregan al path.
"""
from __future__ import annotations

import sys
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
REPO = EP.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "pc2" / "src"))

DATA = EP / "data"
PROMPTS = EP / "prompts"
RESULTS = EP / "results"
FIGS = RESULTS / "figs"

CORPUS_PATH = DATA / "corpus.jsonl"
CONSULTAS_PATH = DATA / "consultas.jsonl"
QRELS_PATH = DATA / "qrels.json"
REFERENCIAS_PATH = DATA / "referencias.jsonl"
CONGELAMIENTO_PATH = DATA / "congelamiento.json"
INDICE_PROCESOS_PATH = DATA / "indice_procesos.jsonl"

SEED = 42

# recuperacion densa (la misma de la PC2 y de las semanas 4, 5 y 7)
ENCODER_ID = "intfloat/multilingual-e5-small"
ENCODER_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
PREFIJO_QUERY = "query: "
PREFIJO_PASSAGE = "passage: "

# reranker canonico de las semanas 5 y 7
RERANKER_ID = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
RERANKER_REVISION = "1427fd652930e4ba29e8149678df786c240d8825"

# BM25 (politica de la semana 5: regex unicode, minusculas, stopwords minimas,
# sin stemming ni normalizacion de tildes)
BM25_K1 = 1.5
BM25_B = 0.75
BM25_EPSILON = 0.25

# unidad de recuperacion: un pasaje con el encabezado de su proceso (ver README 5)
# la configuracion de la PC2 (chunks de 180 palabras) se corre como referencia A0
PC2_TARGET_WORDS = 180
PC2_OVERLAP = 1

CANDIDATE_DEPTH = 20   # candidatos que entrega cada recuperador y que ve el reranker
RRF_CONSTANT = 60
TOP_K_VALUES = [1, 3, 5]
BOOTSTRAP_RESAMPLES = 5000

# generacion (experimento 2): mismo modelo, prompt y decoding en closed-book y RAG
LLM = "1.5B"           # Qwen/Qwen2.5-1.5B-Instruct, revision fijada en src/config.py
RAG_TOP_K = 5          # pasajes que entran al contexto
CONDICION_RAG = "C"    # configuracion del experimento 1 que alimenta al RAG
