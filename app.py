import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from googlemaps import (
    build_day_route_urls,
)
from map import (
    create_day_map,
    create_full_plan_map,
)
from optimizer import (
    create_plan,
    get_plan_summary,
)
from priority import (
    prepare_customers,
    priority_summary,
)
from sheets import (
    get_towns,
    load_sheet,
)


st.set_page_config(
    page_title="Pharma Route Planner ORS",
    layout="wide",
)

st.title(
    "Pharma Route Planner ORS"
)


if "days" not in st.session_state:
    st.session_state.days = None

if "generated" not in st.session_state:
    st.session_state.generated = False


ors_api_key = st.text_input(
    "OpenRouteService API Key (optional)",
    type="password",
)

sheet_url = st.text_input(
    "Google Sheet URL"
)

planning_mode = st.radio(
    "Planning Mode",
    [
        "Nationwide",
        "Area",
    ],
)

daily_limit = st.number_input(
    "Daily KM Limit",
    min_value=25,
    max_value=500,
    value=160,
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
                towns,
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

        days = create_plan(
            df=df,
            ors_api_key=ors_api_key,
            mode=planning_mode.lower(),
            area=selected_area,
            daily_limit=daily_limit,
        )

        st.session_state.days = days
        st.session_state.generated = True

        st.success(
            f"{len(days)} day(s) generated"
        )

    except Exception as e:
        import traceback

        st.error(
            str(e)
        )

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
        use_container_width=True,
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
            key="full_map",
        )

    st.divider()

    for day_no, day in enumerate(
        days,
        start=1,
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
            "Longitude",
        ]:
            if col in day_df.columns:
                display_cols.append(
                    col
                )

        st.dataframe(
            day_df[
                display_cols
            ],
            use_container_width=True,
        )

        routes = build_day_route_urls(
            day
        )

        for route in routes:
            st.link_button(
                (
                    f"Route {route['part']} "
                    f"({route['start']} - {route['end']})"
                ),
                route["url"],
            )

        show_map = st.checkbox(
            f"Show Map Day {day_no}",
            key=f"map_{day_no}",
        )

        if show_map:
            day_map = create_day_map(
                day
            )

            st_folium(
                day_map,
                width=1200,
                height=700,
                key=f"folium_{day_no}",
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

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Visit 1",
        summary["Visit1"],
    )

    c2.metric(
        "Visit 2",
        summary["Visit2"],
    )

    c3.metric(
        "Visit 3",
        summary["Visit3"],
    )

    c4.metric(
        "Completed",
        summary["Completed"],
    )
