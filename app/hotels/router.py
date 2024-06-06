from datetime import date
from fastapi import APIRouter

from app.hotels.dao import HotelDAO
from app.hotels.shemas import SHotel, SHotels
from app.exceptions import NoHotelsAvailableException, NoSuchHotelException


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


# возвращает список отелей по заданным параметрам, причем в отеле должен быть
# минимум 1 свободный номер
@router.get("/free")
async def get_hotels(
    date_from: date,
    date_to: date,
    location: str = "",
) -> list[SHotels]:

    free_hotels = await HotelDAO.find_all(location, date_from, date_to)
    if not free_hotels:
        raise NoHotelsAvailableException

    return free_hotels


@router.get("/id/{id}")
async def get_hotel_on_id(
    id: int,
) -> list[SHotel]:

    hotel_by_id = await HotelDAO.find_hotel_by_id(id)
    if not hotel_by_id:
        raise NoSuchHotelException

    return hotel_by_id
