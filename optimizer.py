from priority import (
    prepare_customers,
    get_pending_customers,
)

from route_engine import (
    build_optimized_plan,
    route_summary,
)

OFFICE_LAT = 6.827305661191226
OFFICE_LON = 79.95698907652856


def build_area_plan(
    df,
    area,
    max_stops=12
):

    area_df = df[
        df["Town"]
        .astype(str)
        .str.upper()
        ==
        str(area).upper()
    ].copy()

    return build_optimized_plan(
        area_df,
        max_stops=max_stops
    )


def build_nationwide_plan(
    df,
    max_stops=12
):

    return build_optimized_plan(
        df,
        max_stops=max_stops
    )


def create_plan(
    df,
    ors_api_key=None,
    mode="nationwide",
    area=None,
    max_stops=12
):

    _ = ors_api_key

    df = prepare_customers(
        df
    )

    df = get_pending_customers(
        df
    )

    if df.empty:
        return []

    if mode == "area":

        return build_area_plan(
            df,
            area,
            max_stops=max_stops
        )

    return build_nationwide_plan(
        df,
        max_stops=max_stops
    )


def get_plan_summary(
    days
):

    return route_summary(
        days
    )
