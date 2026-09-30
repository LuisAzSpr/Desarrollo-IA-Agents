# Resumen de experimentos

Generado por `src/reporte.py` a partir de `results/*.jsonl`. Todas las métricas son sobre 10 casos (Exp. 3: 10 casos × 5 semillas en sampling).

## exp1_prompt

| condicion | n | json_exacto_rate | schema_valid_rate | accuracy | macro_f1 | senal_accuracy | coherencia_rate | evidencia_literal_rate | confianza_media | prompt_tokens_medio | latencia_media_s | distribucion_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 10 | 0.0 | 0.5 | 0.2 | 0.167 | 0.0 | 0.0 | 0.8 | 0.92 | 383.5 | 21.3 | {'alto': 5, 'invalido': 5} |
| P1 | 10 | 0.5 | 0.9 | 0.3 | 0.154 | 0.1 | 1.0 | 0.0 | 0.8 | 635.5 | 23.4 | {'medio': 9, 'invalido': 1} |

## exp2_contexto

| condicion | n | json_exacto_rate | schema_valid_rate | accuracy | macro_f1 | senal_accuracy | coherencia_rate | evidencia_literal_rate | confianza_media | prompt_tokens_medio | latencia_media_s | distribucion_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 10 | 0.5 | 0.9 | 0.3 | 0.154 | 0.1 | 1.0 | 0.0 | 0.8 | 635.5 | 23.4 | {'medio': 9, 'invalido': 1} |
| C1 | 10 | 0.2 | 0.8 | 0.2 | 0.111 | 0.0 | 1.0 | 0.0 | 0.8 | 702.9 | 21.6 | {'medio': 8, 'invalido': 2} |

## exp3_decoding

| condicion | n | json_exacto_rate | schema_valid_rate | accuracy | macro_f1 | senal_accuracy | coherencia_rate | evidencia_literal_rate | confianza_media | prompt_tokens_medio | latencia_media_s | distribucion_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D0_greedy | 20 | 0.5 | 0.9 | 0.3 | 0.154 | 0.1 | 1.0 | 0.0 | 0.8 | 635.5 | 22.5 | {'medio': 18, 'invalido': 2} |
| D1_sampling | 50 | 0.3 | 0.26 | 0.12 | 0.167 | 0.1 | 1.0 | 0.615 | 0.9 | 635.5 | 23.5 | {'invalido': 37, 'medio': 5, 'bajo': 8} |

## exp4_fewshot

| condicion | n | json_exacto_rate | schema_valid_rate | accuracy | macro_f1 | senal_accuracy | coherencia_rate | evidencia_literal_rate | confianza_media | prompt_tokens_medio | latencia_media_s | distribucion_pred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F0_zeroshot | 10 | 0.5 | 0.9 | 0.3 | 0.154 | 0.1 | 1.0 | 0.0 | 0.8 | 635.5 | 23.4 | {'medio': 9, 'invalido': 1} |
| F1_fewshot | 10 | 1.0 | 1.0 | 0.4 | 0.19 | 0.3 | 1.0 | 0.0 | 0.9 | 919.5 | 18.1 | {'medio': 10} |

### Exp. 1 por caso

| id | gold | P0 | P1 | senal_P0 | senal_P1 | ok_P0 | ok_P1 | cambio |
|---|---|---|---|---|---|---|---|---|
| C01 | alto | alto | medio | ninguna | marca_con_equivalente | True | False | empeora |
| C02 | alto | alto | medio | ninguna | marca_con_equivalente | True | False | empeora |
| C03 | alto | json✗ | medio | None | marca_con_equivalente | False | False | cambia (mismo acierto) |
| C04 | medio | schema✗ | json✗ | Microsoft Office 365 | None | False | False | cambia (mismo acierto) |
| C05 | medio | schema✗ | medio | marca_con_equivalente|ninguna | marca_con_equivalente | False | True | mejora |
| C06 | medio | alto | medio | ninguna | marca_con_equivalente | False | True | mejora |
| C07 | medio | alto | medio | ninguna | marca_con_equivalente | False | True | mejora |
| C08 | bajo | alto | medio | compatibilidad_equipo_existente | marca_con_equivalente | False | False | cambia (mismo acierto) |
| C09 | bajo | schema✗ | medio | marca_con_equivalente|ninguna | marca_con_equivalente | False | False | cambia (mismo acierto) |
| C10 | bajo | schema✗ | medio | marca_con_equivalente|ninguna | marca_con_equivalente | False | False | cambia (mismo acierto) |

