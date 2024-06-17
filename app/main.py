from posixpath import abspath, dirname
import sys
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Optional
from datetime import date
from fastapi.staticfiles import StaticFiles

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from contextlib import asynccontextmanager

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))

from app.bookings.router import router as router_bookings
from app.users.router import router as router_users
from app.pages.router import router as router_pages
from app.hotels.router import router as router_hotels
from app.hotels.rooms.router import router as router_rooms
from app.images.router import router as router_images
from app.config import settings


@asynccontextmanager
async def lifespan(application: FastAPI):
    # при запуске
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield
    # при выключении


application = FastAPI(lifespan=lifespan)


application.mount("/static", StaticFiles(directory="app/static"), "static")

application.include_router(router_users)
application.include_router(router_bookings)
application.include_router(router_hotels)
application.include_router(router_rooms)
application.include_router(router_pages)
application.include_router(router_images)

origins = [
    "http://localhost:8000",
]

application.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)


class SHotel(BaseModel):
    address: str
    name: str
    stars: int


class SHotelsSearchArgs:
    def __init__(
        self,
        location: str,
        date_from: date,
        date_to: date,
        has_spa: Optional[bool] = None,
        stars: Optional[int] = Query(None, ge=1, le=5),
    ):
        self.location = location
        self.date_from = date_from
        self.date_to = date_to
        self.has_spa = has_spa
        self.stars = stars


@application.get("/")
async def root():
    return {"message": "Hello, world!"}


# if __name__ == "__main__":
#     uvicorn.run("app.main:application", host="127.0.0.1", port=8000, reload=True)

# uvicorn app.main:application --reload
