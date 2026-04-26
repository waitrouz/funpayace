import asyncio
import logging
import os
from funpayace import FunpayAce, FunpayConfig

logging.basicConfig(level=logging.INFO)

GOLDEN_KEY = os.getenv("GOLDEN_KEY")
GAME_ID = int(os.getenv("GAME_ID", "41"))
NODE_ID = int(os.getenv("NODE_ID", "81"))
PORT = int(os.getenv("PORT", "10000"))

async def main():
    
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
        # Запускаем фоновые процессы
        client.start_forever_online_task()
        client.start_lot_auto_boost_task(GAME_ID, NODE_ID)

        # Периодический опрос баланса
        try:
            while True:
                try:
                    balance = await client.get_balance()
                    print("Баланс:", balance)
                except Exception as e:
                    logging.exception("Не удалось получить баланс: %s", e)
                await asyncio.sleep(30)
        finally:
            await client.cancel_background_tasks()
            await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