### Exp. 2 por caso

| id | gold | C0 | C1 | senal_C0 | senal_C1 | ok_C0 | ok_C1 | cambio | direccion_senal | hacia_la_senal |
|---|---|---|---|---|---|---|---|---|---|---|
| C01 | alto | medio | medio | marca_con_equivalente | marca_con_equivalente | False | False | igual | -1 | 0.0 |
| C02 | alto | medio | medio | marca_con_equivalente | marca_con_equivalente | False | False | igual | -1 | 0.0 |
| C03 | alto | medio | medio | marca_con_equivalente | marca_con_equivalente | False | False | igual | -1 | 0.0 |
| C04 | medio | json✗ | schema✗ | None | marca_con_equivalente | False | False | cambia (mismo acierto) | -1 | nan |
| C05 | medio | medio | schema✗ | marca_con_equivalente | marca_con_equivalente | True | False | empeora | 1 | nan |
| C06 | medio | medio | medio | marca_con_equivalente | marca_con_equivalente | True | True | igual | 1 | 0.0 |
| C07 | medio | medio | medio | marca_con_equivalente | marca_con_equivalente | True | True | igual | -1 | 0.0 |
| C08 | bajo | medio | medio | marca_con_equivalente | marca_con_equivalente | False | False | igual | 1 | 0.0 |
| C09 | bajo | medio | medio | marca_con_equivalente | marca_con_equivalente | False | False | igual | 1 | 0.0 |
| C10 | bajo | medio | medio | marca_con_equivalente | marca_con_equivalente | False | False | igual | 1 | 0.0 |

### Exp. 2 · desplazamiento en probabilidad (sondeo de logits)

E[riesgo] = 0·p(bajo) + 1·p(medio) + 2·p(alto). `hacia_la_senal` > 0 significa que C1 movió la distribución en la dirección que sugiere el resultado del proceso.

| id | direccion_senal | E_riesgo_C0 | E_riesgo_C1 | delta | hacia_la_senal |
|---|---|---|---|---|---|
| C01 | -1 | 1.171 | 1.167 | -0.004 | 0.004 |
| C02 | -1 | 1.107 | 1.137 | 0.031 | -0.031 |
| C03 | -1 | 1.19 | 1.11 | -0.08 | 0.08 |
| C04 | -1 | 1.124 | 1.142 | 0.018 | -0.018 |
| C05 | 1 | 1.075 | 1.131 | 0.056 | 0.056 |
| C06 | 1 | 1.149 | 1.222 | 0.073 | 0.073 |
| C07 | -1 | 1.17 | 1.142 | -0.028 | 0.028 |
| C08 | 1 | 1.261 | 1.276 | 0.016 | 0.016 |
| C09 | 1 | 1.191 | 1.275 | 0.084 | 0.084 |
| C10 | 1 | 1.071 | 1.067 | -0.004 | -0.004 |

### Exp. 4 (opcional) por caso

| id | gold | F0_zeroshot | F1_fewshot | senal_F0_zeroshot | senal_F1_fewshot | ok_F0_zeroshot | ok_F1_fewshot | cambio |
|---|---|---|---|---|---|---|---|---|
| C01 | alto | medio | medio | marca_con_equivalente | compatibilidad_equipo_existente | False | False | igual |
| C02 | alto | medio | medio | marca_con_equivalente | compatibilidad_equipo_existente | False | False | igual |
| C03 | alto | medio | medio | marca_con_equivalente | compatibilidad_equipo_existente | False | False | igual |
| C04 | medio | json✗ | medio | None | compatibilidad_equipo_existente | False | True | mejora |
| C05 | medio | medio | medio | marca_con_equivalente | compatibilidad_equipo_existente | True | True | igual |
| C06 | medio | medio | medio | marca_con_equivalente | compatibilidad_equipo_existente | True | True | igual |
| C07 | medio | medio | medio | marca_con_equivalente | compatibilidad_equipo_existente | True | True | igual |
| C08 | bajo | medio | medio | marca_con_equivalente | compatibilidad_equipo_existente | False | False | igual |
| C09 | bajo | medio | medio | marca_con_equivalente | compatibilidad_equipo_existente | False | False | igual |
| C10 | bajo | medio | medio | marca_con_equivalente | compatibilidad_equipo_existente | False | False | igual |

