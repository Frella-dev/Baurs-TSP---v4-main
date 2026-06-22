import pandas as pd
import re


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

    return (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/export?format=csv"
    )


def load_sheet(sheet_url):

    csv_url = build_csv_url(
        sheet_url
    )

    df = pd.read_csv(
        csv_url
    )

    return clean_sheet(df)


def clean_sheet(df):

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    validate_columns(df)

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
            .str.strip()
            .str.upper()
        )

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

    return df


def validate_columns(df):

    missing = []

    for col in REQUIRED_COLUMNS:

        if col not in df.columns:

            missing.append(col)

    if missing:

        raise Exception(
            f"Missing columns: {missing}"
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


def sheet_summary(df):

    return {
        "customers": len(df),
        "towns": df["Town"].nunique(),
        "visit1_no": len(
            df[
                df["1st Visit"]
                != "YES"
            ]
        ),
        "visit2_no": len(
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
        ),
        "visit3_no": len(
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
    }