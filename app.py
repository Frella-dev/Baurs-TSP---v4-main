import pandas as pdimport streamlit as stfrom streamlit_folium import st_folium

from googlemaps import (build_day_route_urls,)

from map import (create_day_map,create_full_plan_map,)

from optimizer import (create_plan,get_plan_summary,)

from priority import (prepare_customers,priority_summary,)

from sheets import (get_towns,load_sheet,)

st.set_page_config(page_title="Pharmaceutical Territory Intelligence System",layout="wide",)

st.title("Pharmaceutical Territory Intelligence System")

if "days" not in st.session_state:st.session_state.days = []

if "generated" not in st.session_state:st.session_state.generated = False

ors_api_key = st.text_input("OpenRouteService API Key (Optional)",type="password",)

sheet_url = st.text_input("Google Sheet URL")

planning_mode = st.radio("Planning Mode",["Nationwide","Area"])

max_stops = st.slider("Maximum Customers Per Day",min_value=5,max_value=20,value=12)

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

if st.button("Generate Route Plan"):

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
        max_stops=max_stops
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

total_customers = sum(
    len(day)
    for day in days
)

total_days = len(days)

if total_days > 0:

    avg_per_day = round(
        total_customers / total_days,
        1
    )

else:

    avg_per_day = 0

st.divider()

st.header(
    "Planning KPIs"
)

summary_df = get_plan_summary(
    days
)

total_km = 0

if (
    not summary_df.empty
    and
    "KM" in summary_df.columns
):

    total_km = round(
        summary_df["KM"].sum(),
        1
    )

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Customers",
    total_customers
)

c2.metric(
    "Planned Days",
    total_days
)

c3.metric(
    "Avg Customers/Day",
    avg_per_day
)

c4.metric(
    "Total KM",
    total_km
)

st.divider()

st.header(
    "Route Summary"
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

    routes = build_day_route_urls(
        day
    )

    for route in routes:

        st.link_button(
            (
                f"Route {route['part']} "
                f"({route['start']} - {route['end']})"
            ),
            route["url"]
        )

    show_map = st.checkbox(
        f"Show Map Day {day_no}",
        key=f"map_{day_no}"
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

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Visit 1",
    summary["Visit1"]
)

c2.metric(
    "Visit 2",
    summary["Visit2"]
)

c3.metric(
    "Visit 3",
    summary["Visit3"]
)

c4.metric(
    "Completed",
    summary["Completed"]
)
