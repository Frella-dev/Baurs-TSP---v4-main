from urllib.parse import quote

GOOGLE_MAPS_BASE = (
    "https://www.google.com/maps/dir/?api=1"
)

MAX_STOPS_PER_ROUTE = 25


def coordinate_string(lat, lon):

    return f"{lat},{lon}"


def build_route_url(chunk):

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
        f"{GOOGLE_MAPS_BASE}"
        f"&origin={origin}"
        f"&destination={destination}"
        f"&travelmode=driving"
        f"&waypoints={quote(waypoint_string)}"
    )


def build_day_route_urls(day):

    urls = []

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
                "part":
                len(urls) + 1,

                "start":
                i + 1,

                "end":
                min(
                    i + MAX_STOPS_PER_ROUTE,
                    len(day)
                ),

                "url":
                build_route_url(
                    chunk
                )
            }
        )

    return urls