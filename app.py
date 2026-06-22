import streamlit as st
import pandas as pd

from streamlit_folium import st_folium

from sheets import (
    load_sheet,
    get_towns
)

from priority import (
    prepare_customers,
    priority_summary
)

from optimizer import (
    create_plan,
    get_plan_summary
)

from map import (
    create_day_map,
    create_full_plan_map
)

from googlemaps import (
    build_day_route_urls
)


st.set_page_config(
    page_title="Pharma Route Planner V5",
    layout="wide"
)

st.title(
    "Pharma Route Planner V5"
)

if "days" not in st.session_state:
    st.session_state.days = None

if "generated" not in st.session_state:
    st.session_state.generated = False


sheet_url = st.text_input(
    "Google Sheet URL"
)

planning_mode = st.radio(
    "Planning Mode",
    [
        "Nationwide",
        "Area"
    ]
)

daily_limit = st.number_input(
    "Daily KM Limit",
    min_value=25,
    max_value=500,
    value=160
)

selected_area = None


if sheet_url:

    try:

        temp_df = load_sheet(
            sheet_url
        )

        towns = get_towns(
            temp_df
        )

        if planning_mode == "Area":

            selected_area = st.selectbox(
                "Select Area",
                towns
            )

    except Exception as e:

        st.warning(
            str(e)
        )


if st.button(
    "Generate Route Plan"
):

    try:

        df = load_sheet(
            sheet_url
        )

        df = prepare_customers(
            df
        )

        if planning_mode == "Area":

            days = create_plan(
                df,
                mode="area",
                area=selected_area,
                daily_limit=daily_limit
            )

        else:

            days = create_plan(
                df,
                mode="nationwide",
                daily_limit=daily_limit
            )

        st.session_state.days = days
        st.session_state.generated = True

        st.success(
            f"{len(days)} Day Route Plan Generated"
        )

    except Exception as e:

        import traceback

        st.error(str(e))

        st.code(
            traceback.format_exc()
        )


if st.session_state.generated:

    days = st.session_state.days

    st.divider()

    st.header(
        "Route Summary"
    )

    summary_df = get_plan_summary(
        days
    )

    st.dataframe(
        summary_df,
        use_container_width=True
    )

    st.divider()

    if st.checkbox(
        "Show Full Route Map"
    ):

        full_map = create_full_plan_map(
            days
        )

        st_folium(
            full_map,
            width=1400,
            height=700,
            key="full_route_map"
        )

    st.divider()

    for day_no, day in enumerate(
        days,
        start=1
    ):

        st.subheader(
            f"Day {day_no}"
        )

        day_df = pd.DataFrame(
            day
        )

        columns = []

        for col in [
            "Customer name",
            "Town",
            "Pending Visit",
            "Priority",
            "Latitude",
            "Longitude"
        ]:

            if col in day_df.columns:

                columns.append(
                    col
                )

        st.dataframe(
            day_df[
                columns
            ],
            use_container_width=True
        )

        route_parts = (
            build_day_route_urls(
                day
            )
        )

        if len(route_parts) == 1:

            st.link_button(
                f"Open Day {day_no} Route",
                route_parts[0]["url"]
            )

        else:

            st.info(
                f"Day {day_no} split into "
                f"{len(route_parts)} Google Maps routes"
            )

            for part in route_parts:

                st.link_button(
                    (
                        f"Day {day_no} "
                        f"Route {part['part']} "
                        f"({part['start']} - {part['end']})"
                    ),
                    part["url"]
                )

        show_map = st.checkbox(
            f"Show Map Day {day_no}",
            key=f"day_map_{day_no}"
        )

        if show_map:

            day_map = create_day_map(
                day
            )

            st_folium(
                day_map,
                width=1200,
                height=700,
                key=f"folium_{day_no}"
            )

        st.divider()

    st.header(
        "Priority Overview"
    )

    all_rows = []

    for day in days:

        all_rows.extend(
            day
        )

    priority_df = pd.DataFrame(
        all_rows
    )

    summary = priority_summary(
        priority_df
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Visit 1",
        summary["Visit1"]
    )

    col2.metric(
        "Visit 2",
        summary["Visit2"]
    )

    col3.metric(
        "Visit 3",
        summary["Visit3"]
    )

    col4.metric(
        "Completed",
        summary["Completed"]
    )
