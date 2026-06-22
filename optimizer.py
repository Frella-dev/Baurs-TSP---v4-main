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

OFFICE_LAT = 6.8275814230546725
OFFICE_LON = 79.95698659415302


def cluster_center(cluster_df):

    return (
        cluster_df["Latitude"].mean(),
        cluster_df["Longitude"].mean()
    )


def order_clusters(
    df,
    cluster_column="Cluster"
):

    clusters = []

    current_lat = OFFICE_LAT
    current_lon = OFFICE_LON

    remaining = list(
        df[cluster_column].unique()
    )

    while remaining:

        nearest_cluster = None
        nearest_distance = 999999

        for cluster in remaining:

            cluster_df = df[
                df[cluster_column] == cluster
            ]

            lat, lon = cluster_center(
                cluster_df
            )

            distance = haversine(
                current_lat,
                current_lon,
                lat,
                lon
            )

            if distance < nearest_distance:

                nearest_distance = distance
                nearest_cluster = cluster

        clusters.append(
            nearest_cluster
        )

        cluster_df = df[
            df[cluster_column]
            == nearest_cluster
        ]

        current_lat, current_lon = (
            cluster_center(cluster_df)
        )

        remaining.remove(
            nearest_cluster
        )

    return clusters


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
        min(
            len(df) // 15,
            12
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

    cluster_sequence = order_clusters(
        df
    )

    days = []

    start_lat = OFFICE_LAT
    start_lon = OFFICE_LON

    for cluster in cluster_sequence:

        cluster_df = df[
            df["Cluster"] == cluster
        ].copy()

        cluster_df = cluster_df.sort_values(
            "Priority",
            ascending=False
        )

        route = build_master_route(
            cluster_df,
            start_lat,
            start_lon
        )

        cluster_days = split_route_by_distance(
            route,
            daily_limit
        )

        days.extend(
            cluster_days
        )

        if len(route) > 0:

            start_lat = route[-1][
                "Latitude"
            ]

            start_lon = route[-1][
                "Longitude"
            ]

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

            final.append(
                item
            )

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
