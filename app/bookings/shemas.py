from datetime import date
from pydantic import BaseModel


class SBooking(BaseModel):
    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int

    class Config:
        orm_mode = True


class SBookingAdd(BaseModel):
    id: int
    user_id: int
    room_id: int
    date_from: date
    date_to: date

    class Config:
        orm_mode = True


class SBookingsRooms(BaseModel):
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int
    image_id: int
    name: str
    description: str
    services: list[str]

    class Config:
        orm_mode = True
