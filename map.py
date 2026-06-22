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

    return f"""
    <b>{customer}</b><br>
    Town: {town}<br>
    Pending: {pending}<br>
    Priority: {priority}
    """


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

    tooltip = stop.get(
        "Customer name",
        "Customer"
    )

    if sequence is not None:

        tooltip = (
            f"{sequence}. "
            f"{tooltip}"
        )

    popup = create_popup(
        stop
    )

    folium.Marker(
        location=[lat, lon],
        popup=popup,
        tooltip=tooltip,
        icon=folium.Icon(
            color=color
        )
    ).add_to(m)


def add_route_line(
    m,
    coordinates,
    color="blue"
):

    if len(coordinates) < 2:
        return

    folium.PolyLine(
        coordinates,
        weight=4,
        opacity=0.8,
        color=color
    ).add_to(m)


def create_day_map(
    day
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
        zoom_start=10
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
        coordinates,
        "blue"
    )

    return m


def create_full_plan_map(
    days
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
        "cadetblue",
        "darkgreen",
        "darkpurple"
    ]

    for day_no, day in enumerate(
        days,
        start=1
    ):

        coordinates = []

        route_color = colors[
            day_no % len(colors)
        ]

        for idx, stop in enumerate(
            day,
            start=1
        ):

            lat = float(
                stop["Latitude"]
            )

            lon = float(
                stop["Longitude"]
            )

            coordinates.append(
                [lat, lon]
            )

            popup = f"""
            <b>Day {day_no}</b><br>
            Stop {idx}<br>
            {stop.get('Customer name')}<br>
            {stop.get('Town')}<br>
            {stop.get('Pending Visit')}
            """

            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                popup=popup,
                color=route_color,
                fill=True
            ).add_to(m)

        add_route_line(
            m,
            coordinates,
            route_color
        )

    return m
