import json

import numpy as np
import pandas as pd

from preprocessing import filtrar_outliers

CAJA_LAT = (-34.71, -34.52)
CAJA_LON = (-58.54, -58.33)

MAPA = {
    "IdAviso": "id_aviso",
    "Barrio_t": "barrio",
    "Partido_t": "partido",
    "Direccion_Latitud_d": "lat",
    "Direccion_Longitud_d": "lon",
    "MontoNormalizado_i": "precio_usd",
    "SuperficieTotal_d": "sup_total",
    "CantidadAmbientes_i": "ambientes",
    "CantidadDormitorios_i": "dormitorios",
    "Expensas_i": "expensas_ars",
}
NUMERICAS = ["lat", "lon", "precio_usd", "sup_total", "sup_cubierta", "ambientes",
             "dormitorios", "banos", "expensas_ars"]


def extraer_dato(df, etiquetas):
    cols_ley = [c for c in df.columns if c.startswith("DatosComunes_s/") and c.endswith("/Leyenda")]
    resultado = pd.Series(np.nan, index=df.index, dtype=object)
    for c_ley in cols_ley:
        c_val = c_ley.replace("/Leyenda", "/Valor")
        if c_val not in df.columns:
            continue
        coincide = df[c_ley].astype(str).str.strip().str.lower().isin(etiquetas)
        resultado = resultado.fillna(df[c_val].where(coincide))
    return resultado


def normalizar(avisos):
    avisos = [json.loads(a) if isinstance(a, str) else a for a in avisos]
    df = pd.DataFrame(avisos)
    df = df.rename(columns={k: v for k, v in MAPA.items() if k in df.columns})

    sup_cub = (extraer_dato(df, ["sup. cubierta"])
               .astype(str).str.extract(r"(\d+(?:[.,]\d+)?)")[0]
               .str.replace(",", ".").astype(float))
    banos = pd.to_numeric(extraer_dato(df, ["baños"]), errors="coerce")

    for c in ["id_aviso", "barrio", "partido", "lat", "lon", "precio_usd", "sup_total",
              "sup_cubierta", "ambientes", "dormitorios", "banos", "expensas_ars"]:
        if c not in df.columns:
            df[c] = np.nan

    df["sup_cubierta"] = df["sup_cubierta"].fillna(sup_cub)
    df["banos"] = df["banos"].fillna(banos)
    for c in NUMERICAS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def limpiar(df):
    embudo = [("0. Entrada", len(df))]

    df = df.drop_duplicates("id_aviso")
    embudo.append(("1. Sin id_aviso repetido", len(df)))

    df = df.dropna(subset=["lat", "lon"])
    embudo.append(("2. Con coordenadas", len(df)))

    df = df[df["partido"].astype(str).str.contains("capital", case=False, na=False)].copy()
    embudo.append(("3a. Partido = Capital Federal", len(df)))

    df = df[df["lat"].between(*CAJA_LAT) & df["lon"].between(*CAJA_LON)].copy()
    embudo.append(("3b. Dentro de la caja de CABA", len(df)))

    df["sup_total"] = df["sup_total"].fillna(df["sup_cubierta"])
    df.loc[df["sup_total"] <= 0, "sup_total"] = np.nan
    df = df.dropna(subset=["sup_total", "precio_usd"])
    df = df[df["precio_usd"] > 0].copy()
    embudo.append(("4. Con superficie y precio válidos", len(df)))

    df["precio_m2"] = df["precio_usd"] / df["sup_total"]
    df.loc[df["banos"] == 0, "banos"] = np.nan
    df = df[df["precio_m2"] > 0].copy()
    embudo.append(("5. Precio por m² válido", len(df)))

    df, embudo = filtrar_outliers(df, embudo)
    return df.reset_index(drop=True), embudo