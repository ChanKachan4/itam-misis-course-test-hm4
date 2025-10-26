import time
from typing import Callable, Awaitable
from fastapi import FastAPI, HTTPException, Response, status, Request, responses
from pydantic import BaseModel, validator
from services.link_service import LinkService
import requests
from loguru import logger


def create_app() -> FastAPI:
    app = FastAPI()
    short_link_service = LinkService()

    @app.exception_handler(Exception)
    async def global_exeption(request: Request, exc: Exception):
        logger.error(f"Error: {exc}")

        return responses.JSONResponse(
            status_code=500,
            content={
                "message": "Произошла ошибка на сервере",
                "error": str(exc)
            }
        )

    class PutLink(BaseModel):
        link: str

        @validator("link")
        def validate_missed_protocol(cls, value: str) -> str:
            if not value.startswith(("https://", "http://")):
                value = "https://" + value
            return value

        @validator("link")
        def validate_link(cls, value: str) -> str:
            if "localhost" in value or "127.0.0.1" in value:
                return value

            try:
                response = requests.get(value)
                if response.status_code > 400:
                    raise ValueError(f"Ошибка {response.status_code}")

            except requests.exceptions.RequestException as e:
                raise ValueError(f"Невозможно перейти по ссылке: {str(e)}")

            return value

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        t0 = time.time()

        response = await call_next(request)

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        response.headers["X-Latency"] = str(elapsed_ms)
        logger.debug("{} {} done in {}ms", request.method, request.url.path, elapsed_ms)

        return response

    def _service_link_to_real(short_link: str) -> str:
        return f"http://localhost:8000/{short_link}"

    @app.post("/link")
    def create_link(put_link_request: PutLink) -> PutLink:
        short_link = short_link_service.create_link(put_link_request.link)
        return PutLink(link=_service_link_to_real(short_link))

    @app.get("/{link}")
    def get_link(link: str) -> Response:
        real_link = short_link_service.get_real_link(link)

        if real_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found:(")

        return Response(status_code=status.HTTP_301_MOVED_PERMANENTLY, headers={"Location": real_link})

    return app
