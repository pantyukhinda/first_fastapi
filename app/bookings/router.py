from datetime import date
from fastapi import APIRouter, Depends, Request
from pydantic import TypeAdapter, parse_obj_as

from app.bookings.dao import BookingDAO
from app.bookings.shemas import SBooking, SBookingAdd, SBookingsRooms
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.exceptions import (
    BookingCannotBeDeletedException,
    NoRoomsAvailableException,
    RoomCannotBeBookedException,
)


router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBooking]:
    return await BookingDAO.find_all(user_id=user.id)


@router.get("/rooms")
async def get_bookings_rooms(
    user: Users = Depends(get_current_user),
) -> list[SBookingsRooms]:
    bookings_rooms = await BookingDAO.find_bookings_rooms(user_id=user.id)
    if not bookings_rooms:
        raise NoRoomsAvailableException
    return bookings_rooms


@router.post("")
async def add_booking(
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
) -> list[SBookingAdd]:

    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBookedException

    booking_dict_adapter = TypeAdapter(list[SBookingAdd])
    booking_dict = booking_dict_adapter.validate_python(booking)
    send_booking_confirmation_email.delay(booking_dict, user.email)
    return booking_dict


@router.delete("/{id}", status_code=204)
async def delete_bookings(
    id: int,
    user: Users = Depends(get_current_user),
):
    booking_delete = await BookingDAO.delete(id, user_id=user.id)
    if not booking_delete:
        raise BookingCannotBeDeletedException
    return booking_delete
