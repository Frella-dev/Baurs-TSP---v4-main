import pandas as pd
from sklearn.cluster import KMeans

from priority import (
    prepare_customers,
    get_pending_customers
)

from route_engine import (
    build_master_route,
    split_route_by_distance,
    route_summary,
    haversine
)


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
            None,
            None
        )

        return split_route_by_distance(
            route,
            daily_limit
        )

    coords = df[
        [
            "Latitude",
            "Longitude"
        ]
    ].values

    cluster_count = max(
        1,
        min(
            len(df) // 12,
            10
        )
    )

    kmeans = KMeans(
        n_clusters=cluster_count,
        random_state=42,
        n_init=10
    )

    df["Cluster"] = kmeans.fit_predict(
        coords
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
            None,
            None
        )

        cluster_days = split_route_by_distance(
            route,
            daily_limit
        )

        days.extend(
            cluster_days
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


def nearest_day(
    day_a,
    day_b
):

    if len(day_a) == 0:
        return 999999

    if len(day_b) == 0:
        return 999999

    a = day_a[-1]
    b = day_b[0]

    return haversine(
        a["Latitude"],
        a["Longitude"],
        b["Latitude"],
        b["Longitude"]
    )
