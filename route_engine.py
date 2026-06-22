import math
import pandas as pd


def haversine(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


def distance_between(
    point_a,
    point_b
):

    return haversine(
        point_a["Latitude"],
        point_a["Longitude"],
        point_b["Latitude"],
        point_b["Longitude"]
    )


def build_master_route(
    df,
    start_lat,
    start_lon
):

    remaining = df.to_dict(
        "records"
    )

    route = []

    current_lat = start_lat
    current_lon = start_lon

    while remaining:

        nearest = min(
            remaining,
            key=lambda x: haversine(
                current_lat,
                current_lon,
                x["Latitude"],
                x["Longitude"]
            )
        )

        route.append(
            nearest
        )

        current_lat = nearest[
            "Latitude"
        ]

        current_lon = nearest[
            "Longitude"
        ]

        remaining.remove(
            nearest
        )

    return route


def route_distance(
    route
):

    if len(route) <= 1:
        return 0

    total = 0

    for i in range(
        len(route) - 1
    ):

        total += distance_between(
            route[i],
            route[i + 1]
        )

    return round(
        total,
        2
    )


def split_route_by_distance(
    route,
    daily_limit=160
):

    days = []

    current_day = []

    current_distance = 0

    previous = None

    MAX_STOPS_PER_DAY = 10

    for stop in route:

        if previous is None:

            distance = 0

        else:

            distance = distance_between(
                previous,
                stop
            )

        create_new_day = False

        if (
            current_distance + distance
            > daily_limit
            and
            len(current_day) > 0
        ):
            create_new_day = True

        if (
            len(current_day)
            >= MAX_STOPS_PER_DAY
        ):
            create_new_day = True

        if create_new_day:

            days.append(
                current_day
            )

            current_day = []
            current_distance = 0

        current_day.append(
            stop
        )

        current_distance += distance

        previous = stop

    if len(current_day) > 0:

        days.append(
            current_day
        )

    return days


def day_distance(
    day
):

    return route_distance(
        day
    )


def route_summary(
    days
):

    rows = []

    for i, day in enumerate(
        days,
        start=1
    ):

        rows.append(
            {
                "Day": i,
                "Stops": len(day),
                "Distance KM":
                round(
                    day_distance(day),
                    2
                )
            }
        )

    return pd.DataFrame(
        rows
    )
