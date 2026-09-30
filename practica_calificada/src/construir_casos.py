"""Extrae los casos del experimento desde los CSV OCDS.

Uso:
    python src/construir_casos.py

Cada caso es un requerimiento REAL (tender_items.description) de un proceso
del SEACE, con su contexto (C0) y el resultado del proceso (C1) tomados de las
tablas OCDS. La etiqueta gold la asigna el autor con la rúbrica de
data/README.md (no viene en los datos).

Salidas:
    data/casos.jsonl, data/casos.csv
    data/ejemplos_fewshot.jsonl
    data/fichas/<caso>.json   ficha 360° del proceso (bases, postores, ganador...)
"""
from __future__ import annotations

import json
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

from config import CASOS_PATH, DATA_DIR, EJEMPLOS_PATH, PROMPTS_DIR
from ocds import ficha_proceso, tabla

# (id, ocid, fragmento para ubicar el ítem, gold riesgo, señales aceptadas,
#  evidencia de referencia, dificultad, nota de etiquetado)
CASOS = [
    ("C01", "ocds-dgv273-seacev3-1216035", "SWITCHES Y ACCESS POINT", "alto", ["marca_sin_equivalente"],
     "MARCA CISCO", "clara", "Impone la marca Cisco a equipos nuevos, sin 'o equivalente' ni equipo previo declarado."),
    ("C02", "ocds-dgv273-seacev3-1177957", "MICROSOFT OFFICE LTSC", "alto", ["marca_sin_equivalente"],
     "LICENCIAS MICROSOFT OFFICE LTSC PROFESSIONAL PLUS 2024", "clara",
     "Exige un producto de un fabricante (Microsoft Office) sin 'o equivalente'."),
    ("C03", "ocds-dgv273-seacev3-2025-200121-10", "Autodesk Autocad", "alto", ["marca_sin_equivalente"],
     "Autodesk Autocad", "ambigua",
     "Software de marca sin 'o equivalente'. Ambiguo: podría responder a compatibilidad de archivos, pero el texto no lo dice."),
    ("C04", "ocds-dgv273-seacev3-1179832", "Office 365 o equivalente", "medio", ["marca_con_equivalente"],
     "Microsoft Office 365 o equivalente", "clara", "Menciona la marca pero admite 'o equivalente'."),
    ("C05", "ocds-dgv273-seacev3-1095541", "SERVIDORES ORACLE", "medio",
     ["marca_con_equivalente", "compatibilidad_equipo_existente"],
     "SERVIDORES ORACLE O EQUIVALENTE", "clara",
     "Soporte de servidores Oracle existentes con 'o equivalente'. Ambas señales llevan a 'medio'."),
    ("C06", "ocds-dgv273-seacev3-1183945", "MINDRAY", "medio", ["compatibilidad_equipo_existente"],
     "EQUIPO PROPIO MINDRAY MODELO CL2000i", "clara",
     "Reactivos para un analizador que la entidad ya posee ('EQUIPO PROPIO')."),
    ("C07", "ocds-dgv273-seacev3-1209013", "EPSON", "medio", ["compatibilidad_equipo_existente"],
     "IMPRESORA EPSON WORKFORCE PRO EM-C800", "clara",
     "Insumos (tintas) para una impresora de marca y modelo que ya existe."),
    ("C08", "ocds-dgv273-seacev3-2026-99-2", 21208372, "bajo", ["ninguna"], "", "clara",
     "Bien genérico (combustible) sin marca ni modelo."),
    ("C09", "ocds-dgv273-seacev3-1183834", "HOJUELA", "bajo", ["ninguna"], "", "clara",
     "Alimento descrito por su composición, sin marca."),
    ("C10", "ocds-dgv273-seacev3-1152458", "plata", "bajo", ["ninguna"], "", "ambigua",
     "Especificación técnica precisa (ley 0,925) pero estándar y sin marca: posible trampa para el modelo."),
]

EJEMPLOS = [
    ("E1", "ocds-dgv273-seacev3-1166420", "MARCA APPLE", "alto", "marca_sin_equivalente", "MARCA APPLE",
     "Exige la marca Apple para computadoras nuevas y no admite equivalentes."),
    ("E2", "ocds-dgv273-seacev3-190715", "ZAPATAS", "medio", "compatibilidad_equipo_existente",
     "TRACTOR ORUGA BULLDOZER D375A B086 KOMATSU",
     "Las zapatas son repuestos para un tractor Komatsu que la entidad ya posee."),
]

CATEGORIA = {"goods": "bienes", "services": "servicios", "works": "obras"}


MONEDA = {"PEN": "S/", "USD": "US$", "EUR": "€"}


def dinero(x, moneda="PEN") -> str:
    if pd.isna(x) or float(x) == 0:
        return "no publicado"
    return f"{MONEDA.get(moneda, moneda)} {float(x):,.2f}"


def limpiar(texto: str) -> str:
    # Los CSV traen saltos de línea escapados ("\\n"); se normalizan a espacio.
    return " ".join(str(texto).replace("\\n", " ").split())


def item_de(ocid: str, fragmento) -> pd.Series:
    """Ubica el ítem por id (int) o por un fragmento único de su descripción."""
    main = tabla("main")
    mid = main.loc[main["ocid"] == ocid, "id"].iloc[0]
    ti = tabla("tender_items")
    ti = ti[ti["main_id"] == mid]
    if isinstance(fragmento, int):
        items = ti[ti["id"] == fragmento]
    else:
        items = ti[ti["description"].str.contains(fragmento, case=False, regex=False, na=False)]
    if len(items) != 1:
        raise ValueError(f"{ocid}: {len(items)} ítems coinciden con '{fragmento}'")
    return items.iloc[0]


