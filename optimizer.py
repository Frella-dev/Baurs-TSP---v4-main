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


OFFICE_LAT = 6.827305661191226
OFFICE_LON = 79.95698907652856


def create_plan(
    df,
    mode="nationwide",
    area=None,
    daily_limit=160
):

    df = prepare_customers(df)

    df = get_pending_customers(df)

    if len(df) == 0:
        return []

    if mode == "area":

        if area:

            df = df[
                df["Town"]
                .astype(str)
                .str.upper()
                ==
                str(area).upper()
            ].copy()

    route = build_master_route(
        df,
        OFFICE_LAT,
        OFFICE_LON
    )

    days = split_route_by_distance(
        route,
        daily_limit
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