### Exp. 3 por caso

| id | gold | greedy | greedy_repetible | sampling | moda | estabilidad | acuerdo_con_greedy | etiquetas_distintas | schema_valid_sampling | justificaciones_distintas | acc_sampling | margen_logits |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C01 | alto | medio | True | schema✗ medio bajo schema✗ schema✗ | schema✗ | 0.6 | 0.2 | 3 | 0.4 | 5 | 0.0 | 0.3336 |
| C02 | alto | medio | True | schema✗ medio schema✗ schema✗ schema✗ | schema✗ | 0.8 | 0.2 | 2 | 0.2 | 5 | 0.0 | 0.4477 |
| C03 | alto | medio | True | schema✗ schema✗ bajo schema✗ schema✗ | schema✗ | 0.8 | 0.0 | 2 | 0.2 | 5 | 0.0 | 0.3481 |
| C04 | medio | json✗ | True | schema✗ medio bajo schema✗ schema✗ | schema✗ | 0.6 | 0.0 | 3 | 0.4 | 5 | 0.2 | 0.4964 |
| C05 | medio | medio | True | schema✗ schema✗ medio schema✗ json✗ | schema✗ | 0.6 | 0.2 | 3 | 0.2 | 4 | 0.2 | 0.5993 |
| C06 | medio | medio | True | schema✗ medio bajo schema✗ schema✗ | schema✗ | 0.6 | 0.2 | 3 | 0.4 | 5 | 0.2 | 0.4459 |
| C07 | medio | medio | True | schema✗ schema✗ bajo schema✗ schema✗ | schema✗ | 0.8 | 0.0 | 2 | 0.2 | 5 | 0.0 | 0.3468 |
| C08 | bajo | medio | True | schema✗ schema✗ bajo schema✗ schema✗ | schema✗ | 0.8 | 0.0 | 2 | 0.2 | 5 | 0.2 | 0.1772 |
| C09 | bajo | medio | True | schema✗ schema✗ bajo schema✗ schema✗ | schema✗ | 0.8 | 0.0 | 2 | 0.2 | 5 | 0.2 | 0.3155 |
| C10 | bajo | medio | True | schema✗ schema✗ bajo schema✗ schema✗ | schema✗ | 0.8 | 0.0 | 2 | 0.2 | 5 | 0.2 | 0.4726 |

### Exp. 3 agregado

```json
{
  "acuerdo_entre_casos_misma_semilla": 0.86,
  "etiqueta_modal_por_semilla": {
    "0": "schema✗",
    "1": "schema✗",
    "2": "bajo",
    "3": "schema✗",
    "4": "schema✗"
  },
  "greedy_schema_valid_rate": 0.9,
  "sampling_schema_valid_rate": 0.26,
  "greedy_accuracy": 0.3,
  "sampling_accuracy_media": 0.12,
  "greedy_repetible_casos": 10,
  "estabilidad_media": 0.72,
  "acuerdo_con_greedy_medio": 0.08,
  "casos_con_2_o_mas_etiquetas": 10,
  "justificaciones_distintas_media": 4.9,
  "corr_margen_vs_estabilidad": -0.426
}
```

## Sondeo de logits

