"""Herramienta del experimento 3: ocds.indicadores_proceso (contratos de la Semana 6).

Especificacion
--------------
nombre      ocds.indicadores_proceso
proposito   dar senales objetivas de un proceso del SEACE, calculadas desde sus
            datos OCDS, para contrastar lo que dice el LLM (PC1) o el RAG:
              - unico_postor            n_postores == 1 (single bidding)
              - adjudicado_sobre_vr     monto adjudicado / valor referencial > 1
              - equivalente_solo_en_objeto
                                        el objeto dice "o equivalente" y el item no
                                        (el item es lo que se compra; caso APN, Q15)
entrada     {"ocid": str, "tender_item_id": int | null}
salida      IndicadoresSalida (abajo)
efectos     ninguno: solo lee el indice local data/indice_procesos.jsonl.
            Por eso un reintento no duplica nada.
errores     validation       la entrada no cumple el contrato (no se reintenta)
            domain           ocid o item que no existen, o falta elegir item (no se reintenta)
            transient        el indice no esta disponible por un momento (se reintenta)
            timeout          un intento pasa del limite (se reintenta si queda deadline)
            execution        excepcion interna no esperada (no se reintenta)
            output_contract  la salida no cumple el contrato (no se reintenta)
            protocol         herramienta desconocida (no se reintenta)

No decide si hay direccionamiento: eso sigue siendo del LLM + regla() de la
PC1. Solo calcula hechos verificables del registro.

Los fallos transitorios y lentos se inyectan de forma determinista con el
parametro `fallo` (como en el Cuaderno 6): hoy el indice es un archivo local y
no falla solo. Simulan lo que pasaria al leer la API OCDS del SEACE.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
import unicodedata
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, ValidationError, model_validator

import config_ep as C

NOMBRE = "ocds.indicadores_proceso"
OCID_RE = r"^ocds-dgv273-seacev3-\d+(-\d+){0,2}$"
EQUIVALENTE_RE = re.compile(r"\bO\s+(EQUIVALENTE|SIMILAR)\b")
Alerta = Literal["unico_postor", "adjudicado_sobre_vr", "equivalente_solo_en_objeto"]


# ---------------------------------------------------------------- contratos
class IndicadoresEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")  # un argumento inventado es un error, no se ignora

    ocid: str = Field(pattern=OCID_RE, max_length=60)
    tender_item_id: StrictInt | None = Field(default=None, ge=1)


class IndicadoresSalida(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ocid: str = Field(pattern=OCID_RE)
    nomenclatura: str = Field(min_length=1)
    entidad: str = Field(min_length=1)
    tender_item_id: int
    item_descripcion: str = Field(min_length=1)
    n_postores: int | None = Field(ge=0)
    unico_postor: bool | None
    ratio_adjudicado_vr: float | None = Field(ge=0)
    adjudicado_sobre_vr: bool | None
    objeto_dice_equivalente: bool
    item_dice_equivalente: bool
    alertas: list[Alerta]
    fuente: str

    @model_validator(mode="after")
    def coherente(self):
        # las banderas tienen que salir de los numeros que la misma salida reporta
        if self.unico_postor != (None if self.n_postores is None else self.n_postores == 1):
            raise ValueError("unico_postor no coincide con n_postores")
        if self.adjudicado_sobre_vr != (None if self.ratio_adjudicado_vr is None else self.ratio_adjudicado_vr > 1):
            raise ValueError("adjudicado_sobre_vr no coincide con el ratio")
        if sorted(self.alertas) != sorted(alertas_de(self.model_dump())):
            raise ValueError("alertas no coinciden con los indicadores")
        return self


ErrorKind = Literal["protocol", "validation", "domain", "transient", "timeout", "execution", "output_contract"]


class ToolError(BaseModel):
    code: str
    kind: ErrorKind
    retryable: bool
    message: str


class ToolResult(BaseModel):
    status: Literal["ok", "error"]
    data: dict[str, Any] | None = None
    error: ToolError | None = None


def error_result(kind, code, message, retryable):
    return ToolResult(status="error", error=ToolError(code=code, kind=kind, retryable=retryable, message=message))


# ---------------------------------------------------------------- excepciones de la implementacion
class DomainError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class TransientToolError(Exception):
    pass


# ---------------------------------------------------------------- implementacion
def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    return " ".join("".join(c for c in texto if not unicodedata.combining(c)).upper().split())


def dice_equivalente(texto):
    return bool(EQUIVALENTE_RE.search(normalizar(texto)))


def alertas_de(s):
    out = []
    if s["unico_postor"]:
        out.append("unico_postor")
    if s["adjudicado_sobre_vr"]:
        out.append("adjudicado_sobre_vr")
    if s["objeto_dice_equivalente"] and not s["item_dice_equivalente"]:
        out.append("equivalente_solo_en_objeto")
    return out


_INDICE = None


def indice():
    global _INDICE
    if _INDICE is None:
        filas = [json.loads(l) for l in C.INDICE_PROCESOS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
        _INDICE = {r["ocid"]: r for r in filas}
    return _INDICE


async def leer_proceso(ocid, fallo, intento):
    """Lectura del indice: el punto donde se inyectan los fallos de infraestructura."""
    if fallo == "transitorio_una_vez" and intento == 1:
        raise TransientToolError("indice no disponible (fallo inyectado, intento 1)")
    if fallo == "transitorio_siempre":
        raise TransientToolError("indice no disponible (fallo inyectado persistente)")
    if (fallo == "lento_una_vez" and intento == 1) or fallo == "lento_siempre":
        await asyncio.sleep(0.15)
    if fallo == "error_interno":
        raise KeyError("valor_referencial_pen")  # simula un bug al leer un campo
    return indice().get(ocid)


async def indicadores_proceso(args, fallo="ninguno", intento=1):
    proc = await leer_proceso(args["ocid"], fallo, intento)
    # validacion de dominio: la entrada esta bien formada pero puede no tener sentido en el SEACE
    if proc is None:
        raise DomainError("proceso_no_encontrado", f"el ocid {args['ocid']} no esta en el indice")
    items = {it["tender_item_id"]: it for it in proc["items"]}
    item_id = args.get("tender_item_id")
    if item_id is None:
        if len(items) != 1:
            raise DomainError("item_requerido", f"el proceso tiene {len(items)} items: indique tender_item_id")
        item_id = next(iter(items))
    if item_id not in items:
        raise DomainError("item_no_pertenece", f"el item {item_id} no pertenece a {args['ocid']}")
    item = items[item_id]

    # mismo criterio que los pasajes (pc2/construir_corpus.py): % solo con una adjudicacion en soles
    adj, vr = proc["adjudicaciones"], proc["valor_referencial_pen"]
    ratio = (round(adj[0]["monto"] / vr, 4) if len(adj) == 1 and vr and adj[0]["moneda"] == "PEN"
             and adj[0]["monto"] is not None else None)
    n = proc["n_postores"]
    salida = {
        "ocid": proc["ocid"], "nomenclatura": proc["nomenclatura"], "entidad": proc["entidad"],
        "tender_item_id": item_id, "item_descripcion": item["descripcion"],
        "n_postores": n, "unico_postor": None if n is None else n == 1,
        "ratio_adjudicado_vr": ratio, "adjudicado_sobre_vr": None if ratio is None else ratio > 1,
        "objeto_dice_equivalente": dice_equivalente(proc["objeto"]),
        "item_dice_equivalente": dice_equivalente(item["descripcion"]),
        "fuente": f"OCDS SEACE via {C.INDICE_PROCESOS_PATH.name}",
    }
    salida["alertas"] = alertas_de(salida)
    if fallo == "salida_mal_formada":
        salida["n_postores"] = -1  # simula un bug que rompe el contrato de salida
    return salida


HERRAMIENTAS = {NOMBRE: (indicadores_proceso, IndicadoresEntrada, IndicadoresSalida)}


# ---------------------------------------------------------------- runtime (Cuaderno 6)
@dataclass(frozen=True)
class Politica:
    nombre: str
    validar_entrada: bool
    validar_salida: bool
    reintento: Literal["no", "todo", "selectivo"]
    usar_timeout: bool
    max_intentos: int = 3
    backoff_ms: tuple[int, ...] = (20, 40)
    timeout_intento_ms: int = 100
    deadline_ms: int = 300


POLITICAS = {
    "A": Politica("A", False, False, "no", False, max_intentos=1),       # sin contratos
    "B": Politica("B", True, True, "no", False, max_intentos=1),         # contratos, sin reintento
    "C": Politica("C", True, True, "todo", True),                        # reintenta cualquier error
    "D": Politica("D", True, True, "selectivo", True),                   # reintenta solo transient/timeout
}


def error_de_excepcion(exc):
    if isinstance(exc, DomainError):
        return ToolError(code=exc.code, kind="domain", retryable=False, message=str(exc))
    if isinstance(exc, TransientToolError):
        return ToolError(code="indice_no_disponible", kind="transient", retryable=True, message=str(exc))
    if isinstance(exc, asyncio.TimeoutError):
        return ToolError(code="attempt_timeout", kind="timeout", retryable=True, message="el intento paso el limite")
    return ToolError(code="internal_error", kind="execution", retryable=False, message=f"{type(exc).__name__}: {exc}")


def debe_reintentar(error, intento, politica):
    if intento >= politica.max_intentos or politica.reintento == "no":
        return False
    if politica.reintento == "todo":
        return True
    return error.retryable


async def ejecutar(nombre, argumentos, politica, fallo="ninguno"):
    """Corre la herramienta bajo una politica. Devuelve el ToolResult y la traza de intentos."""
    t0 = time.perf_counter()
    traza = []
    extra = {"entrada_invalida_ejecutada": False, "salida_invalida_aceptada": False}

    def fin(resultado):
        return {"result": resultado.model_dump(), "intentos": len(traza), "traza": traza,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1), **extra}

    if nombre not in HERRAMIENTAS:
        return fin(error_result("protocol", "unknown_tool", f"herramienta no permitida: {nombre}", False))
    impl, Entrada, Salida = HERRAMIENTAS[nombre]

    args = dict(argumentos)
    try:
        validos = Entrada.model_validate(argumentos).model_dump()
    except ValidationError as exc:
        validos = None
        if politica.validar_entrada:
            return fin(error_result("validation", "invalid_arguments", _primer_error(exc), False))
    if politica.validar_entrada:
        args = validos
    elif validos is None:
        extra["entrada_invalida_ejecutada"] = True  # A ejecuta algo que el contrato habria rechazado

    intento = 0
    while True:
        intento += 1
        ti = time.perf_counter()
        try:
            coro = impl(args, fallo, intento)
            if politica.usar_timeout:
                restante = politica.deadline_ms - (time.perf_counter() - t0) * 1000
                data = await asyncio.wait_for(coro, timeout=min(politica.timeout_intento_ms, restante) / 1000)
            else:
                data = await coro
            try:
                Salida.model_validate(data)
            except ValidationError as exc:
                if politica.validar_salida:
                    raise _SalidaInvalida(_primer_error(exc)) from None
                extra["salida_invalida_aceptada"] = True
            traza.append({"intento": intento, "status": "ok", "kind": None,
                          "ms": round((time.perf_counter() - ti) * 1000, 1)})
            return fin(ToolResult(status="ok", data=data))
        except _SalidaInvalida as exc:
            err = ToolError(code="invalid_tool_output", kind="output_contract", retryable=False, message=str(exc))
        except Exception as exc:  # noqa: BLE001  (toda excepcion se vuelve un ToolError tipado)
            err = error_de_excepcion(exc)
            if not politica.validar_entrada and not politica.validar_salida:
                # A no tiene errores tipados: todo sale como fallo generico
                err = ToolError(code="error", kind="execution", retryable=False, message=f"{type(exc).__name__}: {exc}")
        traza.append({"intento": intento, "status": "error", "kind": err.kind, "retryable": err.retryable,
                      "ms": round((time.perf_counter() - ti) * 1000, 1)})
        if not debe_reintentar(err, intento, politica):
            return fin(ToolResult(status="error", error=err))
        espera = politica.backoff_ms[min(intento - 1, len(politica.backoff_ms) - 1)]
        if politica.usar_timeout and (time.perf_counter() - t0) * 1000 + espera >= politica.deadline_ms:
            return fin(error_result("timeout", "deadline_exceeded",
                                    f"no queda deadline para otro intento ({len(traza)} intentos)", True))
        await asyncio.sleep(espera / 1000)


class _SalidaInvalida(Exception):
    pass


def _primer_error(exc):
    e = exc.errors()[0]
    return f"{'.'.join(str(x) for x in e['loc']) or 'salida'}: {e['msg']}"


def llamar(argumentos, politica="D", fallo="ninguno"):
    """Atajo sincrono para la demo y las pruebas."""
    return asyncio.run(ejecutar(NOMBRE, argumentos, POLITICAS[politica], fallo))
