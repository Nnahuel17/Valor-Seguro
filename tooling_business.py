import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

RUTA_DELITOS = "delitos_muestra.csv"
RADIO_TIERRA_M = 6371000
RADIO_M = 1000


def cargar_arboles():
    d = pd.read_csv(RUTA_DELITOS).dropna(subset=["Latitud", "Longitud"])
    todos = BallTree(np.radians(d[["Latitud", "Longitud"]].values), metric="haversine")
    robos = d[d["Tipo"].isin(["Robo", "Robo automotor"])]
    arbol_robos = BallTree(np.radians(robos[["Latitud", "Longitud"]].values), metric="haversine")
    return todos, arbol_robos


def agregar_delitos(df, arbol_todos, arbol_robos):
    pts = np.radians(df[["lat", "lon"]].values)
    r = RADIO_M / RADIO_TIERRA_M
    df["delitos_1km"] = arbol_todos.query_radius(pts, r=r, count_only=True)
    df["robos_1km"] = arbol_robos.query_radius(pts, r=r, count_only=True)
    return df