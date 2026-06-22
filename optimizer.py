import pandas as pd

from sklearn.cluster import KMeans

from priority import (
    prepare_customers,
    get_pending_customers
)

from route_engine import (
    build_master_route,
    split_route_by_distance,
    route_summary
)


OFFICE_LAT = 6.8275814230546725
OFFICE_LON = 79.95698659415302


def build_nationwide_plan(
    df,
    daily_limit=160
):

    df = prepare_customers(df)

    df = get_pending_customers(df)

    if len(df) == 0:
        return []

    coords = df[
        [
            "Latitude",
            "Longitude"
        ]
    ].values

    cluster_count = max(
        1,
        len(df) // 12
    )

    kmeans = KMeans(
        n_clusters=cluster_count,
        random_state=42,
        n_init=10
    )

    df["Cluster"] = kmeans.fit_predict(
        coords
    )

    df = df.sort_values(
        by=[
            "Cluster",
            "Priority"
        ],
        ascending=[
            True,
            False
        ]
    )

    days = []

    for cluster in sorted(
        df["Cluster"].unique()
    ):

        cluster_df = df[
            df["Cluster"] == cluster
        ].copy()

        route = build_master_route(
            cluster_df,
            OFFICE_LAT,
            OFFICE_LON
        )

        cluster_days = split_route_by_distance(
            route,
            daily_limit
        )

        days.extend(
            cluster_days
        )

    return days


def build_area_plan(
    df,
    area,
    daily_limit=160
):

    df = prepare_customers(df)

    df = get_pending_customers(df)

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


def inject_missed_visit1(
    route_day,
    all_customers,
    radius_km=15
):

    from route_engine import haversine

    missed = all_customers[
        all_customers[
            "Pending Visit No"
        ] == 1
    ]

    additions = []

    for stop in route_day:

        for _, customer in missed.iterrows():

            distance = haversine(
                stop["Latitude"],
                stop["Longitude"],
                customer["Latitude"],
                customer["Longitude"]
            )

            if distance <= radius_km:

                additions.append(
                    customer.to_dict()
                )

    unique = {}

    for item in additions:

        unique[
            item["Customer name"]
        ] = item

    final = route_day.copy()

    for item in unique.values():

        exists = False

        for stop in final:

            if (
                stop["Customer name"]
                ==
                item["Customer name"]
            ):
                exists = True
                break

        if not exists:
            final.append(item)

    return final


def apply_missed_visit_logic(
    days,
    df,
    radius_km=15
):

    enhanced = []

    for day in days:

        enhanced.append(
            inject_missed_visit1(
                day,
                df,
                radius_km
            )
        )

    return enhanced


def create_plan(
    df,
    mode="nationwide",
    area=None,
    daily_limit=160
):

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

    df = prepare_customers(df)

    days = apply_missed_visit_logic(
        days,
        df
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