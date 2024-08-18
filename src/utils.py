from datetime import datetime, timedelta

import requests


class BorderInfo:
    def __init__(self, uuid: str, name: str):
        self.uuid = uuid
        self.name = name


class CrossingInfo:
    def __init__(self, license_plate: str, vehicle_type: str, priority: bool, arrived_at: datetime):
        self.license_plate = license_plate
        self.vehicle_type = vehicle_type
        self.priority = priority
        self.arrived_at = arrived_at


def get_borders_info() -> list[BorderInfo]:
    try:
        response: requests.Response = requests.get(
            url="https://belarusborder.by/info/checkpoint?token=bts47d5f-6420-4f74-8f78-42e8e4370cc4"
        )
    except requests.RequestException as err:
        print(f"{datetime.now().strftime('%H:%M:%S')} > Error at get_borders_info()")
        raise err

    borders: list[dict] = response.json()["result"]
    return [
        BorderInfo(
            uuid=border.get("id"),
            name=border.get("name")
        ) for border in borders
    ]


def get_border_data(border_uuid: str) -> dict:
    try:
        response: requests.Response = requests.get(
            url=f"https://belarusborder.by/info/monitoring-new?token=test&checkpointId={border_uuid}"
        )
    except requests.RequestException as err:
        print(f"{datetime.now().strftime('%H:%M:%S')} > Error at get_border_data({border_uuid})")
        raise err

    border_data: dict = response.json()
    return border_data


def get_queue(border_uuid: str, vehicle_types: list[str]) -> list[CrossingInfo]:
    result: list[CrossingInfo] = []

    border_data = get_border_data(border_uuid)
    for vehicle_type in vehicle_types:
        for priority in [True, False]:
            queue: list[dict] = border_data.get(f"{vehicle_type}Priority" if priority else f"{vehicle_type}LiveQueue")
            result.extend([CrossingInfo(
                license_plate=entry.get("regnum"),
                vehicle_type=vehicle_type,
                priority=priority,
                arrived_at=datetime.strptime(entry.get("registration_date"), "%H:%M:%S %d.%m.%Y") - timedelta(hours=3)
            ) for entry in queue])

    return result
