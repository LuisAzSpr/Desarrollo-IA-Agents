"""Configuración única del prototipo PC1.

Todo lo que define una condición experimental (modelo, revisión, decoding,
semillas, rutas) vive aquí para que quede registrado en un solo lugar.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Carpeta con los CSV OCDS descargados (no se versionan: ~1.4 GB).
# Por defecto: ../claudego/2026 respecto del repositorio.
OCDS_DIR = Path(os.environ.get("OCDS_DIR", ROOT.parent / "claudego" / "2026")).resolve()

DATA_DIR = ROOT / "data"
PROMPTS_DIR = ROOT / "prompts"
SCHEMA_PATH = ROOT / "schema" / "salida_requisito.schema.json"
RESULTS_DIR = ROOT / "results"
FIGS_DIR = RESULTS_DIR / "figs"
CACHE_PATH = RESULTS_DIR / "cache_generaciones.jsonl"
CASOS_PATH = DATA_DIR / "casos.jsonl"
EJEMPLOS_PATH = DATA_DIR / "ejemplos_fewshot.jsonl"

# Modelo: se fija la revisión (commit del repo en Hugging Face) para que la
# ejecución sea repetible aunque el autor publique una versión nueva.
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
MODEL_REVISION = os.environ.get("PC1_MODEL_REVISION", "7ae557604adf67be50417f59c2c2f167def9a775")
DTYPE = "float32"  # CPU: float32 es lo más estable y reproducible.
NUM_THREADS = 8  # fijo: el orden de las sumas en paralelo puede alterar empates en greedy.

MAX_NEW_TOKENS = 192
SEED = 42

# Políticas de decoding. OJO: el generation_config.json de Qwen2.5-Instruct
# trae do_sample=True, temperature=0.7, top_p=0.8, top_k=20 y
# repetition_penalty=1.1. En llm.py se neutraliza ese archivo para que
# "greedy" sea realmente argmax y cada política quede definida solo por esto.
DECODING = {
    "greedy": {
        "do_sample": False,
        "repetition_penalty": 1.0,
        "max_new_tokens": MAX_NEW_TOKENS,
    },
    "sampling": {
        "do_sample": True,
        "temperature": 0.8,
        "top_p": 0.9,
        "top_k": 0,  # 0 = sin truncamiento top-k (solo nucleus / top-p)
        "repetition_penalty": 1.0,
        "max_new_tokens": MAX_NEW_TOKENS,
    },
}

# Semillas del Experimento 3 (una generación por semilla y por caso).
SAMPLING_SEEDS = [0, 1, 2, 3, 4]

LABELS = ["alto", "medio", "bajo"]
SENALES = [
    "marca_sin_equivalente",
    "marca_con_equivalente",
    "compatibilidad_equipo_existente",
    "ninguna",
]
# Regla de coherencia interna (no está en el schema: es validación semántica).
SENAL_A_RIESGO = {
    "marca_sin_equivalente": "alto",
    "marca_con_equivalente": "medio",
    "compatibilidad_equipo_existente": "medio",
    "ninguna": "bajo",
}
ORDEN_RIESGO = {"bajo": 0, "medio": 1, "alto": 2}
