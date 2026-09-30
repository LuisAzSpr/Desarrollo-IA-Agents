"""Plantillas de prompt (se leen tal cual desde prompts/)."""
from __future__ import annotations

from config import PROMPTS_DIR

PLANTILLAS = {
    "P0": "P0_baseline.txt",
    "P1": "P1_mejorado.txt",
    "F1": "F1_fewshot.txt",
}


def sistema() -> str:
    return (PROMPTS_DIR / "system.txt").read_text(encoding="utf-8").strip()


def plantilla(nombre: str) -> str:
    return (PROMPTS_DIR / PLANTILLAS[nombre]).read_text(encoding="utf-8").strip()


def mensajes(prompt: str, caso: dict, contexto: str) -> list[dict]:
    """Separa instrucción (system + plantilla), entrada (requerimiento) y contexto.

    Se usa str.replace y no str.format porque las plantillas contienen llaves
    literales del formato JSON.
    """
    usuario = (plantilla(prompt)
               .replace("{requerimiento}", caso["requerimiento"])
               .replace("{contexto}", caso[f"contexto_{contexto}"]))
    return [
        {"role": "system", "content": sistema()},
        {"role": "user", "content": usuario},
    ]
