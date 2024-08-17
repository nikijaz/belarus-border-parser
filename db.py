from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Engine, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

from utils import BorderInfo


class Base(DeclarativeBase): pass


class Border(Base):
    __tablename__ = "borders"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    crossings: Mapped[list["Crossing"]] = relationship(back_populates="border")


class VehicleType(Base):
    __tablename__ = "vehicle_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    crossings: Mapped[list["Crossing"]] = relationship(back_populates="vehicle_type")


class LicensePlate(Base):
    __tablename__ = "license_plates"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(unique=True)
    crossings: Mapped[list["Crossing"]] = relationship(back_populates="license_plate")


class Crossing(Base):
    __tablename__ = "crossings"

    id: Mapped[int] = mapped_column(primary_key=True)
    border_id: Mapped[int] = mapped_column(ForeignKey("borders.id"))
    border: Mapped["Border"] = relationship(back_populates="crossings")
    license_plate_id: Mapped[int] = mapped_column(ForeignKey("license_plates.id"))
    license_plate: Mapped["LicensePlate"] = relationship(back_populates="crossings")
    vehicle_type_id: Mapped[int] = mapped_column(ForeignKey("vehicle_types.id"))
    vehicle_type: Mapped["VehicleType"] = relationship(back_populates="crossings")
    priority: Mapped[bool]
    arrived_at: Mapped[datetime]
    left_at: Mapped[Optional[datetime]]


def init_db_connection() -> Engine:
    engine: Engine = create_engine("sqlite:///sqlite.db")
    engine.connect()
    Base.metadata.create_all(engine)

    return engine


def init_db(engine: Engine, borders_info: list[BorderInfo], vehicle_types: list[str]) -> None:
    session = Session(engine)

    for border_info in borders_info:
        if not session.scalar(select(Border).where(Border.uuid == border_info.uuid)):
            session.add(Border(uuid=border_info.uuid, name=border_info.name))
    for vehicle_type in vehicle_types:
        if not session.scalar(select(VehicleType).where(VehicleType.name == vehicle_type)):
            session.add(VehicleType(name=vehicle_type))

    session.commit()
    return
