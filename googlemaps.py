from urllib.parse import quote


MAX_STOPS_PER_ROUTE = 10


def coordinate_string(
    lat,
    lon
):

    return f"{lat},{lon}"


def build_route_url(
    chunk
):

    if len(chunk) == 0:
        return None

    if len(chunk) == 1:

        return (
            "https://www.google.com/maps/search/?api=1"
            f"&query={chunk[0]['Latitude']},{chunk[0]['Longitude']}"
        )

    origin = coordinate_string(
        chunk[0]["Latitude"],
        chunk[0]["Longitude"]
    )

    destination = coordinate_string(
        chunk[-1]["Latitude"],
        chunk[-1]["Longitude"]
    )

    waypoints = []

    for stop in chunk[1:-1]:

        waypoints.append(
            coordinate_string(
                stop["Latitude"],
                stop["Longitude"]
            )
        )

    waypoint_string = "|".join(
        waypoints
    )

    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={origin}"
        f"&destination={destination}"
        f"&travelmode=driving"
        f"&waypoints={quote(waypoint_string)}"
    )


def build_day_route_urls(
    day
):

    urls = []

    part_no = 1

    for i in range(
        0,
        len(day),
        MAX_STOPS_PER_ROUTE
    ):

        chunk = day[
            i:i + MAX_STOPS_PER_ROUTE
        ]

        urls.append(
            {
                "part": part_no,
                "start": i + 1,
                "end": min(
                    i + MAX_STOPS_PER_ROUTE,
                    len(day)
                ),
                "url": build_route_url(
                    chunk
                )
            }
        )

        part_no += 1

    return urls
