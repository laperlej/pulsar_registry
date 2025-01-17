from fastapi import FastAPI, Depends
from fastapi.middleware.gzip import GZipMiddleware
from app.internal.database import Database
from app.controllers.pulsar_controller import router as pulsar_router
from app.controllers.health_controller import router as health_router
from app.internal.config import AppConfig
from app.internal.middlewares import token_verification as token_verification
import uvicorn

def create_app(config: AppConfig) -> FastAPI:
    app = FastAPI()

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

    addr = f"{config.server.host}:{config.server.port}"
    print(f"Listening on http://{addr}")
    uvicorn.run(
        "app.main:app",
        host=config.server.host,
        port=config.server.port,
    )

if __name__ == "__main__":
    main()