def resultado(ficha: dict, item: pd.Series) -> dict:
    """Resultado del ítem: awards_items no guarda el id del ítem convocado, así
    que se enlaza por descripción dentro del mismo proceso."""
    desc = limpiar(item["description"]).upper()
    ai = [a for a in ficha["items_adjudicados"] if limpiar(a["description"]).upper() == desc]
    ids = {a["awards_id"] for a in ai}
    ganadores = sorted({a["name"] for a in ficha["adjudicaciones"] if a["awards_id"] in ids})
    monto = sum(a["totalValue_amount"] for a in ai)
    moneda = ai[0]["totalValue_currency"] if ai else "PEN"
    ref = item["totalValue_amount"]
    pct = f" ({monto / ref:.0%} del valor referencial)" if ref and ref > 0 and monto and \
        moneda == item["totalValue_currency"] else ""
    return {
        "n_postores": int(ficha["n_postores_ocds"]) if pd.notna(ficha["n_postores_ocds"]) else None,
        "ganador": " | ".join(ganadores) if ganadores else "sin buena pro registrada",
        "monto_adjudicado": (dinero(monto, moneda) + pct) if monto else "no registrado",
    }


def render(plantilla: str, valores: dict) -> str:
    texto = plantilla
    for k, v in valores.items():
        texto = texto.replace("{" + k + "}", str(v))
    return texto.strip()


def construir(spec, plantilla_c0, plantilla_c1) -> dict:
    cid, ocid, frag = spec[:3]
    item = item_de(ocid, frag)
    ficha = ficha_proceso(ocid)
    res = resultado(ficha, item)
    base = {
        "entidad": ficha["entidad"],
        "procedimiento": ficha["procedimiento"],
        "nomenclatura": ficha["nomenclatura"],
        "categoria": CATEGORIA.get(ficha["categoria"], ficha["categoria"]),
        "cubso": item["classification_description"] if pd.notna(item["classification_description"]) else "no registrada",
        "valor_referencial": dinero(item["totalValue_amount"], item["totalValue_currency"]),
        "fecha": str(ficha["fecha_convocatoria"])[:10],
    }
    bases = [d for d in ficha["bases_y_documentos"] if d["title"] in ("Bases Administrativas", "Bases Integradas")]
    caso = {
        "id": cid,
        "ocid": ocid,
        "tender_item_id": int(item["id"]),
        "requerimiento": limpiar(item["description"]),
        "estado_item": item["statusDetails"],
        **base,
        **res,
        "contexto_C0": render(plantilla_c0, base),
        "contexto_C1": render(plantilla_c1, {**base, **res}),
        "url_bases": bases[0]["url"] if bases else None,
    }
    (DATA_DIR / "fichas").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "fichas" / f"{cid}.json").write_text(
        json.dumps(ficha, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return caso


def main():
    c0 = (PROMPTS_DIR / "C0_contexto_base.txt").read_text(encoding="utf-8")
    c1 = (PROMPTS_DIR / "C1_contexto_conflictivo.txt").read_text(encoding="utf-8")

    casos = []
    for spec in CASOS:
        caso = construir(spec, c0, c1)
        _, _, _, riesgo, senales, evid, dificultad, nota = spec
        n = caso["n_postores"]
        # Dirección de la señal de resultado: +1 sugiere más riesgo (postor único),
        # -1 sugiere menos riesgo (competencia amplia). El diseño de C1 busca que
        # apunte en contra de la etiqueta gold.
        caso["direccion_senal_C1"] = 1 if n == 1 else (-1 if n and n >= 9 else 0)
        caso.update({"gold_riesgo": riesgo, "gold_senales": senales, "gold_evidencia_ref": evid,
                     "dificultad": dificultad, "nota_etiqueta": nota})
        casos.append(caso)
        print(f"{caso['id']} [{riesgo:5s}] postores={n} dir={caso['direccion_senal_C1']:+d} | {caso['requerimiento'][:90]}")
        print(f"      ganador={caso['ganador']} | {caso['monto_adjudicado']}")

    for c in casos:
        conflicto = (c["gold_riesgo"] == "alto" and c["direccion_senal_C1"] < 0) or \
                    (c["gold_riesgo"] == "bajo" and c["direccion_senal_C1"] > 0) or \
                    (c["gold_riesgo"] == "medio" and c["direccion_senal_C1"] != 0)
        assert conflicto, f"{c['id']}: el contexto C1 no es conflictivo"

    with CASOS_PATH.open("w", encoding="utf-8") as f:
        for c in casos:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    pd.DataFrame(casos).drop(columns=["contexto_C0", "contexto_C1"]).to_csv(
        DATA_DIR / "casos.csv", index=False, encoding="utf-8-sig")

    with EJEMPLOS_PATH.open("w", encoding="utf-8") as f:
        for eid, ocid, frag, riesgo, senal, evid, just in EJEMPLOS:
            item = item_de(ocid, frag)
            ej = {"id": eid, "ocid": ocid, "tender_item_id": int(item["id"]),
                  "requerimiento": limpiar(item["description"]),
                  "salida": {"riesgo": riesgo, "senal": senal, "evidencia": evid, "confianza": 0.9,
                             "justificacion": just}}
            assert evid.upper() in ej["requerimiento"].upper(), eid
            f.write(json.dumps(ej, ensure_ascii=False) + "\n")
            print(eid, ej["requerimiento"])
    print(f"\n{len(casos)} casos -> {CASOS_PATH}")


if __name__ == "__main__":
    main()
