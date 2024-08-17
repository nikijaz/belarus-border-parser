import time

import requests
from sqlalchemy import Engine

from src.db import init_db_connection, init_db
from src.gather import gather
from src.utils import get_borders_info, BorderInfo


def main():
    engine: Engine = init_db_connection()

    try:
        borders_info: list[BorderInfo] = get_borders_info()
    except requests.RequestException:
        return
    vehicle_types: list[str] = ["bus", "car", "motorcycle", "truck"]

    init_db(engine, borders_info, vehicle_types)

    while True:
        gather(engine, borders_info, vehicle_types)
        time.sleep(60)


if __name__ == "__main__":
    main()
