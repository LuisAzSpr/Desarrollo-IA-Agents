"""Acceso a los CSV OCDS (SEACE, Perú) y relaciones entre tablas.

Cada fila de main.csv es un *compiled release*: un proceso de contratación
(ocid) con su estado más reciente. Todas las tablas hijas cuelgan de él por
`main_id` (= main.id). Los ids de awards, contracts, items y documentos NO son
únicos globalmente: la clave real siempre incluye `main_id`.
"""
from __future__ import annotations

from functools import lru_cache

import pandas as pd

from config import OCDS_DIR

# Tabla -> (clave primaria, [(columnas FK, tabla padre, columnas padre)])
ESQUEMA = {
    "main": (["id"], []),
    "sources": ([], [(["main_id"], "main", ["id"])]),
    "parties": (["main_id", "id"], [(["main_id"], "main", ["id"])]),
    "parties_additionalIdentifiers": ([], [(["main_id", "parties_id"], "parties", ["main_id", "id"])]),
    "tender_documents": (["main_id", "id"], [(["main_id"], "main", ["id"])]),
    "tender_items": (["main_id", "id"], [(["main_id"], "main", ["id"])]),
    "tender_items_additionalClassifications": ([], [(["main_id", "tender_items_id"], "tender_items", ["main_id", "id"])]),
    "tender_items_totalValue_exchangeRates": ([], [(["main_id", "tender_items_id"], "tender_items", ["main_id", "id"])]),
    "tender_tenderers": (["main_id", "id"], [(["main_id"], "main", ["id"]), (["main_id", "id"], "parties", ["main_id", "id"])]),
    "awards": (["main_id", "id"], [(["main_id"], "main", ["id"])]),
    "awards_suppliers": ([], [(["main_id", "awards_id"], "awards", ["main_id", "id"]), (["main_id", "id"], "parties", ["main_id", "id"])]),
    "awards_items": ([], [(["main_id", "awards_id"], "awards", ["main_id", "id"])]),
    "awards_items_additionalClassifications": ([], [(["main_id", "awards_id"], "awards", ["main_id", "id"])]),
    "awards_items_totalValue_exchangeRates": ([], [(["main_id", "awards_id"], "awards", ["main_id", "id"])]),
    "awards_value_exchangeRates": ([], [(["main_id", "awards_id"], "awards", ["main_id", "id"])]),
    "contracts": (["main_id", "id"], [(["main_id"], "main", ["id"]), (["main_id", "awardID"], "awards", ["main_id", "id"])]),
    "contracts_documents": ([], [(["main_id", "contracts_id"], "contracts", ["main_id", "id"])]),
    "contracts_items": ([], [(["main_id", "contracts_id"], "contracts", ["main_id", "id"])]),
    "contracts_items_additionalClassifications": ([], [(["main_id", "contracts_id"], "contracts", ["main_id", "id"])]),
    "contracts_items_totalValue_exchangeRates": ([], [(["main_id", "contracts_id"], "contracts", ["main_id", "id"])]),
    "contracts_value_exchangeRates": ([], [(["main_id", "contracts_id"], "contracts", ["main_id", "id"])]),
}


def ruta(tabla: str):
    path = OCDS_DIR / f"{tabla}.csv"
    if not path.is_file():
        raise FileNotFoundError(
            f"No existe {path}. Define OCDS_DIR con la carpeta de los CSV OCDS."
        )
    return path


def leer(tabla: str, usecols=None) -> pd.DataFrame:
    return pd.read_csv(ruta(tabla), usecols=usecols, low_memory=False)


@lru_cache(maxsize=None)
def tabla(tabla: str) -> pd.DataFrame:
    """Lectura completa con caché en memoria (para la ficha 360°)."""
    return leer(tabla)


def ficha_proceso(ocid: str) -> dict:
    """Ficha 360° de un proceso: entidad, bases, ítems, postores, ganador, contrato."""
    main = tabla("main")
    fila = main.loc[main["ocid"] == ocid]
    if fila.empty:
        raise KeyError(ocid)
    m = fila.iloc[0]
    mid = m["id"]

    def hijos(nombre, cols):
        df = tabla(nombre)
        return df.loc[df["main_id"] == mid, cols]

    docs = hijos("tender_documents", ["title", "documentType", "format", "datePublished", "url"])
    items = hijos("tender_items", ["id", "description", "quantity", "unit_name", "totalValue_amount",
                                   "totalValue_currency", "classification_description", "statusDetails"])
    postores = hijos("tender_tenderers", ["id", "name"])
    awards = hijos("awards", ["id", "date", "value_amount", "value_currency"])
    sup = hijos("awards_suppliers", ["awards_id", "id", "name"])
    aitems = hijos("awards_items", ["awards_id", "description", "quantity", "totalValue_amount",
                                    "totalValue_currency", "statusDetails"])
    contratos = hijos("contracts", ["id", "awardID", "dateSigned", "value_amount", "value_currency", "statusDetails"])

    ganadores = awards.merge(sup, left_on="id", right_on="awards_id", suffixes=("_award", "_proveedor"))
    return {
        "ocid": ocid,
        "entidad": m["buyer_name"],
        "entidad_id": m["buyer_id"],
        "procedimiento": m["tender_procurementMethodDetails"],
        "nomenclatura": m["tender_title"],
        "categoria": m["tender_mainProcurementCategory"],
        "objeto": m["tender_description"],
        "fecha_convocatoria": m["tender_datePublished"],
        "valor_referencial_pen": m["tender_value_amount_PEN"],
        "n_postores_ocds": m["tender_numberOfTenderers"],
        "bases_y_documentos": docs.to_dict("records"),
        "items": items.to_dict("records"),
        "postores": postores.to_dict("records"),
        "adjudicaciones": ganadores.to_dict("records"),
        "items_adjudicados": aitems.to_dict("records"),
        "contratos": contratos.to_dict("records"),
    }
