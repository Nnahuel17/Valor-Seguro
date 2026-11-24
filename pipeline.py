import json

from ETL import normalizar, limpiar
from EDA import eda
from tooling_business import cargar_arboles, agregar_delitos
from inferencia import predecir_prob, evaluar


def leer_avisos(entrada):
    avisos = entrada.get("avisos", [])
    if isinstance(avisos, dict):
        avisos = [avisos]
    if not avisos:
        raise ValueError("La entrada 'avisos' está vacía.")
    return avisos


def preparar(avisos):
    crudo = normalizar(avisos)
    return limpiar(crudo)


def enriquecer(limpio):
    todos, robos = cargar_arboles()
    limpio = agregar_delitos(limpio, todos, robos)
    limpio = predecir_prob(limpio)
    limpio["evaluacion"] = evaluar(limpio)
    return limpio


def registros(df):
    return json.loads(df.to_json(orient="records"))


def resumen_salida(limpio):
    resumen, por_barrio = eda(limpio)
    return resumen, registros(por_barrio)
