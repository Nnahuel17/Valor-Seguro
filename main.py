import asyncio

from apify import Actor

from pipeline import leer_avisos, preparar, enriquecer, registros, resumen_salida


async def main():
    async with Actor:
        entrada = await Actor.get_input() or {}
        avisos = leer_avisos(entrada)

        limpio, embudo = preparar(avisos)
        await Actor.set_value("EMBUDO", embudo)
        Actor.log.info(f"Avisos después de la limpieza: {len(limpio)}")

        if limpio.empty:
            return

        limpio = enriquecer(limpio)

        resumen, barrios = resumen_salida(limpio)
        await Actor.set_value("EDA_RESUMEN", resumen)
        await Actor.set_value("EDA_BARRIOS", barrios)

        await Actor.push_data(registros(limpio))


if __name__ == "__main__":
    asyncio.run(main())
