from datetime import datetime

import requests
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from db import Border, VehicleType, LicensePlate, Crossing
from utils import BorderInfo, get_queue, CrossingInfo


def gather(engine: Engine, borders_info: list[BorderInfo], vehicle_types: list[str]):
    session: Session = Session(engine)

    arrived_counter: int = 0
    left_counter: int = 0

    print(f"{datetime.now().strftime('%H:%M:%S')} > Retrieving data...")

    cache: set[str] = set()
    for border_info in borders_info:
        try:
            queue: list[CrossingInfo] = get_queue(border_info.uuid, vehicle_types)
        except requests.RequestException:
            continue

        for entry in queue:
            cache.add(f"{entry.license_plate}{entry.arrived_at.isoformat()}")

            license_plate = session.scalar(select(LicensePlate).where(
                LicensePlate.value == entry.license_plate
            ))
            if not license_plate:
                license_plate = LicensePlate(value=entry.license_plate)
                session.add(license_plate)

            if not session.scalar(select(Crossing).where(
                    (Crossing.license_plate == license_plate) &
                    (Crossing.arrived_at == entry.arrived_at)
            )):
                session.add(Crossing(
                    border=session.scalar(select(Border).where(
                        Border.uuid == border_info.uuid
                    )),
                    license_plate=license_plate,
                    vehicle_type=session.scalar(select(VehicleType).where(
                        VehicleType.name == entry.vehicle_type
                    )),
                    priority=entry.priority,
                    arrived_at=entry.arrived_at
                ))
                arrived_counter += 1

    for crossing in session.scalars(select(Crossing).where(Crossing.left_at == None)):
        if f"{crossing.license_plate.value}{crossing.arrived_at.isoformat()}" not in cache:
            crossing.left_at = datetime.now().replace(microsecond=0)
            left_counter += 1

    print(f"{datetime.now().strftime('%H:%M:%S')} > Success (+{arrived_counter} -{left_counter})")

    session.commit()
