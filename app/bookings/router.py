from fastapi import APIRouter


router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


@router.get("")
def get_bookings():
    pass


@router.get("/{booking_id}")
def get_bookings2(booking_id):
    pass
