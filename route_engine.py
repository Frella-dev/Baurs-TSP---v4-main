import pandas as pd
import requests


ORS_MATRIX_URL = (
    "https://api.openrouteservice.org/v2/matrix/driving-car"
)


def build_distance_matrix(
    locations,
    api_key
):

    coordinates = []

    for row in locations:

        coordinates.append(
            [
                float(row["Longitude"]),
                float(row["Latitude"])
            ]
        )

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "locations": coordinates,
        "metrics": ["distance"]
    }

    response = requests.post(
        ORS_MATRIX_URL,
        json=payload,
        headers=headers,
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["distances"]


def nearest_neighbor_route(
    locations,
    distance_matrix
):

    if len(locations) <= 1:

        return locations

    remaining = list(
        range(len(locations))
    )

    route_indexes = []

    current = 0

    route_indexes.append(
        current
    )

    remaining.remove(
        current
    )

    while remaining:

        next_stop = min(
            remaining,
            key=lambda x:
            distance_matrix[current][x]
        )

        route_indexes.append(
            next_stop
        )

        remaining.remove(
            next_stop
        )

        current = next_stop

    result = []

    for idx in route_indexes:

        result.append(
            locations[idx]
        )

    return result


def build_master_route(
    df,
    api_key
):

    locations = df.to_dict(
        "records"
    )

    if len(locations) <= 1:

        return locations

    matrix = build_distance_matrix(
        locations,
        api_key
    )

    return nearest_neighbor_route(
        locations,
        matrix
    )


def route_distance(
    route
):

    total = 0

    for i in range(
        len(route) - 1
    ):

        lat1 = route[i][
            "Latitude"
        ]

        lon1 = route[i][
            "Longitude"
        ]

        lat2 = route[i + 1][
            "Latitude"
        ]

        lon2 = route[i + 1][
            "Longitude"
        ]

        total += (
            ((lat2 - lat1) ** 2)
            +
            ((lon2 - lon1) ** 2)
        ) ** 0.5

    return round(
        total,
        2
    )


def split_route_by_distance(
    route,
    daily_limit=160,
    max_stops=10
):

    days = []

    current_day = []

    for stop in route:

        current_day.append(
            stop
        )

        if (
            len(current_day)
            >= max_stops
        ):

            days.append(
                current_day
            )

            current_day = []

    if current_day:

        days.append(
            current_day
        )

    return days


def route_summary(
    days
):

    rows = []

    for day_no, day in enumerate(
        days,
        start=1
    ):

        rows.append(
            {
                "Day":
                day_no,

                "Stops":
                len(day),

                "Distance":
                route_distance(
                    day
                )
            }
        )

    return pd.DataFrame(
        rows
    )
