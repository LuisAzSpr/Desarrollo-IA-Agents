"""Carga del modelo, generación con política de decoding explícita y sondeo de logits."""
from __future__ import annotations

import time
from functools import lru_cache

import numpy as np
import torch

from config import DECODING, DTYPE, LABELS, MODEL_ID, MODEL_REVISION, NUM_THREADS


def _truststore():
    # En redes con inspección TLS, requests/certifi no reconoce la CA local.
    # truststore usa el almacén de certificados del sistema operativo.
    try:
        import truststore
    except ImportError:
        try:
            import pip._vendor.truststore as truststore
        except ImportError:
            return
    truststore.inject_into_ssl()


@lru_cache(maxsize=1)
def cargar(): 
    from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

    _truststore()
    torch.set_num_threads(NUM_THREADS)
    tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    dtype = getattr(torch, DTYPE)
    try:
        model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REVISION, dtype=dtype)
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(MODEL_ID, revision=MODEL_REVISION, torch_dtype=dtype)
    model.eval()

    # Neutraliza el generation_config.json del modelo (do_sample=True, T=0.7,
    # top_p=0.8, top_k=20, repetition_penalty=1.1). Transformers rellena con
    # esos valores cualquier parámetro que se deje en su default global, así
    # que sin este paso "greedy" no sería argmax puro.
    base = model.generation_config
    model.generation_config = GenerationConfig(
        bos_token_id=base.bos_token_id,
        eos_token_id=base.eos_token_id,
        pad_token_id=base.pad_token_id,
    )
    return tok, model


def revision_resuelta() -> str:
    _, model = cargar()
    return getattr(model.config, "_commit_hash", None) or MODEL_REVISION


def _entradas(mensajes: list[dict], prefijo_asistente: str = ""):
    tok, model = cargar()
    texto = tok.apply_chat_template(mensajes, add_generation_prompt=True, tokenize=False) + prefijo_asistente
    return tok(texto, return_tensors="pt").to(model.device)


def generar(mensajes: list[dict], politica: str = "greedy", seed: int = 0, use_cache: bool = True) -> dict:
    tok, model = cargar()
    kwargs = dict(DECODING[politica])
    torch.manual_seed(seed)
    np.random.seed(seed)
    entradas = _entradas(mensajes)
    n_prompt = entradas["input_ids"].shape[-1]
    t0 = time.perf_counter()
    with torch.inference_mode():
        salida = model.generate(**entradas, **kwargs, use_cache=use_cache)
    ms = (time.perf_counter() - t0) * 1000
    generados = salida[0, n_prompt:]
    termino_eos = bool(len(generados) and int(generados[-1]) in _eos_ids())
    return {
        "raw_text": tok.decode(generados, skip_special_tokens=True).strip(),
        "prompt_tokens": int(n_prompt),
        "generated_tokens": int(len(generados)),
        "truncado": (not termino_eos) and len(generados) >= kwargs["max_new_tokens"],
        "latency_ms": round(ms, 1),
    }


def _eos_ids() -> set[int]:
    _, model = cargar()
    eos = model.generation_config.eos_token_id
    return set(eos if isinstance(eos, list) else [eos])


def sondear_etiqueta(mensajes: list[dict], prefijo: str = '{"riesgo": "', temperaturas=(1.0, 0.8)) -> dict:
    """Probabilidad de cada etiqueta en la posición del valor de "riesgo".

    Se fuerza el prefijo JSON y se leen los logits del siguiente token
    (teacher forcing). La probabilidad de la etiqueta usa la regla de la cadena
    sobre sus tokens ("medio" = "med" + "io") y exige que luego se cierre la
    cadena: se suma la probabilidad de TODOS los tokens que empiezan con
    comilla, porque el BPE de Qwen suele cerrar con '",' y no con '"' solo.
    """
    tok, model = cargar()
    entradas = _entradas(mensajes, prefijo)
    ids = entradas["input_ids"]
    with torch.inference_mode():
        out = model(**entradas, use_cache=True)
    logits = out.logits[0, -1].float()
    pkv = out.past_key_values

    res = {"prefijo": prefijo}
    primeros = {lab: tok.encode(lab)[0] for lab in LABELS}
    for T in temperaturas:
        p = torch.softmax(logits / T, dim=-1)
        res[f"p_primer_token_T{T}"] = {lab: round(float(p[i]), 4) for lab, i in primeros.items()}
    res["top5_T1.0"] = [(tok.decode([int(i)]), round(float(v), 4))
                        for v, i in zip(*torch.topk(torch.softmax(logits, -1), 5))]

    # Log-probabilidad de la secuencia completa de cada etiqueta, reutilizando
    # el KV cache del prefijo (solo se procesan los tokens nuevos).
    cierre = torch.tensor(_ids_con_comilla())
    logp = {}
    for lab in LABELS:
        cont = tok.encode(lab)
        lp = float(torch.log_softmax(logits, -1)[cont[0]])
        cache = _copiar_cache(pkv)
        for j, t in enumerate(cont):
            with torch.inference_mode():
                o = model(input_ids=torch.tensor([[t]]), past_key_values=cache, use_cache=True)
            cache = o.past_key_values
            lsm = torch.log_softmax(o.logits[0, -1].float(), -1)
            lp += float(lsm[cont[j + 1]]) if j + 1 < len(cont) else float(torch.logsumexp(lsm[cierre], 0))
        logp[lab] = lp
    z = np.array(list(logp.values()))
    probs = np.exp(z - z.max())
    probs = probs / probs.sum()
    res["logp_secuencia"] = {k: round(v, 4) for k, v in logp.items()}
    res["p_etiqueta_normalizada"] = {k: round(float(v), 4) for k, v in zip(logp, probs)}
    orden = sorted(res["p_etiqueta_normalizada"].values(), reverse=True)
    res["margen_top1_top2"] = round(orden[0] - orden[1], 4)
    res["prompt_tokens"] = int(ids.shape[-1])
    return res


@lru_cache(maxsize=1)
def _ids_con_comilla() -> list[int]:
    tok, _ = cargar()
    return [i for i in range(len(tok)) if tok.decode([i]).startswith('"')]


def _copiar_cache(pkv):
    import copy
    return copy.deepcopy(pkv)


def medir_kv_cache(mensajes: list[dict], n_tokens: int = 32) -> dict:
    """Misma generación greedy con y sin KV cache: mismo texto, distinto costo."""
    tok, model = cargar()
    entradas = _entradas(mensajes)
    out = {}
    for usar in (True, False):
        t0 = time.perf_counter()
        with torch.inference_mode():
            s = model.generate(**entradas, do_sample=False, max_new_tokens=n_tokens,
                               min_new_tokens=n_tokens, use_cache=usar)
        out["con_cache" if usar else "sin_cache"] = {
            "ms": round((time.perf_counter() - t0) * 1000, 1),
            "texto": tok.decode(s[0, entradas["input_ids"].shape[-1]:], skip_special_tokens=True),
        }
    out["mismo_texto"] = out["con_cache"]["texto"] == out["sin_cache"]["texto"]
    out["prompt_tokens"] = int(entradas["input_ids"].shape[-1])
    out["n_tokens_generados"] = n_tokens
    out["aceleracion"] = round(out["sin_cache"]["ms"] / out["con_cache"]["ms"], 2)
    return out
