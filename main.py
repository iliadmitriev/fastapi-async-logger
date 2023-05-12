import asyncio
import json
from contextlib import asynccontextmanager
from functools import partial

from fastapi import FastAPI
from hypercorn import Config
from hypercorn.asyncio import serve
from starlette.requests import Request

from async_logger import async_logger, system_log
from middleware import log_middleware


@asynccontextmanager
async def main_startup(app: FastAPI):
    asyncio.create_task(async_logger.run_loop())
    yield
    await async_logger.finish_loop()


app = FastAPI(lifespan=main_startup)
append_middleware = app.middleware("http")
append_middleware(partial(log_middleware))


@app.post("/healthcheck")
async def healthcheck(request: Request):
    data = await request.json()
    system_log(json.dumps(data))
    return data


if __name__ == '__main__':
    asyncio.run(serve(app, config=Config()))
