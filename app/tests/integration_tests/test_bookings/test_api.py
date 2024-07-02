from httpx import AsyncClient
import pytest


@pytest.mark.parametrize(
    "room_id,date_from,date_to,staus_code",
    [
        *[(4, "2030-05-1", "2030-05-15", 200)] * 8,
        (4, "2030-05-1", "2030-05-15", 409),
        (4, "2030-05-1", "2030-05-15", 409),
    ],
)
async def test_add_and_get_booking(
    room_id,
    date_from,
    date_to,
    staus_code,
    authenticated_ac: AsyncClient,
):
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )

    assert response.status_code == staus_code
