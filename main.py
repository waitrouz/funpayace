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

    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"Health check запущен на порту {PORT}")

    client = FunpayAce(golden_key=GOLDEN_KEY, config=FunpayConfig())
    async with client:
        client.start_forever_online_task()
        client.start_lot_auto_boost_task(GAME_ID, NODE_ID)

        try:
            while True:
                try:
                    balance = await client.get_balance()
                    logger.info("Баланс: %s", balance)
                except Exception as e:
                    logger.exception("Ошибка получения баланса: %s", e)
                await asyncio.sleep(30)
        finally:
            await client.cancel_background_tasks()
            await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
