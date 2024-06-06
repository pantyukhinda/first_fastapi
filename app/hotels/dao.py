from datetime import date

from sqlalchemy import Integer, func, insert, delete, select, and_, or_, distinct
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(
        cls,
        location: str,
        date_from: date,
        date_to: date,
    ):

        location = f"%{location}%"

        # WITH booked_rooms AS (
        #     SELECT * FROM bookings
        #     WHERE
        #     (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
        #     (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        #     ),

        # subq_free_hotels AS (
        #     SELECT
        #     hotels.id,
        #     hotels.name,
        #     hotels.location,
        #     hotels.services,
        #     hotels.rooms_quantity,
        #     hotels.image_id,
        #     --booked_rooms.room_id,
        #     --(rooms.quantity - COUNT(booked_rooms.room_id)) AS left_rooms,
        #     SUM(rooms.quantity - COUNT(booked_rooms.room_id)) OVER (PARTITION BY hotels.name) AS rooms_left,
        #     ROW_NUMBER() OVER (PARTITION BY hotels.name) AS row_num_in_group
        #     FROM rooms
        #     LEFT OUTER JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        #     LEFT OUTER JOIN hotels ON hotels.id = rooms.hotel_id
        #     WHERE lower(location) LIKE '%алтай%'
        #     GROUP BY rooms.quantity, booked_rooms.room_id, hotels.id)

        # SELECT
        #     subq_free_hotels.id,
        #     subq_free_hotels.name,
        #     subq_free_hotels.location,
        #     subq_free_hotels.services,
        #     subq_free_hotels.rooms_quantity,
        #     subq_free_hotels.image_id,
        #     subq_free_hotels.rooms_left,
        #     subq_free_hotels.row_num_in_group
        # FROM subq_free_hotels
        # WHERE row_num_in_group = 1

        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings).where(
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to,
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from,
                        ),
                    )
                )
            ).cte("booked_rooms")

            subq_free_hotels = (
                select(
                    Hotels.id,
                    Hotels.name,
                    Hotels.location,
                    Hotels.services,
                    Hotels.rooms_quantity,
                    Hotels.image_id,
                    (func.sum(Rooms.quantity - func.count(booked_rooms.c.room_id)))
                    .over(partition_by=Hotels.name)
                    .label("rooms_left"),
                    func.row_number()
                    .over(partition_by=Hotels.name)
                    .label("row_num_in_group"),
                )
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .join(Hotels, Hotels.id == Rooms.hotel_id, isouter=True)
                .where(Hotels.location.ilike(location))
                .group_by(Rooms.quantity, booked_rooms.c.room_id, Hotels.id)
            ).cte("subq_free_hotels")

            get_free_hotels = (
                select(
                    subq_free_hotels.c.id,
                    subq_free_hotels.c.name,
                    subq_free_hotels.c.location,
                    subq_free_hotels.c.services,
                    subq_free_hotels.c.rooms_quantity,
                    subq_free_hotels.c.image_id,
                    subq_free_hotels.c.rooms_left.cast(Integer),
                )
                .select_from(subq_free_hotels)
                .where(subq_free_hotels.c.row_num_in_group == 1)
            )

            # print(get_free_hotels.compile(engine, compile_kwargs={"literal_binds": True}))
            free_hotels_table = await session.execute(get_free_hotels)
            return free_hotels_table.mappings().all()

    @classmethod
    async def find_hotel_by_id(
        cls,
        id: int,
    ):

        async with async_session_maker() as session:
            get_hotel_by_id = (
                select(
                    Hotels.id,
                    Hotels.name,
                    Hotels.location,
                    Hotels.services,
                    Hotels.rooms_quantity,
                    Hotels.image_id,
                )
                .select_from(Hotels)
                .where(Hotels.id == id)
            )

            hotel_by_id = await session.execute(get_hotel_by_id)
            return hotel_by_id.mappings().all()
