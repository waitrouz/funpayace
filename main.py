import asyncio
import logging
import os
from aiohttp import web
from funpayace import FunpayAce, FunpayConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

GOLDEN_KEY = os.getenv("GOLDEN_KEY")
GAME_ID = int(os.getenv("GAME_ID", "41"))
NODE_ID = int(os.getenv("NODE_ID", "81"))
PORT = int(os.getenv("PORT", "10000"))

async def health_handler(request):
    return web.Response(text="OK")

async def main():
    if not GOLDEN_KEY:
        logger.error("GOLDEN_KEY не задан в переменных окружения!")
        return

    # Запуск health check сервера
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Health check запущен на порту {PORT}")

    # Запуск автоподнятия лотов
    client = FunpayAce(golden_key=GOLDEN_KEY, config=FunpayConfig())
    async with client:
        client.start_lot_auto_boost_task(GAME_ID, NODE_ID)
        logger.info(f"Автоподнятие лотов запущено для GAME_ID={GAME_ID}, NODE_ID={NODE_ID}")

        # Держим приложение запущенным, пока работает автоподнятие
        try:
            while True:
                await asyncio.sleep(60)
        finally:
            await client.cancel_background_tasks()
            await runner.cleanup()
            logger.info("Приложение завершено")

if __name__ == "__main__":
    asyncio.run(main())
