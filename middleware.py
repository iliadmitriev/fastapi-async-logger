from typing import Callable

from starlette.concurrency import iterate_in_threadpool
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message

from async_logger import system_log


async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {"type": "http.request", "body": body}

    request._receive = receive


async def get_body(request: Request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body


async def log_middleware(request: Request, call_next: Callable) -> Response:
    body = await get_body(request)
    system_log(f"Incoming message via REST. {body.decode()}")
    response = await call_next(request)

    response_body = [chunk async for chunk in response.body_iterator]
    response.body_iterator = iterate_in_threadpool(iter(response_body))
    decoded_body = response_body[0].decode() if response_body else None

    system_log(f"Outgoing message via REST. {decoded_body}")
    return response
