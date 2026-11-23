import math
import pandas as pd
from scipy.stats import spearmanr

MIN_AVISOS_BARRIO = 10


def _limpio(x):
    if x is None:
        return None
    try:
        return None if math.isnan(float(x)) else float(x)
    except (TypeError, ValueError):
        return None


def eda(df):
    rho, p = None, None
    if len(df) >= 3:
        rho_v, p_v = spearmanr(df["delitos_1km"], df["precio_m2"])
        rho, p = _limpio(round(float(rho_v), 3)), _limpio(float(p_v))

    resumen = {
        "avisos": int(len(df)),
        "precio_m2_mediana": _limpio(round(float(df["precio_m2"].median()), 1)),
        "delitos_1km_promedio": _limpio(round(float(df["delitos_1km"].mean()), 1)),
        "spearman_delitos_vs_precio_m2": {"rho": rho, "p": p},
    }
    por_barrio = (df.groupby("barrio")
                    .agg(avisos=("id_aviso", "count"),
                         precio_m2_mediano=("precio_m2", "median"),
                         delitos_1km_prom=("delitos_1km", "mean"))
                    .round(1)
                    .reset_index())
    por_barrio = por_barrio[por_barrio["avisos"] >= MIN_AVISOS_BARRIO]
    return resumen, por_barrio