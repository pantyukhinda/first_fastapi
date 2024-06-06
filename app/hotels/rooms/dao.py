from datetime import date, datetime
from sqlalchemy import Integer, Float, func, insert, delete, select, and_, or_, distinct


from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker, engine


class RoomDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def all_hotel_rooms(
        cls,
        hotel_id: str,
        date_from: date,
        date_to: date,
    ):

        delta = date_to - date_from

        # date_from = datetime.fromisoformat(date_from)
        # date_to = datetime.fromisoformat(date_to)

        # WITH booked_rooms AS  (
        # SELECT
        # bookings.id AS id,
        # bookings.room_id AS room_id,
        # bookings.user_id AS user_id,
        # bookings.date_from AS date_from,
        # bookings.date_to AS date_to,
        # bookings.price AS price,
        # bookings.total_cost AS total_cost,
        # bookings.total_days AS total_days
        # FROM bookings
        # WHERE bookings.date_from >= '2023-05-15' AND bookings.date_from <= '2023-06-20'
        # OR bookings.date_from <= '2023-05-15' AND bookings.date_to > '2023-05-15')

        # SELECT
        # rooms.id,
        # rooms.hotel_id,
        # rooms.name,
        # rooms.description,
        # rooms.services,
        # rooms.price,
        # rooms.quantity,
        # rooms.image_id,
        # (rooms.price * (SELECT DATE_PART('day', '2023-06-20'::timestamp - '2023-05-15'::timestamp))::INT) AS total_cost,
        # (rooms.quantity - COUNT(rooms.id)::INT) AS rooms_left
        # FROM rooms
        # LEFT OUTER JOIN bookings ON bookings.room_id = rooms.id
        # WHERE rooms.hotel_id = 1
        # GROUP BY rooms.id, bookings.room_id
        # ORDER BY rooms.id

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

            get_all_hotel_rooms = (
                select(
                    Rooms.id,
                    Rooms.hotel_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                    Rooms.price,
                    Rooms.quantity,
                    Rooms.image_id,
                    (Rooms.price * delta.days).cast(Float).label("total_cost"),
                    (Rooms.quantity - func.count(Rooms.id))
                    .cast(Integer)
                    .label("rooms_left"),
                )
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .where(Rooms.hotel_id == hotel_id)
                .group_by(Rooms.id, booked_rooms.c.room_id)
                .order_by(Rooms.id)
            )
            # print(
            #     get_all_hotel_rooms.compile(engine, compile_kwargs={"literal_binds": True})
            # )
            all_hotels_rooms = await session.execute(get_all_hotel_rooms)
            return all_hotels_rooms.mappings().all()
