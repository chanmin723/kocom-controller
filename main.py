import asyncio, sys, os, logging, time
from kocom_manager import KocomManager
from load_config import LoadConfig
  
async def main():
    loader = LoadConfig()
    config = loader.load()
    while(1):
        try:
            manager = KocomManager(config)
            await manager.start()
        
        except Exception as e:
            logging.error(e)

        finally:
            await manager.close()
            logging.error("Restart after 30s...")
            time.sleep(30)

if __name__ == "__main__":
    if sys.platform.lower() == "win32" or os.name.lower() == "nt":
            from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
            set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
