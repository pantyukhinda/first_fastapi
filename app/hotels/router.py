from datetime import date
from fastapi import APIRouter

from app.hotels.dao import HotelDAO
from app.hotels.shemas import SHotels
from app.exceptions import NoHotelsAvailableException


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@router.get("/free")
async def get_hotels(
    location: str,
    date_from: date,
    date_to: date,
):

    free_hotels_table = await HotelDAO.find_all(location, date_from, date_to)
    if not free_hotels_table:
        raise NoHotelsAvailableException
