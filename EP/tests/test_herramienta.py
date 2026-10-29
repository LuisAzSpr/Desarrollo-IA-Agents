"""Pruebas de la herramienta ocds.indicadores_proceso.

    python -m pytest EP/tests -q

Cubren lo que pide el experimento 3: ejecucion valida, entrada invalida,
error de dominio, fallo transitorio y timeout, y cuando se reintenta.
"""
import pytest

import herramienta as H

E03 = "ocds-dgv273-seacev3-1095541"   # SBS, soporte Oracle, 1 postor
E36 = "ocds-dgv273-seacev3-2025-200121-10"  # APN, AutoCAD
E50 = "ocds-dgv273-seacev3-1228163"   # Hospital de Jaen, tomografo Siemens


def ok(r):
    assert r["result"]["status"] == "ok", r["result"]["error"]
    return r["result"]["data"]


def error(r):
    assert r["result"]["status"] == "error"
    return r["result"]["error"]


# ---- ejecucion valida
def test_valido_cumple_contrato_de_salida():
    data = ok(H.llamar({"ocid": E36}))
    H.IndicadoresSalida.model_validate(data)
    assert data["objeto_dice_equivalente"] and not data["item_dice_equivalente"]
    assert data["alertas"] == ["equivalente_solo_en_objeto"]


def test_valido_unico_postor_y_ratio():
    data = ok(H.llamar({"ocid": E50}))
    assert data["n_postores"] == 1 and data["unico_postor"]
    assert data["ratio_adjudicado_vr"] == 1.0 and data["adjudicado_sobre_vr"] is False


# ---- entrada invalida (contrato de entrada): no se ejecuta ni se reintenta
@pytest.mark.parametrize("args", [
    {"ocid": "2025-42031-2"},
    {"ocid": E50, "tender_item_id": "21314522"},
    {"ocid": E50, "tender_item_id": 0},
    {"ocid": E50, "entidad": "HOSPITAL GENERAL DE JAEN"},
    {},
])
def test_entrada_invalida(args):
    r = H.llamar(args)
    e = error(r)
    assert e["kind"] == "validation" and e["retryable"] is False
    assert r["intentos"] == 0


# ---- error de dominio: entrada bien formada que no existe en el SEACE
@pytest.mark.parametrize("args,code", [
    ({"ocid": "ocds-dgv273-seacev3-9999999"}, "proceso_no_encontrado"),
    ({"ocid": E03, "tender_item_id": 21314522}, "item_no_pertenece"),
    ({"ocid": "ocds-dgv273-seacev3-1184513"}, "item_requerido"),
])
def test_error_de_dominio_no_se_reintenta(args, code):
    r = H.llamar(args)
    e = error(r)
    assert (e["kind"], e["code"], e["retryable"]) == ("domain", code, False)
    assert r["intentos"] == 1


# ---- fallos transitorios y timeout
def test_transitorio_una_vez_se_recupera_con_reintento():
    r = H.llamar({"ocid": E03}, fallo="transitorio_una_vez")
    ok(r)
    assert [t["status"] for t in r["traza"]] == ["error", "ok"]


def test_transitorio_sin_reintento_falla():
    e = error(H.llamar({"ocid": E03}, politica="B", fallo="transitorio_una_vez"))
    assert e["kind"] == "transient" and e["retryable"] is True


def test_transitorio_persistente_se_corta_en_max_intentos():
    r = H.llamar({"ocid": E03}, fallo="transitorio_siempre")
    assert error(r)["kind"] == "transient"
    assert r["intentos"] == H.POLITICAS["D"].max_intentos


def test_lento_una_vez_timeout_y_luego_ok():
    r = H.llamar({"ocid": E03}, fallo="lento_una_vez")
    ok(r)
    assert r["traza"][0]["kind"] == "timeout"


def test_lento_siempre_respeta_el_deadline():
    r = H.llamar({"ocid": E03}, fallo="lento_siempre")
    assert error(r)["kind"] == "timeout"
    assert r["latency_ms"] < H.POLITICAS["D"].deadline_ms + 50


# ---- errores que no se arreglan reintentando
def test_error_interno_no_se_reintenta():
    r = H.llamar({"ocid": E03}, fallo="error_interno")
    assert error(r)["kind"] == "execution" and r["intentos"] == 1


def test_salida_mal_formada_se_bloquea():
    r = H.llamar({"ocid": E03}, fallo="salida_mal_formada")
    e = error(r)
    assert e["kind"] == "output_contract" and r["intentos"] == 1


def test_sin_contratos_la_salida_mala_pasa():
    # politica A: es lo que el contrato de salida evita
    r = H.llamar({"ocid": E03}, politica="A", fallo="salida_mal_formada")
    assert ok(r)["n_postores"] == -1 and r["salida_invalida_aceptada"]


def test_reintento_ingenuo_repite_errores_de_dominio():
    r = H.llamar({"ocid": "ocds-dgv273-seacev3-9999999"}, politica="C")
    assert error(r)["kind"] == "domain" and r["intentos"] == 3


# ---- politica de reintento
def test_debe_reintentar():
    d = H.POLITICAS["D"]
    transitorio = H.ToolError(code="x", kind="transient", retryable=True, message="")
    dominio = H.ToolError(code="x", kind="domain", retryable=False, message="")
    assert H.debe_reintentar(transitorio, 1, d) is True
    assert H.debe_reintentar(transitorio, 3, d) is False
    assert H.debe_reintentar(dominio, 1, d) is False


def test_herramienta_desconocida():
    import asyncio
    r = asyncio.run(H.ejecutar("ocds.borrar_proceso", {"ocid": E03}, H.POLITICAS["D"]))
    assert error(r)["kind"] == "protocol"


def test_contrato_de_salida_detecta_alertas_incoherentes():
    data = ok(H.llamar({"ocid": E50}))
    data["alertas"] = []
    with pytest.raises(Exception):
        H.IndicadoresSalida.model_validate(data)
