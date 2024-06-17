import asyncio
from datetime import date, datetime
from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache
from pydantic import TypeAdapter

from app.hotels.dao import HotelDAO
from app.hotels.shemas import SHotel, SHotels
from app.exceptions import NoHotelsAvailableException, NoSuchHotelException


router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


# возвращает список отелей по заданным параметрам, причем в отеле должен быть
# минимум 1 свободный номер
@router.get("/{location}")
@cache(expire=60)
async def get_hotels(
    date_from: date = Query(..., description=f"Например {datetime.now().date()}"),
    date_to: date = Query(..., description=f"Например {datetime.now().date()}"),
    location: str = "",
):

    await asyncio.sleep(3)
    free_hotels = await HotelDAO.find_all(location, date_from, date_to)
    hotels_list_adapter = TypeAdapter(list[SHotels])
    free_hotels_json = hotels_list_adapter.validate_python(free_hotels)
    if not free_hotels:
        raise NoHotelsAvailableException

    return free_hotels_json


@router.get("/id/{id}")
async def get_hotel_on_id(
    id: int,
) -> list[SHotel]:

    hotel_by_id = await HotelDAO.find_hotel_by_id(id)
    if not hotel_by_id:
        raise NoSuchHotelException

    return hotel_by_id
