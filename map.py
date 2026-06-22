import folium

from priority import (
    marker_color
)


def create_popup(stop):

    customer = stop.get(
        "Customer name",
        "Unknown"
    )

    town = stop.get(
        "Town",
        "-"
    )

    pending = stop.get(
        "Pending Visit",
        "-"
    )

    priority = stop.get(
        "Priority",
        "-"
    )

    html = f"""
    <b>{customer}</b><br>
    Town: {town}<br>
    Pending: {pending}<br>
    Priority: {priority}
    """

    return html


def add_customer_marker(
    m,
    stop,
    sequence=None
):

    lat = float(
        stop["Latitude"]
    )

    lon = float(
        stop["Longitude"]
    )

    color = stop.get(
        "Marker Color",
        marker_color(stop)
    )

    popup = create_popup(
        stop
    )

    tooltip = stop.get(
        "Customer name",
        "Customer"
    )

    if sequence:

        tooltip = (
            f"{sequence}. "
            f"{tooltip}"
        )

    folium.Marker(
        [lat, lon],
        popup=popup,
        tooltip=tooltip,
        icon=folium.Icon(
            color=color
        )
    ).add_to(m)


def add_route_line(
    m,
    coordinates
):

    if len(coordinates) < 2:
        return

    folium.PolyLine(
        coordinates,
        weight=5,
        opacity=0.8
    ).add_to(m)


def create_day_map(
    day,
    office_lat=None,
    office_lon=None
):

    if len(day) == 0:

        return folium.Map(
            location=[
                7.5,
                80.7
            ],
            zoom_start=8
        )

    first = day[0]

    m = folium.Map(
        location=[
            float(
                first["Latitude"]
            ),
            float(
                first["Longitude"]
            )
        ],
        zoom_start=9
    )

    coordinates = []

    for idx, stop in enumerate(
        day,
        start=1
    ):

        add_customer_marker(
            m,
            stop,
            idx
        )

        coordinates.append(
            [
                float(
                    stop["Latitude"]
                ),
                float(
                    stop["Longitude"]
                )
            ]
        )

    add_route_line(
        m,
        coordinates
    )

    return m


def create_area_map(
    customers
):

    if len(customers) == 0:

        return folium.Map(
            location=[
                7.5,
                80.7
            ],
            zoom_start=7
        )

    first = customers[0]

    m = folium.Map(
        location=[
            first["Latitude"],
            first["Longitude"]
        ],
        zoom_start=10
    )

    for stop in customers:

        add_customer_marker(
            m,
            stop
        )

    return m


def create_full_plan_map(
    days,
    office_lat=None,
    office_lon=None
):

    m = folium.Map(
        location=[
            7.5,
            80.7
        ],
        zoom_start=7
    )

    colors = [
        "red",
        "blue",
        "green",
        "purple",
        "orange",
        "darkred",
        "cadetblue"
    ]

    for day_no, day in enumerate(
        days,
        start=1
    ):

        coords = []

        for stop in day:

            lat = float(
                stop["Latitude"]
            )

            lon = float(
                stop["Longitude"]
            )

            coords.append(
                [lat, lon]
            )

            popup = f"""
            Day {day_no}<br>
            {stop['Customer name']}<br>
            Pending:
            {stop.get('Pending Visit')}
            """

            folium.CircleMarker(
                [lat, lon],
                radius=6,
                popup=popup,
                color=colors[
                    day_no % len(colors)
                ]
            ).add_to(m)

        if len(coords) > 1:

            folium.PolyLine(
                coords,
                weight=3,
                color=colors[
                    day_no % len(colors)
                ]
            ).add_to(m)

    return m
