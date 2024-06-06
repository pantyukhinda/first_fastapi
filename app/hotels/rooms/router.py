from datetime import date
from fastapi import APIRouter

from app.exceptions import NoRoomsAvailableException
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.shemas import SRooms
from app.hotels.router import router


# возвращает список всех номеров определенного отеля
@router.get("/{hotel_id}/rooms")
async def get_rooms(
    hotel_id: int,
    date_from: date,
    date_to: date,
) -> list[SRooms]:
    all_hotel_rooms = await RoomDAO.all_hotel_rooms(hotel_id, date_from, date_to)
    if not all_hotel_rooms:
        raise NoRoomsAvailableException()

    return all_hotel_rooms
