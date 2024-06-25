from datetime import date


from sqlalchemy import func, insert, delete, select, and_, or_
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker, engine
from app.hotels.rooms.models import Rooms


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):

        # WITH booked_rooms AS (
        #     SELECT * FROM bookings
        #     WHERE room_id = 1 AND
        #     (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
        #     (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        # )

        # SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        # LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        # WHERE rooms.id = 1
        # GROUP BY rooms.quantity, booked_rooms.room_id

        async with async_session_maker() as session:
            booked_rooms = (
                select(Bookings)
                .where(
                    and_(
                        Bookings.room_id == room_id,
                        or_(
                            and_(
                                Bookings.date_from >= date_from,
                                Bookings.date_from <= date_to,
                            ),
                            and_(
                                Bookings.date_from <= date_from,
                                Bookings.date_to > date_from,
                            ),
                        ),
                    )
                )
                .cte("booked_rooms")
            )

            get_rooms_left = (
                select(
                    (Rooms.quantity - func.count(booked_rooms.c.room_id)).label(
                        "rooms_left"
                    )
                )
                .select_from(Rooms)
                .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                .where(Rooms.id == room_id)
                .group_by(Rooms.quantity, booked_rooms.c.room_id)
            )

            # print(
            #     get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True})
            # )

            rooms_left = await session.execute(get_rooms_left)
            rooms_left: int = rooms_left.scalar()

            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = (
                    insert(Bookings)
                    .values(
                        room_id=room_id,
                        user_id=user_id,
                        date_from=date_from,
                        date_to=date_to,
                        price=price,
                    )
                    .returning(
                        Bookings.id,
                        Bookings.user_id,
                        Bookings.room_id,
                        Bookings.date_from,
                        Bookings.date_to,
                    )
                )

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.mappings().one()

            else:
                return None

    @classmethod
    async def delete(cls, id: int, user_id: int):
        async with async_session_maker() as session:

            #         SELECT id
            #         FROM public.bookings
            #         WHERE user_id = 3
            find_booking = (
                select(Bookings.id)
                .select_from(Bookings)
                .where(and_((Bookings.user_id == user_id), (Bookings.id == id)))
            )
            booking = await session.execute(find_booking)
            booking: int = booking.mappings().all()
            print(booking)

            if booking:
                delete_user_bookings = delete(Bookings).where(
                    and_((Bookings.user_id == user_id), (Bookings.id == id))
                )
                await session.execute(delete_user_bookings)
                await session.commit()
                return True
            else:
                return None

    @classmethod
    async def find_bookings_rooms(
        cls,
        user_id: int,
    ):

        # SELECT
        #     bookings.room_id,
        #     bookings.user_id,
        #     bookings.date_from,
        #     bookings.date_to,
        #     bookings.price,
        #     bookings.total_cost,
        #     bookings.total_days,
        #     rooms.image_id,
        #     rooms.name,
        #     rooms.description,
        #     rooms.services
        # FROM bookings
        # JOIN rooms ON rooms.id = bookings.room_id
        # WHERE bookings.user_id = 3

        async with async_session_maker() as session:
            get_all_bookings_rooms = (
                select(
                    Bookings.room_id,
                    Bookings.user_id,
                    Bookings.date_from,
                    Bookings.date_to,
                    Bookings.price,
                    Bookings.total_cost,
                    Bookings.total_days,
                    Rooms.image_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                )
                .select_from(Bookings)
                .join(Rooms, Rooms.id == Bookings.room_id)
                .where(Bookings.user_id == user_id)
            )

            # print(
            #     get_all_bookings_rooms.compile(
            #         engine, compile_kwargs={"literal_binds": True}
            #     )
            # )

            all_bookings_rooms = await session.execute(get_all_bookings_rooms)
            return all_bookings_rooms.mappings().all()
