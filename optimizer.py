import pandas as pd

from priority import (
    prepare_customers,
    get_pending_customers
)

from route_engine import (
    build_master_route,
    split_route_by_distance,
    route_summary
)


def build_area_plan(
    df,
    area,
    ors_api_key,
    daily_limit=160
):

    area_df = df[
        df["Town"]
        .astype(str)
        .str.upper()
        ==
        str(area).upper()
    ].copy()

    if len(area_df) == 0:
        return []

    route = build_master_route(
        area_df,
        ors_api_key
    )

    return split_route_by_distance(
        route,
        daily_limit
    )


def build_nationwide_plan(
    df,
    ors_api_key,
    daily_limit=160
):

    towns = sorted(
        df["Town"]
        .dropna()
        .unique()
    )

    days = []

    for town in towns:

        town_df = df[
            df["Town"] == town
        ].copy()

        if len(town_df) == 0:
            continue

        route = build_master_route(
            town_df,
            ors_api_key
        )

        town_days = split_route_by_distance(
            route,
            daily_limit
        )

        days.extend(
            town_days
        )

    return days


def inject_visit1_priority(
    days
):

    result = []

    for day in days:

        visit1 = []
        visit2 = []
        visit3 = []

        for stop in day:

            visit_no = stop.get(
                "Pending Visit No",
                999
            )

            if visit_no == 1:

                visit1.append(
                    stop
                )

            elif visit_no == 2:

                visit2.append(
                    stop
                )

            else:

                visit3.append(
                    stop
                )

        ordered = (
            visit1
            +
            visit2
            +
            visit3
        )

        result.append(
            ordered
        )

    return result


def create_plan(
    df,
    ors_api_key,
    mode="nationwide",
    area=None,
    daily_limit=160
):

    df = prepare_customers(
        df
    )

    df = get_pending_customers(
        df
    )

    if len(df) == 0:

        return []

    if mode == "area":

        days = build_area_plan(
            df,
            area,
            ors_api_key,
            daily_limit
        )

    else:

        days = build_nationwide_plan(
            df,
            ors_api_key,
            daily_limit
        )

    days = inject_visit1_priority(
        days
    )

    return days


def get_plan_summary(
    days
):

    return route_summary(
        days
    )


def get_day_stops(
    days,
    day_no
):

    if day_no < 1:
        return []

    if day_no > len(days):
        return []

    return days[
        day_no - 1
    ]
