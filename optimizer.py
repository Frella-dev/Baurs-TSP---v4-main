import math
import pandas as pd

from ortools.constraint_solver import (
    routing_enums_pb2,
    pywrapcp
)


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


def create_distance_matrix(df):

    records = df.to_dict(
        "records"
    )

    matrix = []

    for row1 in records:

        row = []

        for row2 in records:

            distance = haversine(
                row1["Latitude"],
                row1["Longitude"],
                row2["Latitude"],
                row2["Longitude"]
            )

            row.append(
                int(distance * 1000)
            )

        matrix.append(row)

    return matrix


def solve_tsp(df):

    if len(df) <= 1:

        return df.to_dict(
            "records"
        )

    distance_matrix = create_distance_matrix(
        df
    )

    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        1,
        0
    )

    routing = pywrapcp.RoutingModel(
        manager
    )

    def distance_callback(
        from_index,
        to_index
    ):

        from_node = manager.IndexToNode(
            from_index
        )

        to_node = manager.IndexToNode(
            to_index
        )

        return distance_matrix[
            from_node
        ][
            to_node
        ]

    transit_callback_index = (
        routing.RegisterTransitCallback(
            distance_callback
        )
    )

    routing.SetArcCostEvaluatorOfAllVehicles(
        transit_callback_index
    )

    search_parameters = (
        pywrapcp.DefaultRoutingSearchParameters()
    )

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy
        .PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(
        search_parameters
    )

    if solution is None:

        return df.to_dict(
            "records"
        )

    records = df.to_dict(
        "records"
    )

    route = []

    index = routing.Start(
        0
    )

    while not routing.IsEnd(
        index
    ):

        node = manager.IndexToNode(
            index
        )

        route.append(
            records[node]
        )

        index = solution.Value(
            routing.NextVar(index)
        )

    return route


def build_master_route(
    df,
    start_lat=None,
    start_lon=None
):

    return solve_tsp(
        df
    )


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


def merge_small_days(
    days
):

    if len(days) <= 1:

        return days

    result = []

    for day in days:

        if (
            len(day) < 5
            and
            len(result) > 0
        ):

            result[-1].extend(
                day
            )

        else:

            result.append(
                day
            )

    return result


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

        if (
            (
                current_distance
                + distance
            )
            > daily_limit
            and
            len(current_day) > 0
        ):

            days.append(
                current_day
            )

            current_day = []

            current_distance = 0

        if (
            len(current_day)
            >= MAX_STOPS_PER_DAY
        ):

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

    return merge_small_days(
        days
    )


def day_distance(
    day
):

    return route_distance(
        day
    )


def create_day_summary(
    day
):

    visit1 = 0
    visit2 = 0
    visit3 = 0

    for row in day:

        pending = row.get(
            "Pending Visit No",
            999
        )

        if pending == 1:
            visit1 += 1

        elif pending == 2:
            visit2 += 1

        elif pending == 3:
            visit3 += 1

    return {
        "stops": len(day),
        "distance": round(
            day_distance(day),
            2
        ),
        "visit1": visit1,
        "visit2": visit2,
        "visit3": visit3
    }


def route_summary(
    days
):

    result = []

    for idx, day in enumerate(
        days,
        start=1
    ):

        summary = create_day_summary(
            day
        )

        summary["day"] = idx

        result.append(
            summary
        )

    return pd.DataFrame(
        result
    )


def get_last_stop(
    day
):

    if len(day) == 0:
        return None

    return day[-1]


def get_start_point(
    day
):

    if len(day) == 0:
        return None

    return day[0]
