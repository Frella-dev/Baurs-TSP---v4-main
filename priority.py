import pandas as pd


def pending_visit(row):

    v1 = str(
        row.get("1st Visit", "NO")
    ).strip().upper()

    v2 = str(
        row.get("2nd Visit", "NO")
    ).strip().upper()

    v3 = str(
        row.get("3rd Visit", "NO")
    ).strip().upper()

    if v1 != "YES":
        return 1

    if v2 != "YES":
        return 2

    if v3 != "YES":
        return 3

    return 999


def pending_visit_text(row):

    visit_no = pending_visit(row)

    if visit_no == 1:
        return "Visit 1"

    if visit_no == 2:
        return "Visit 2"

    if visit_no == 3:
        return "Visit 3"

    return "Completed"


def priority_score(row):

    visit_no = pending_visit(row)

    if visit_no == 1:
        return 100

    if visit_no == 2:
        return 70

    if visit_no == 3:
        return 40

    return 0


def marker_color(row):

    visit_no = pending_visit(row)

    if visit_no == 1:
        return "red"

    if visit_no == 2:
        return "orange"

    if visit_no == 3:
        return "green"

    return "blue"


def customer_status(row):

    visit_no = pending_visit(row)

    if visit_no == 999:
        return "Completed"

    return f"Pending Visit {visit_no}"


def prepare_customers(df):

    df = df.copy()

    df["Pending Visit No"] = df.apply(
        pending_visit,
        axis=1
    )

    df["Pending Visit"] = df.apply(
        pending_visit_text,
        axis=1
    )

    df["Priority"] = df.apply(
        priority_score,
        axis=1
    )

    df["Marker Color"] = df.apply(
        marker_color,
        axis=1
    )

    df["Customer Status"] = df.apply(
        customer_status,
        axis=1
    )

    return df


def get_pending_customers(df):

    df = prepare_customers(df)

    return df[
        df["Pending Visit No"] < 999
    ].copy()


def get_completed_customers(df):

    df = prepare_customers(df)

    return df[
        df["Pending Visit No"] == 999
    ].copy()


def get_visit1_customers(df):

    df = prepare_customers(df)

    return df[
        df["Pending Visit No"] == 1
    ].copy()


def get_visit2_customers(df):

    df = prepare_customers(df)

    return df[
        df["Pending Visit No"] == 2
    ].copy()


def get_visit3_customers(df):

    df = prepare_customers(df)

    return df[
        df["Pending Visit No"] == 3
    ].copy()


def priority_summary(df):

    df = prepare_customers(df)

    return {
        "Visit1": len(
            df[
                df["Pending Visit No"] == 1
            ]
        ),
        "Visit2": len(
            df[
                df["Pending Visit No"] == 2
            ]
        ),
        "Visit3": len(
            df[
                df["Pending Visit No"] == 3
            ]
        ),
        "Completed": len(
            df[
                df["Pending Visit No"] == 999
            ]
        )
    }
