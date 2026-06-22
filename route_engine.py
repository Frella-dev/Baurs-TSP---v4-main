import math
import pandas as pd

def haversine(
lat1,
lon1,
lat2,
lon2
):

```
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
```

def distance_between(
point_a,
point_b
):

```
return haversine(
    point_a["Latitude"],
    point_a["Longitude"],
    point_b["Latitude"],
    point_b["Longitude"]
)
```

def build_master_route(
df,
start_lat,
start_lon
):
"""
Territory aware route
Priority aware route
"""

```
remaining = df.to_dict(
    "records"
)

if len(remaining) == 0:
    return []

route = []

current_lat = start_lat
current_lon = start_lon

while len(remaining) > 0:

    candidates = []

    for stop in remaining:

        distance = haversine(
            current_lat,
            current_lon,
            stop["Latitude"],
            stop["Longitude"]
        )

        priority = stop.get(
            "Priority",
            0
        )

        score = (
            distance
            -
            (
                priority * 0.20
            )
        )

        candidates.append(
            (
                score,
                stop
            )
        )

    candidates.sort(
        key=lambda x: x[0]
    )

    selected = candidates[
        0
    ][1]

    route.append(
        selected
    )

    current_lat = selected[
        "Latitude"
    ]

    current_lon = selected[
        "Longitude"
    ]

    remaining.remove(
        selected
    )

return route
```

def route_distance(
route
):

```
if len(route) <= 1:
    return 0

total = 0

for i in range(
    len(route) - 1
):

    total += distance_between(
        route[i],
        route[i + 1]
    )

return round(
    total,
    2
)
```

def merge_small_days(
days
):

```
if len(days) <= 1:
    return days

result = []

for day in days:

    if (
        len(day) < 5
        and
        len(result) > 0
    ):

        result[-1].extend(
            day
        )

    else:

        result.append(
            day
        )

return result
```

def split_route_by_distance(
route,
daily_limit=160
):

```
days = []

current_day = []

current_distance = 0

previous = None

MIN_STOPS_PER_DAY = 8
MAX_STOPS_PER_DAY = 20

for stop in route:

    if previous is None:

        distance = 0

    else:

        distance = distance_between(
            previous,
            stop
        )

    create_new_day = False

    if (
        current_distance + distance
        > daily_limit
        and
        len(current_day)
        >= MIN_STOPS_PER_DAY
    ):
        create_new_day = True

    if (
        len(current_day)
        >= MAX_STOPS_PER_DAY
    ):
        create_new_day = True

    if create_new_day:

        days.append(
            current_day
        )

        current_day = []

        current_distance = 0

    current_day.append(
        stop
    )

    current_distance += distance

    previous = stop

if len(current_day) > 0:

    days.append(
        current_day
    )

return merge_small_days(
    days
)
```

def day_distance(
day
):

```
return route_distance(
    day
)
```

def create_day_summary(
day
):

```
visit1 = 0
visit2 = 0
visit3 = 0

for row in day:

    pending = row.get(
        "Pending Visit No",
        999
    )

    if pending == 1:
        visit1 += 1

    elif pending == 2:
        visit2 += 1

    elif pending == 3:
        visit3 += 1

return {
    "stops": len(day),
    "distance": round(
        day_distance(day),
        2
    ),
    "visit1": visit1,
    "visit2": visit2,
    "visit3": visit3
}
```

def route_summary(
days
):

```
result = []

for idx, day in enumerate(
    days,
    start=1
):

    summary = create_day_summary(
        day
    )

    summary["day"] = idx

    result.append(
        summary
    )

return pd.DataFrame(
    result
)
```

def build_area_route(
df,
area_column="Town"
):

```
routes = {}

areas = sorted(
    df[
        area_column
    ]
    .dropna()
    .unique()
)

for area in areas:

    area_df = df[
        df[
            area_column
        ]
        == area
    ]

    routes[
        area
    ] = area_df.to_dict(
        "records"
    )

return routes
```

def get_last_stop(
day
):

```
if len(day) == 0:
    return None

return day[-1]
```

def get_start_point(
day
):

```
if len(day) == 0:
    return None

return day[0]
```