| prompt | contexto | id | gold_riesgo | p_etiqueta_normalizada | margen_top1_top2 | p_primer_token_T1.0 | p_primer_token_T0.8 |
|---|---|---|---|---|---|---|---|
| P0 | C0 | C01 | alto | {'alto': 0.8344, 'medio': 0.0924, 'bajo': 0.0732} | 0.742 | {'alto': 0.6673, 'medio': 0.0865, 'bajo': 0.0788} | {'alto': 0.8032, 'medio': 0.0625, 'bajo': 0.0556} |
| P0 | C0 | C02 | alto | {'alto': 0.7891, 'medio': 0.1059, 'bajo': 0.105} | 0.6832 | {'alto': 0.623, 'medio': 0.09, 'bajo': 0.1007} | {'alto': 0.7613, 'medio': 0.0678, 'bajo': 0.0781} |
| P0 | C0 | C03 | alto | {'alto': 0.9135, 'medio': 0.0467, 'bajo': 0.0398} | 0.8668 | {'alto': 0.7982, 'medio': 0.0449, 'bajo': 0.0447} | {'alto': 0.9025, 'medio': 0.0247, 'bajo': 0.0246} |
| P0 | C0 | C04 | medio | {'alto': 0.8727, 'medio': 0.0774, 'bajo': 0.05} | 0.7953 | {'alto': 0.7405, 'medio': 0.0731, 'bajo': 0.0572} | {'alto': 0.8595, 'medio': 0.0476, 'bajo': 0.035} |
| P0 | C0 | C05 | medio | {'alto': 0.8747, 'medio': 0.075, 'bajo': 0.0502} | 0.7997 | {'alto': 0.7395, 'medio': 0.0706, 'bajo': 0.0582} | {'alto': 0.8582, 'medio': 0.0455, 'bajo': 0.0358} |
| P0 | C0 | C06 | medio | {'alto': 0.8348, 'medio': 0.0798, 'bajo': 0.0854} | 0.7494 | {'alto': 0.6706, 'medio': 0.0704, 'bajo': 0.0843} | {'alto': 0.805, 'medio': 0.0481, 'bajo': 0.0603} |
| P0 | C0 | C07 | medio | {'alto': 0.8606, 'medio': 0.0772, 'bajo': 0.0622} | 0.7834 | {'alto': 0.6978, 'medio': 0.073, 'bajo': 0.0656} | {'alto': 0.8275, 'medio': 0.0492, 'bajo': 0.0431} |
| P0 | C0 | C08 | bajo | {'alto': 0.925, 'medio': 0.0402, 'bajo': 0.0348} | 0.8848 | {'alto': 0.8147, 'medio': 0.0416, 'bajo': 0.0411} | {'alto': 0.9139, 'medio': 0.0222, 'bajo': 0.0219} |
| P0 | C0 | C09 | bajo | {'alto': 0.9061, 'medio': 0.0442, 'bajo': 0.0497} | 0.8564 | {'alto': 0.7748, 'medio': 0.0443, 'bajo': 0.0565} | {'alto': 0.8859, 'medio': 0.0247, 'bajo': 0.0336} |
| P0 | C0 | C10 | bajo | {'alto': 0.892, 'medio': 0.0453, 'bajo': 0.0627} | 0.8293 | {'alto': 0.7628, 'medio': 0.0438, 'bajo': 0.0695} | {'alto': 0.8757, 'medio': 0.0246, 'bajo': 0.0438} |
| P1 | C0 | C01 | alto | {'alto': 0.2791, 'medio': 0.6127, 'bajo': 0.1082} | 0.3336 | {'alto': 0.2034, 'medio': 0.5487, 'bajo': 0.092} | {'alto': 0.1941, 'medio': 0.6714, 'bajo': 0.072} |
| P1 | C0 | C02 | alto | {'alto': 0.2196, 'medio': 0.6673, 'bajo': 0.1131} | 0.4477 | {'alto': 0.1619, 'medio': 0.5799, 'bajo': 0.0933} | {'alto': 0.145, 'medio': 0.7148, 'bajo': 0.0728} |
| P1 | C0 | C03 | alto | {'alto': 0.2806, 'medio': 0.6287, 'bajo': 0.0908} | 0.3481 | {'alto': 0.2154, 'medio': 0.5677, 'bajo': 0.0757} | {'alto': 0.204, 'medio': 0.6852, 'bajo': 0.0552} |
| P1 | C0 | C04 | medio | {'alto': 0.2091, 'medio': 0.7055, 'bajo': 0.0854} | 0.4964 | {'alto': 0.1571, 'medio': 0.6318, 'bajo': 0.0725} | {'alto': 0.134, 'medio': 0.7632, 'bajo': 0.051} |
| P1 | C0 | C05 | medio | {'alto': 0.1584, 'medio': 0.7577, 'bajo': 0.0838} | 0.5993 | {'alto': 0.1199, 'medio': 0.6792, 'bajo': 0.0696} | {'alto': 0.093, 'medio': 0.8129, 'bajo': 0.0472} |
| P1 | C0 | C06 | medio | {'alto': 0.2344, 'medio': 0.6803, 'bajo': 0.0852} | 0.4459 | {'alto': 0.1758, 'medio': 0.5993, 'bajo': 0.0756} | {'alto': 0.1574, 'medio': 0.729, 'bajo': 0.0548} |
| P1 | C0 | C07 | medio | {'alto': 0.2745, 'medio': 0.6213, 'bajo': 0.1042} | 0.3468 | {'alto': 0.208, 'medio': 0.5579, 'bajo': 0.0884} | {'alto': 0.1972, 'medio': 0.6771, 'bajo': 0.0677} |
| P1 | C0 | C08 | bajo | {'alto': 0.3612, 'medio': 0.5384, 'bajo': 0.1004} | 0.1772 | {'alto': 0.2811, 'medio': 0.4918, 'bajo': 0.0879} | {'alto': 0.2898, 'medio': 0.5831, 'bajo': 0.0677} |
| P1 | C0 | C09 | bajo | {'alto': 0.2919, 'medio': 0.6074, 'bajo': 0.1007} | 0.3155 | {'alto': 0.228, 'medio': 0.5414, 'bajo': 0.0889} | {'alto': 0.2216, 'medio': 0.6532, 'bajo': 0.0682} |
| P1 | C0 | C10 | bajo | {'alto': 0.1993, 'medio': 0.6719, 'bajo': 0.1288} | 0.4726 | {'alto': 0.1505, 'medio': 0.6009, 'bajo': 0.1057} | {'alto': 0.1298, 'medio': 0.7326, 'bajo': 0.0834} |
| P1 | C1 | C01 | alto | {'alto': 0.2584, 'medio': 0.6505, 'bajo': 0.0911} | 0.3921 | {'alto': 0.1889, 'medio': 0.571, 'bajo': 0.0778} | {'alto': 0.1758, 'medio': 0.7006, 'bajo': 0.058} |
| P1 | C1 | C02 | alto | {'alto': 0.2372, 'medio': 0.663, 'bajo': 0.0998} | 0.4258 | {'alto': 0.1775, 'medio': 0.5723, 'bajo': 0.085} | {'alto': 0.163, 'medio': 0.7045, 'bajo': 0.065} |
| P1 | C1 | C03 | alto | {'alto': 0.2001, 'medio': 0.7101, 'bajo': 0.0898} | 0.51 | {'alto': 0.1538, 'medio': 0.6219, 'bajo': 0.0756} | {'alto': 0.132, 'medio': 0.7566, 'bajo': 0.0543} |
| P1 | C1 | C04 | medio | {'alto': 0.1978, 'medio': 0.7461, 'bajo': 0.0562} | 0.5483 | {'alto': 0.1531, 'medio': 0.668, 'bajo': 0.0499} | {'alto': 0.1262, 'medio': 0.7963, 'bajo': 0.0311} |
| P1 | C1 | C05 | medio | {'alto': 0.2003, 'medio': 0.7304, 'bajo': 0.0693} | 0.5301 | {'alto': 0.1557, 'medio': 0.6383, 'bajo': 0.059} | {'alto': 0.1323, 'medio': 0.7716, 'bajo': 0.0393} |
| P1 | C1 | C06 | medio | {'alto': 0.2935, 'medio': 0.6355, 'bajo': 0.0709} | 0.342 | {'alto': 0.223, 'medio': 0.5559, 'bajo': 0.0646} | {'alto': 0.2152, 'medio': 0.6743, 'bajo': 0.0457} |
| P1 | C1 | C07 | medio | {'alto': 0.2301, 'medio': 0.6819, 'bajo': 0.0879} | 0.4518 | {'alto': 0.1733, 'medio': 0.5962, 'bajo': 0.0752} | {'alto': 0.1557, 'medio': 0.7295, 'bajo': 0.0548} |
| P1 | C1 | C08 | bajo | {'alto': 0.3672, 'medio': 0.5421, 'bajo': 0.0906} | 0.1749 | {'alto': 0.2924, 'medio': 0.4815, 'bajo': 0.0806} | {'alto': 0.3061, 'medio': 0.5711, 'bajo': 0.0612} |
| P1 | C1 | C09 | bajo | {'alto': 0.3645, 'medio': 0.5463, 'bajo': 0.0892} | 0.1818 | {'alto': 0.2933, 'medio': 0.4804, 'bajo': 0.0794} | {'alto': 0.3078, 'medio': 0.5703, 'bajo': 0.0601} |
| P1 | C1 | C10 | bajo | {'alto': 0.1751, 'medio': 0.7165, 'bajo': 0.1084} | 0.5414 | {'alto': 0.1335, 'medio': 0.6219, 'bajo': 0.0911} | {'alto': 0.1112, 'medio': 0.761, 'bajo': 0.0689} |
| F1 | C0 | C01 | alto | {'alto': 0.3544, 'medio': 0.5666, 'bajo': 0.079} | 0.2122 | {'alto': 0.3389, 'medio': 0.4321, 'bajo': 0.0817} | {'alto': 0.3662, 'medio': 0.4961, 'bajo': 0.0619} |
| F1 | C0 | C02 | alto | {'alto': 0.3591, 'medio': 0.5472, 'bajo': 0.0937} | 0.1881 | {'alto': 0.3344, 'medio': 0.4156, 'bajo': 0.0932} | {'alto': 0.3645, 'medio': 0.4785, 'bajo': 0.0738} |
| F1 | C0 | C03 | alto | {'alto': 0.3535, 'medio': 0.5727, 'bajo': 0.0738} | 0.2192 | {'alto': 0.3402, 'medio': 0.4437, 'bajo': 0.0744} | {'alto': 0.364, 'medio': 0.5074, 'bajo': 0.0544} |
| F1 | C0 | C04 | medio | {'alto': 0.2963, 'medio': 0.6074, 'bajo': 0.0963} | 0.3111 | {'alto': 0.2853, 'medio': 0.4721, 'bajo': 0.098} | {'alto': 0.2949, 'medio': 0.5535, 'bajo': 0.0776} |
| F1 | C0 | C05 | medio | {'alto': 0.2813, 'medio': 0.6374, 'bajo': 0.0813} | 0.3561 | {'alto': 0.2719, 'medio': 0.497, 'bajo': 0.0847} | {'alto': 0.2753, 'medio': 0.5849, 'bajo': 0.064} |
| F1 | C0 | C06 | medio | {'alto': 0.2848, 'medio': 0.624, 'bajo': 0.0912} | 0.3392 | {'alto': 0.2725, 'medio': 0.4806, 'bajo': 0.0945} | {'alto': 0.2799, 'medio': 0.569, 'bajo': 0.0745} |
| F1 | C0 | C07 | medio | {'alto': 0.3541, 'medio': 0.5536, 'bajo': 0.0923} | 0.1995 | {'alto': 0.333, 'medio': 0.4245, 'bajo': 0.0937} | {'alto': 0.3606, 'medio': 0.4886, 'bajo': 0.0739} |
| F1 | C0 | C08 | bajo | {'alto': 0.3662, 'medio': 0.5495, 'bajo': 0.0843} | 0.1833 | {'alto': 0.3447, 'medio': 0.4237, 'bajo': 0.0854} | {'alto': 0.374, 'medio': 0.484, 'bajo': 0.0653} |
| F1 | C0 | C09 | bajo | {'alto': 0.3431, 'medio': 0.5819, 'bajo': 0.075} | 0.2388 | {'alto': 0.3282, 'medio': 0.4518, 'bajo': 0.0778} | {'alto': 0.3488, 'medio': 0.5202, 'bajo': 0.0577} |
| F1 | C0 | C10 | bajo | {'alto': 0.2765, 'medio': 0.6174, 'bajo': 0.1061} | 0.3409 | {'alto': 0.2665, 'medio': 0.4828, 'bajo': 0.1078} | {'alto': 0.2716, 'medio': 0.571, 'bajo': 0.0877} |

## KV cache

```json
{
  "caso": "C05",
  "prompt": "P1",
  "contexto": "C0",
  "mismo_texto": true,
  "prompt_tokens": 631,
  "n_tokens_generados": 32,
  "aceleracion": 9.44,
  "ms_con_cache": 8035.0,
  "ms_sin_cache": 75818.8
}
```
