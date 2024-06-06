from typing import Optional
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Rooms(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    name: Mapped[str]
    description: Mapped[Optional[str]]
    services: Mapped[list[str]] = mapped_column(JSON)
    price: Mapped[int]
    quantity: Mapped[int]
    image_id: Mapped[int]
