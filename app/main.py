from fastapi import FastAPI, Depends
from fastapi.middleware.gzip import GZipMiddleware
from internal.database import Database
from controllers.pulsar_controller import router as pulsar_router
from controllers.health_controller import router as health_router
from internal.config import AppConfig
from internal.middlewares import token_verification as token_verification
from worker.worker import Worker
from galaxy.galaxy import Galaxy
import uvicorn

def create_app(config: AppConfig) -> FastAPI:
    app = FastAPI(docs_url="/api/pulsar/docs")

    database = Database(config)
    app.state.db = database.connect()

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    verify_token = token_verification(config)
    app.include_router(health_router)
    app.include_router(pulsar_router, dependencies=[Depends(verify_token)])

    return app

config = AppConfig()
app = create_app(config)

def main():
    galaxy = Galaxy(config)
    worker = Worker(app, galaxy)
    worker.start()

    addr = f"{config.server.host}:{config.server.port}"
    print(f"Listening on http://{addr}")
    try:
        uvicorn.run(
            "main:app",
            log_level="trace",
            host=config.server.host,
            port=config.server.port,
        )
    except:
        worker.join()
        worker.stop()
        raise 

if __name__ == "__main__":
    main()
