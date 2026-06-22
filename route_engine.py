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
    a,
    b
):

    return haversine(
        a["Latitude"],
        a["Longitude"],
        b["Latitude"],
        b["Longitude"]
    )


def build_master_route(
    df,
    office_lat,
    office_lon
):
    """
    Build one continuous nationwide route.
    Start from office.
    Never jump randomly.
    """

    remaining = df.to_dict(
        "records"
    )

    route = []

    current_lat = office_lat
    current_lon = office_lon

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
    daily_limit=160,
    max_stops=10
):

    days = []

    current_day = []

    current_km = 0

    previous = None

    for stop in route:

        if previous is None:

            leg = 0

        else:

            leg = distance_between(
                previous,
                stop
            )

        create_new_day = False

        if (
            current_km + leg
            > daily_limit
            and
            len(current_day) > 0
        ):
            create_new_day = True

        if (
            len(current_day)
            >= max_stops
        ):
            create_new_day = True

        if create_new_day:

            days.append(
                current_day
            )

            current_day = []
            current_km = 0

        current_day.append(
            stop
        )

        current_km += leg

        previous = stop

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
                "Day": day_no,
                "Stops": len(day),
                "Distance KM":
                round(
                    route_distance(day),
                    2
                )
            }
        )

    return pd.DataFrame(
        rows
    )
