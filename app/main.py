"""Project for fastapi education"""

"""Вторая строка комментария"""

"""Третья строка комментария"""

"""Четвертая строка комментария для третьей ветки"""

from fastapi import FastAPI, Query
import uvicorn
from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.bookings.router import router as router_bookings

app = FastAPI()

app.include_router(router_bookings)


class SBooking(BaseModel):
    room_id: int
    date_from: date
    date_to: date


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


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


@app.get("/hotels/{hotel_id}")
async def get_hotel(hotel_id: int, date_from, date_to):
    return {"hotel_id": hotel_id, "date_from": date_from, "date_to": date_to}


@app.get("/hotels")
async def get_hotels(
    location: str,
    date_from: date,
    date_to: date,
    has_spa: Optional[bool] = None,
    stars: Optional[int] = Query(None, ge=1, le=5),
) -> list[SHotel]:
    hotels = [
        {
            "address": "ул. Гагарина, 1, Алтай",
            "name": "Super Hotel",
            "stars": 5,
        }
    ]

    return hotels


@app.post("/bookings")
async def add_booking(booking: SBooking):
    pass


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# uvicorn app.main:app --reload
