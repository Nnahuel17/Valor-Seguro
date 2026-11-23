import asyncio
import json

from apify import Actor

from ETL import normalizar, limpiar
from EDA import eda
from tooling_business import cargar_arboles, agregar_delitos


async def main():
    async with Actor:
        entrada = await Actor.get_input() or {}
        avisos = entrada.get("avisos", [])
        if isinstance(avisos, dict):
            avisos = [avisos]
        if not avisos:
            raise ValueError("La entrada 'avisos' está vacía.")

        crudo = normalizar(avisos)
        limpio, embudo = limpiar(crudo)
        await Actor.set_value("EMBUDO", embudo)
        Actor.log.info(f"Avisos después de la limpieza: {len(limpio)}")

        if limpio.empty:
            return

        todos, robos = cargar_arboles()
        limpio = agregar_delitos(limpio, todos, robos)

        resumen, por_barrio = eda(limpio)
        await Actor.set_value("EDA_RESUMEN", resumen)
        await Actor.set_value("EDA_BARRIOS", json.loads(por_barrio.to_json(orient="records")))

        await Actor.push_data(json.loads(limpio.to_json(orient="records")))


if __name__ == "__main__":
    asyncio.run(main())