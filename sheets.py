import pandas as pd
import re
from urllib.parse import parse_qs, urlparse


REQUIRED_COLUMNS = [
    "Customer name",
    "Town",
    "Latitude",
    "Longitude",
    "1st Visit",
    "2nd Visit",
    "3rd Visit"
]


def extract_sheet_id(sheet_url):

    match = re.search(
        r"/d/([a-zA-Z0-9-_]+)",
        sheet_url
    )

    if not match:

        raise Exception(
            "Invalid Google Sheet URL"
        )

    return match.group(1)


def build_csv_url(sheet_url):

    sheet_id = extract_sheet_id(
        sheet_url
    )

    parsed_url = urlparse(
        sheet_url
    )

    query_params = parse_qs(
        parsed_url.query
    )

    gid = query_params.get(
        "gid",
        [None]
    )[0]

    gid_part = ""

    if gid:

        gid_part = f"&gid={gid}"

    return (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/export?format=csv"
        f"{gid_part}"
    )


def load_sheet(sheet_url):

    csv_url = build_csv_url(
        sheet_url
    )

    df = pd.read_csv(
        csv_url
    )

    return clean_sheet(df)


def validate_columns(df):

    missing = []

    for col in REQUIRED_COLUMNS:

        if col not in df.columns:

            missing.append(col)

    if len(missing) > 0:

        raise Exception(
            f"Missing columns: {missing}"
        )


def clean_sheet(df):

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    validate_columns(df)

    df["Customer name"] = (
        df["Customer name"]
        .astype(str)
        .str.strip()
    )

    df["Town"] = (
        df["Town"]
        .astype(str)
        .str.strip()
    )

    df["Latitude"] = pd.to_numeric(
        df["Latitude"],
        errors="coerce"
    )

    df["Longitude"] = pd.to_numeric(
        df["Longitude"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "Latitude",
            "Longitude"
        ]
    )

    for col in [
        "1st Visit",
        "2nd Visit",
        "3rd Visit"
    ]:

        df[col] = (
            df[col]
            .astype(str)
            .str.upper()
            .str.strip()
        )

    return df.reset_index(
        drop=True
    )


def get_all_customers(df):

    return df.copy()


def get_valid_customers(df):

    return df[
        (
            df["Latitude"].notna()
        )
        &
        (
            df["Longitude"].notna()
        )
    ].copy()


def get_towns(df):

    towns = (
        df["Town"]
        .dropna()
        .unique()
        .tolist()
    )

    towns.sort()

    return towns


def filter_by_town(
    df,
    town
):

    if not town:

        return df.copy()

    return df[
        df["Town"]
        .astype(str)
        .str.upper()
        ==
        str(town).upper()
    ].copy()


def get_customer_count(df):

    return len(df)


def get_town_count(df):

    return df["Town"].nunique()


def sheet_summary(df):

    visit1 = len(
        df[
            df["1st Visit"]
            != "YES"
        ]
    )

    visit2 = len(
        df[
            (
                df["1st Visit"]
                == "YES"
            )
            &
            (
                df["2nd Visit"]
                != "YES"
            )
        ]
    )

    visit3 = len(
        df[
            (
                df["1st Visit"]
                == "YES"
            )
            &
            (
                df["2nd Visit"]
                == "YES"
            )
            &
            (
                df["3rd Visit"]
                != "YES"
            )
        ]
    )

    completed = len(
        df[
            (
                df["1st Visit"]
                == "YES"
            )
            &
            (
                df["2nd Visit"]
                == "YES"
            )
            &
            (
                df["3rd Visit"]
                == "YES"
            )
        ]
    )

    return {
        "customers": len(df),
        "towns": df["Town"].nunique(),
        "visit1": visit1,
        "visit2": visit2,
        "visit3": visit3,
        "completed": completed
    }
