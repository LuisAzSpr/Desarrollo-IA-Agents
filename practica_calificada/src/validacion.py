"""Tres niveles de validación de la salida del LLM (Semana 3).

1. JSON parseable      -> exacto (json.loads del texto completo) o recuperado
                          (primer objeto {...} decodificable dentro del texto).
2. Schema-valid        -> cumple schema/salida_requisito.schema.json (Draft 2020-12).
3. Semánticamente OK   -> coherencia senal->riesgo, evidencia literal y, contra
                          el gold, etiqueta y señal correctas.
"""
from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Optional

from jsonschema import Draft202012Validator

from config import SCHEMA_PATH, SENAL_A_RIESGO

SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


def parse_exacto(raw: str) -> Optional[dict]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def recuperar_objeto(raw: str) -> Optional[dict]:
    decoder = json.JSONDecoder()
    for m in re.finditer(r"\{", raw):
        try:
            data, _ = decoder.raw_decode(raw[m.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return None


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[\"'“”‘’¿?]", "", texto.upper())
    return " ".join(texto.split())


def evaluar(raw: str, caso: dict) -> dict[str, Any]:
    exacto = parse_exacto(raw)
    parsed = exacto if exacto is not None else recuperar_objeto(raw)
    r = {
        "json_exacto": exacto is not None,
        "json_recuperado": parsed is not None,
        "parsed": parsed,
        "schema_valid": False,
        "errores_schema": [],
        "pred_riesgo": None,
        "pred_senal": None,
        "confianza": None,
        "coherente": False,
        "evidencia_literal": False,
        "riesgo_correcto": False,
        "senal_correcta": False,
    }
    if parsed is None:
        r["estado"] = "json_invalido"
        return r

    errores = sorted(VALIDATOR.iter_errors(parsed), key=lambda e: list(e.path))
    r["errores_schema"] = [f"{'/'.join(map(str, e.path)) or '<raíz>'}: {e.message}" for e in errores][:5]
    r["schema_valid"] = not errores
    r["pred_riesgo"] = parsed.get("riesgo") if isinstance(parsed.get("riesgo"), str) else None
    r["pred_senal"] = parsed.get("senal") if isinstance(parsed.get("senal"), str) else None
    conf = parsed.get("confianza")
    r["confianza"] = float(conf) if isinstance(conf, (int, float)) and not isinstance(conf, bool) else None

    if not r["schema_valid"]:
        r["estado"] = "schema_invalido"
        return r

    evid = parsed["evidencia"].strip()
    r["coherente"] = SENAL_A_RIESGO[parsed["senal"]] == parsed["riesgo"]
    if parsed["senal"] == "ninguna":
        r["evidencia_literal"] = evid == "" or normalizar(evid) in normalizar(caso["requerimiento"])
    else:
        r["evidencia_literal"] = evid != "" and normalizar(evid) in normalizar(caso["requerimiento"])
    r["riesgo_correcto"] = parsed["riesgo"] == caso["gold_riesgo"]
    r["senal_correcta"] = parsed["senal"] in caso["gold_senales"]
    r["estado"] = "valido_correcto" if r["riesgo_correcto"] else "valido_incorrecto"
    return r


if __name__ == "__main__":
    caso = {"requerimiento": "ADQUISICIÓN DE SWITCHES DE LA MARCA CISCO", "gold_riesgo": "alto",
            "gold_senales": ["marca_sin_equivalente"]}
    ok = '{"riesgo": "alto", "senal": "marca_sin_equivalente", "evidencia": "marca Cisco", "confianza": 0.9, "justificacion": "Exige la marca Cisco."}'
    assert evaluar(ok, caso)["estado"] == "valido_correcto"
    assert evaluar("```json\n" + ok + "\n```", caso)["json_exacto"] is False
    assert evaluar("```json\n" + ok + "\n```", caso)["schema_valid"] is True
    malo = ok.replace('"alto"', '"high"')
    assert evaluar(malo, caso)["estado"] == "schema_invalido"
    incoh = ok.replace('"alto"', '"bajo"')
    e = evaluar(incoh, caso)
    assert e["schema_valid"] and not e["coherente"] and e["estado"] == "valido_incorrecto"
    inventada = ok.replace("marca Cisco", "marca Juniper")
    assert evaluar(inventada, caso)["evidencia_literal"] is False
    assert evaluar("No puedo responder", caso)["estado"] == "json_invalido"
    print("validacion.py: pruebas OK")
