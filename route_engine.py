import math
import pandas as pd
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

OFFICE_LAT = 6.827512186996366
OFFICE_LON = 79.95694904907492

VISIT_MINUTES = 15
WORKING_DAY_MINUTES = 480
AVERAGE_SPEED_KMH = 40


def haversine(lat1, lon1, lat2, lon2):

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


def build_distance_matrix(df):

    coords = list(
        zip(
            df["Latitude"],
            df["Longitude"]
        )
    )

    matrix = []

    for lat1, lon1 in coords:

        row = []

        for lat2, lon2 in coords:

            row.append(
                int(
                    haversine(
                        lat1,
                        lon1,
                        lat2,
                        lon2
                    ) * 1000
                )
            )

        matrix.append(row)

    return matrix


def solve_tsp(df):

    if len(df) <= 1:
        return df.to_dict("records")

    office_row = {
        "Customer name": "OFFICE",
        "Town": "OFFICE",
        "Latitude": OFFICE_LAT,
        "Longitude": OFFICE_LON
    }

    office_df = pd.DataFrame(
        [office_row]
    )

    working_df = pd.concat(
        [office_df, df],
        ignore_index=True
    )

    distance_matrix = build_distance_matrix(
        working_df
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
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )

    search_parameters.time_limit.seconds = 20

    solution = routing.SolveWithParameters(
        search_parameters
    )

    if solution is None:
        return df.to_dict("records")

    ordered_route = []

    index = routing.Start(0)

    while not routing.IsEnd(index):

        node = manager.IndexToNode(
            index
        )

        row = working_df.iloc[node]

        if row["Customer name"] != "OFFICE":

            ordered_route.append(
                row.to_dict()
            )

        index = solution.Value(
            routing.NextVar(index)
        )

    return ordered_route


def route_distance(route):

    if len(route) == 0:
        return 0

    total = 0

    total += haversine(
        OFFICE_LAT,
        OFFICE_LON,
        route[0]["Latitude"],
        route[0]["Longitude"]
    )

    for i in range(
        len(route) - 1
    ):

        total += haversine(
            route[i]["Latitude"],
            route[i]["Longitude"],
            route[i + 1]["Latitude"],
            route[i + 1]["Longitude"]
        )

    total += haversine(
        route[-1]["Latitude"],
        route[-1]["Longitude"],
        OFFICE_LAT,
        OFFICE_LON
    )

    return total


def split_route_by_time(
    route,
    max_stops=12
):

    days = []

    current_day = []

    current_minutes = 0

    previous_lat = OFFICE_LAT
    previous_lon = OFFICE_LON

    for stop in route:

        km = haversine(
            previous_lat,
            previous_lon,
            stop["Latitude"],
            stop["Longitude"]
        )

        travel_minutes = (
            km /
            AVERAGE_SPEED_KMH
        ) * 60

        stop_minutes = VISIT_MINUTES

        total_needed = (
            travel_minutes
            +
            stop_minutes
        )

        if (
            current_day
            and
            (
                current_minutes
                +
                total_needed
                >
                WORKING_DAY_MINUTES
                or
                len(current_day)
                >= max_stops
            )
        ):

            days.append(
                current_day
            )

            current_day = []

            current_minutes = 0

            previous_lat = OFFICE_LAT
            previous_lon = OFFICE_LON

            km = haversine(
                previous_lat,
                previous_lon,
                stop["Latitude"],
                stop["Longitude"]
            )

            travel_minutes = (
                km /
                AVERAGE_SPEED_KMH
            ) * 60

            total_needed = (
                travel_minutes
                +
                VISIT_MINUTES
            )

        current_day.append(
            stop
        )

        current_minutes += total_needed

        previous_lat = stop["Latitude"]
        previous_lon = stop["Longitude"]

    if current_day:

        days.append(
            current_day
        )

    return days


def build_optimized_plan(
    df,
    max_stops=12
):

    if len(df) == 0:
        return []

    ordered_route = solve_tsp(
        df
    )

    return split_route_by_time(
        ordered_route,
        max_stops=max_stops
    )


def route_summary(days):

    rows = []

    for day_no, day in enumerate(
        days,
        start=1
    ):

        rows.append(
            {
                "Day": day_no,
                "Stops": len(day),
                "KM": round(
                    route_distance(day),
                    1
                )
            }
        )

    return pd.DataFrame(
        rows
    )
