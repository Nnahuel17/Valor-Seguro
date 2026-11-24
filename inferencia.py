import gzip
import os
import pickle

import numpy as np
import pandas as pd

RUTA_MODELO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelo_precio_m2.pkl.gz")
_paquete = None


def cargar_paquete():
    global _paquete
    if _paquete is None:
        if not os.path.exists(RUTA_MODELO):
            raise FileNotFoundError(
                f"Falta el modelo en {RUTA_MODELO}. Debe estar incluido en el Actor; no se descarga."
            )
        with gzip.open(RUTA_MODELO, "rb") as f:
            _paquete = pickle.load(f)
    return _paquete


def predecir_prob(df):
    paquete = cargar_paquete()
    X = df.copy()
    X["barrio"] = X["barrio"].fillna("sin_barrio").astype(str)
    X["ambientes"] = pd.to_numeric(X["ambientes"], errors="coerce")
    X["banos"] = pd.to_numeric(X["banos"], errors="coerce")
    X["prob_precio_alto"] = paquete["modelo"].predict_proba(X[paquete["features"]])[:, 1]
    return X


def evaluar(df):
    paquete = cargar_paquete()
    real_alto = df["precio_m2"] > paquete["umbral_usd_m2"]
    caro = real_alto & (df["prob_precio_alto"] < paquete["umbral_p_bajo"])
    barato = (~real_alto) & (df["prob_precio_alto"] > paquete["umbral_p_alto"])
    return np.select([caro, barato],
                     ["Caro para su zona", "Barato para su zona"],
                     default="En línea con su zona")
