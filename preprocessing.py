import numpy as np


def filtrar_outliers(df, embudo):
    # Z-score robusto sobre log(precio por m²), como en el notebook de ANOVA
    df = df.copy()
    df["log_precio_m2"] = np.log(df["precio_m2"])
    mediana = df["log_precio_m2"].median()
    mad = (df["log_precio_m2"] - mediana).abs().median()

    if len(df) < 3 or not mad or np.isnan(mad):
        df["z_robusto"] = 0.0
    else:
        df["z_robusto"] = 0.6745 * (df["log_precio_m2"] - mediana) / mad

    df["revisar_outlier"] = df["z_robusto"].abs() > 3.5
    df = df[df["z_robusto"].abs() <= 10].copy()
    embudo.append(("6. Sin errores groseros (|z| > 10)", len(df)))
    return df, embudo