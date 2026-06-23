from priority import (
    get_pending_customers,
    prepare_customers,
)
from route_engine import (
    build_master_route,
    create_zones,
    order_zones,
    route_summary,
    split_route_by_distance,
)


OFFICE_LAT = 6.827305661191226
OFFICE_LON = 79.95698907652856


def build_nationwide_plan(df, daily_limit=160):
    df = create_zones(
        df,
        n_zones=6,
    )

    if df.empty:
        return []

    zone_order = order_zones(
        df,
        OFFICE_LAT,
        OFFICE_LON,
    )

    all_days = []

    current_lat = OFFICE_LAT
    current_lon = OFFICE_LON

    for zone in zone_order:
        zone_df = df[
            df["Zone"] == zone
        ].copy()

        route = build_master_route(
            zone_df,
            current_lat,
            current_lon,
        )

        zone_days = split_route_by_distance(
            route,
            daily_limit,
            max_stops=10,
        )

        all_days.extend(
            zone_days
        )

        if route:
            current_lat = route[-1][
                "Latitude"
            ]
            current_lon = route[-1][
                "Longitude"
            ]

    return all_days


def build_area_plan(df, area, daily_limit=160):
    area_df = df[
        df["Town"]
        .astype(str)
        .str.upper()
        ==
        str(area).upper()
    ].copy()

    route = build_master_route(
        area_df,
        OFFICE_LAT,
        OFFICE_LON,
    )

    return split_route_by_distance(
        route,
        daily_limit,
        max_stops=10,
    )


def create_plan(
    df,
    ors_api_key=None,
    mode="nationwide",
    area=None,
    daily_limit=160,
):
    _ = ors_api_key

    df = prepare_customers(
        df
    )

    df = get_pending_customers(
        df
    )

    if mode == "area":
        return build_area_plan(
            df,
            area,
            daily_limit,
        )

    return build_nationwide_plan(
        df,
        daily_limit,
    )


def get_plan_summary(days):
    return route_summary(
        days
    )
