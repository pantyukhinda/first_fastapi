from fastapi import APIRouter, Depends, Request

from app.bookings.dao import BookingDAO
from app.bookings.shemas import SBooking
from app.users.dependencies import get_current_user
from app.users.models import Users


router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)):  # -> list[SBooking]:
    return await BookingDAO.find_all(user_id=1)
