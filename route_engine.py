import mathimport pandas as pdfrom sklearn.cluster import KMeans

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

def distance_between(a, b):

return haversine(
    a["Latitude"],
    a["Longitude"],
    b["Latitude"],
    b["Longitude"]
)

def create_zones(df, n_zones=6):

df = df.copy()

coords = df[
    ["Latitude", "Longitude"]
]

kmeans = KMeans(
    n_clusters=n_zones,
    random_state=42,
    n_init=10
)

df["Zone"] = kmeans.fit_predict(coords)

return df

def zone_center(zone_df):

return (
    zone_df["Latitude"].mean(),
    zone_df["Longitude"].mean()
)

def order_zones(df,office_lat,office_lon):

zones = []

for zone in sorted(df["Zone"].unique()):

    zone_df = df[
        df["Zone"] == zone
    ]

    lat, lon = zone_center(
        zone_df
    )

    distance = haversine(
        office_lat,
        office_lon,
        lat,
        lon
    )

    zones.append(
        (zone, distance)
    )

zones.sort(
    key=lambda x: x[1]
)

return [
    z[0]
    for z in zones
]

def build_master_route(df,start_lat,start_lon):

remaining = df.to_dict(
    "records"
)

route = []

current_lat = start_lat
current_lon = start_lon

while remaining:

    nearest = min(
        remaining,
        key=lambda x:
        haversine(
            current_lat,
            current_lon,
            x["Latitude"],
            x["Longitude"]
        )
    )

    route.append(
        nearest
    )

    current_lat = nearest[
        "Latitude"
    ]

    current_lon = nearest[
        "Longitude"
    ]

    remaining.remove(
        nearest
    )

return route

def split_route_by_distance(route,daily_limit=160,max_stops=10):

days = []

current_day = []

current_km = 0

previous = None

for stop in route:

    if previous is None:

        leg = 0

    else:

        leg = distance_between(
            previous,
            stop
        )

    if (
        current_day
        and
        (
            current_km + leg > daily_limit
            or
            len(current_day) >= max_stops
        )
    ):

        days.append(
            current_day
        )

        current_day = []

        current_km = 0

    current_day.append(
        stop
    )

    current_km += leg

    previous = stop

if current_day:

    days.append(
        current_day
    )

return days

def route_summary(days):

rows = []

for idx, day in enumerate(
    days,
    start=1
):

    rows.append(
        {
            "Day": idx,
            "Stops": len(day)
        }
    )

return pd.DataFrame(rows)
