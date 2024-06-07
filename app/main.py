from posixpath import abspath, dirname
import sys
from fastapi import FastAPI, Query
import uvicorn
from pydantic import BaseModel
from typing import Optional
from datetime import date
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))

from app.bookings.router import router as router_bookings
from app.users.router import router as router_users
from app.pages.router import router as router_pages
from app.hotels.router import router as router_hotels
from app.hotels.rooms.router import router as router_rooms
from app.images.router import router as router_images


application = FastAPI()

application.mount("/static", StaticFiles(directory="app/static"), "static")

application.include_router(router_users)
application.include_router(router_bookings)
application.include_router(router_hotels)
application.include_router(router_rooms)
application.include_router(router_pages)
application.include_router(router_images)


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


# @application.get("/hotels/{hotel_id}")
# async def get_hotel(hotel_id: int, date_from, date_to):
#     return {"hotel_id": hotel_id, "date_from": date_from, "date_to": date_to}


# @application.get("/hotels")
# async def get_hotels(
#     location: str,
#     date_from: date,
#     date_to: date,
#     has_spa: Optional[bool] = None,
#     stars: Optional[int] = Query(None, ge=1, le=5),
# ) -> list[SHotel]:
#     hotels = [
#         {
#             "address": "ул. Гагарина, 1, Алтай",
#             "name": "Super Hotel",
#             "stars": 5,
#         }
#     ]

#     return hotels


# if __name__ == "__main__":
#     uvicorn.run("app.main:application", host="127.0.0.1", port=8000, reload=True)

# uvicorn app.main:application --reload
