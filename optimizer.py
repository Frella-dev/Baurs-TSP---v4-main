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


def build_area_plan(
    df,
    area,
    daily_limit
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
        OFFICE_LAT,
        OFFICE_LON
    )

    return split_route_by_distance(
        route,
        daily_limit
    )


def build_nationwide_plan(
    df,
    daily_limit
):
    """
    One continuous Sri Lanka route.
    """

    route = build_master_route(
        df,
        OFFICE_LAT,
        OFFICE_LON
    )

    return split_route_by_distance(
        route,
        daily_limit
    )


def create_plan(
    df,
    ors_api_key=None,
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
            daily_limit
        )

    else:

        days = build_nationwide_plan(
            df,
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
