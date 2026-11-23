# Valor-Seguro
Este es un análisis de cómo se relaciona la cantidad de delitos cercanos con el precio por m² de los departamentos en venta en CABA.

## Qué hace el Actor
El Actor de Apify (`valor-seguro`) recibe una lista de avisos de Argenprop, los limpia y calcula cuántos delitos y robos hay a menos de 1 km de cada propiedad.

- **ETL:** normalización de campos, embudo de filas, validaciones y filtro de outliers con z-score robusto.
- **Cruce:** conteo de delitos y robos en un radio de 1 km usando `delitos_muestra.csv`.
- **EDA:** resumen del lote y tabla por barrio, guardados en el key-value store.

## Escenario de Make
![Escenario en Make](captura_escenario.png)

1. Scraper de Argenprop (Capital Federal)
2. Lectura del dataset del scraper
3. Lista de avisos (Array aggregator)
4. Creación del JSON para el Actor
5. Actor `valor-seguro` (ETL + EDA)
6. Lectura del resultado limpio

## Última corrida
| Paso del embudo | Filas |
|---|---|
| Entrada | 50 |
| Sin id_aviso repetido | 50 |
| Con coordenadas | 50 |
| Partido = Capital Federal | 50 |
| Dentro de la caja de CABA | 49 |
| Con superficie y precio válidos | 49 |
| Precio por m² válido | 49 |
| Sin errores groseros (\|z\| > 10) | 49 |

## Limitaciones
- Solo se usan avisos de Capital Federal.
- `zona_riesgo` (terciles de delitos) y `dist_centro_km` se calculan en el análisis, no en el Actor.
- Superficie cubierta y baños vienen dentro de `DatosComunes_s`, y todavía no se extraen bien.
