from fastapi import APIRouter

from app.bookings.dao import BookingDAO
from app.bookings.shemas import SBooking


router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
async def get_bookings(user):  # -> list[SBooking]:
    return await BookingDAO.find_all()
