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
    area
):

    area_df = df[
        df["Town"]
        .astype(str)
        .str.upper()
        ==
        str(area).upper()
    ].copy()

    return build_optimized_plan(
        area_df
    )


def build_nationwide_plan(df):

    return build_optimized_plan(
        df
    )


def create_plan(
    df,
    ors_api_key=None,
    mode="nationwide",
    area=None,
    daily_limit=160
):

    _ = ors_api_key
    _ = daily_limit

    df = prepare_customers(df)

    df = get_pending_customers(df)

    if mode == "area":

        return build_area_plan(
            df,
            area
        )

    return build_nationwide_plan(
        df
    )


def get_plan_summary(days):

    return route_summary(
        days
    )
