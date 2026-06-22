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


OFFICE_LAT = 6.8275814230546725
OFFICE_LON = 79.95698659415302


st.set_page_config(
    page_title="Sales Route Planner V3",
    layout="wide"
)

st.title(
    "Sales Route Planner V3"
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
    min_value=10,
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
                "Select Town",
                towns
            )

    except Exception:
        pass


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
            f"{len(days)} route day(s) generated"
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
        "Plan Summary"
    )

    summary_df = get_plan_summary(
        days
    )

    st.dataframe(
        summary_df,
        use_container_width=True
    )

    st.divider()

    show_full_map = st.checkbox(
        "Show Full Sri Lanka Route Map"
    )

    if show_full_map:

        full_map = create_full_plan_map(
            days,
            OFFICE_LAT,
            OFFICE_LON
        )

        st_folium(
            full_map,
            width=1400,
            height=700,
            key="full_map"
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

        display_cols = []

        for col in [
            "Customer name",
            "Town",
            "Pending Visit",
            "Priority",
            "Latitude",
            "Longitude"
        ]:

            if col in day_df.columns:
                display_cols.append(
                    col
                )

        st.dataframe(
            day_df[
                display_cols
            ],
            use_container_width=True
        )

        route_parts = build_day_route_urls(
            day
        )

        if len(route_parts) == 1:

            st.link_button(
                f"🗺 Open Day {day_no} In Google Maps",
                route_parts[0]["url"]
            )

        else:

            st.warning(
                f"Day {day_no} exceeds Google Maps waypoint limit."
            )

            for part in route_parts:

                st.link_button(
                    (
                        f"🗺 Day {day_no} Route {part['part']} "
                        f"(Stops {part['start']} - {part['end']})"
                    ),
                    part["url"]
                )

        show_map = st.checkbox(
            f"Show Day {day_no} Map",
            key=f"map_{day_no}"
        )

        if show_map:

            day_map = create_day_map(
                day,
                OFFICE_LAT,
                OFFICE_LON
            )

            st_folium(
                day_map,
                width=1200,
                height=700,
                key=f"folium_day_{day_no}"
            )

        st.divider()

    st.header(
        "Priority Overview"
    )

    all_rows = []

    for day in days:
        all_rows.extend(day)

    priority_df = pd.DataFrame(
        all_rows
    )

    summary = priority_summary(
        priority_df
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Visit 1 Pending",
            summary["Visit1"]
        )

    with col2:
        st.metric(
            "Visit 2 Pending",
            summary["Visit2"]
        )

    with col3:
        st.metric(
            "Visit 3 Pending",
            summary["Visit3"]
        )

    with col4:
        st.metric(
            "Completed",
            summary["Completed"]
        )