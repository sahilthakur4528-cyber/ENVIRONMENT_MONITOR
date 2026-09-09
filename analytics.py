# ==========================================
# Analytics Module
# Environment Monitoring System
# ==========================================

import pandas as pd
import plotly.express as px

from database import execute_query, fetch_one
from database import fetch_all
from database import *


# ==========================================
# Dashboard Summary
# ==========================================

def dashboard_summary():

    query = """

    SELECT

        temperature,
        humidity,
        pm25,
        pm10,
        aqi

    FROM environment_data

    ORDER BY id DESC

    LIMIT 1

    """

    return fetch_one(query)


# ==========================================
# Load Dataset
# ==========================================

def load_dataset():

    query = """

    SELECT

        date,
        temperature,
        humidity,
        pm25,
        pm10,
        aqi

    FROM environment_data

    ORDER BY date

    """

    data = fetch_all(query)

    return pd.DataFrame(data)


# ==========================================
# AQI Trend
# ==========================================

def aqi_chart():

    df = load_dataset()

    if df.empty:

        return "<h3>No AQI Data Available</h3>"

    fig = px.line(

        df,

        x="date",

        y="aqi",

        title="AQI Trend",

        markers=True

    )

    fig.update_layout(

        template="plotly_white",

        height=420

    )

    return fig.to_html(full_html=False)


# ==========================================
# Temperature Trend
# ==========================================

def temperature_chart():

    df = load_dataset()

    if df.empty:

        return "<h3>No Temperature Data Available</h3>"

    fig = px.line(

        df,

        x="date",

        y="temperature",

        title="Temperature Trend",

        markers=True

    )

    fig.update_layout(

        template="plotly_white",

        height=420

    )

    return fig.to_html(full_html=False)


# ==========================================
# Humidity Trend
# ==========================================

def humidity_chart():

    df = load_dataset()

    if df.empty:

        return "<h3>No Humidity Data Available</h3>"

    fig = px.bar(

        df,

        x="date",

        y="humidity",

        title="Humidity Trend"

    )

    fig.update_layout(

        template="plotly_white",

        height=420

    )

    return fig.to_html(full_html=False)


# ==========================================
# PM2.5 vs PM10
# ==========================================

def pollution_chart():

    df = load_dataset()

    if df.empty:

        return "<h3>No Pollution Data Available</h3>"

    fig = px.line(

        df,

        x="date",

        y=["pm25", "pm10"],

        title="PM2.5 vs PM10"

    )

    fig.update_layout(

        template="plotly_white",

        height=420

    )

    return fig.to_html(full_html=False)


# ==========================================
# AQI Distribution
# ==========================================

def aqi_distribution():

    df = load_dataset()

    if df.empty:

        return "<h3>No AQI Data Available</h3>"

    bins = [0, 50, 100, 150, 200, 300, 500]

    labels = [

        "Good",

        "Moderate",

        "Sensitive",

        "Unhealthy",

        "Very Unhealthy",

        "Hazardous"

    ]

    df["Category"] = pd.cut(

        df["aqi"],

        bins=bins,

        labels=labels,

        include_lowest=True

    )

    category = df["Category"].value_counts().reset_index()

    category.columns = ["Category", "Count"]

    fig = px.pie(

        category,

        names="Category",

        values="Count",

        title="AQI Distribution"

    )

    fig.update_layout(

        template="plotly_white",

        height=420

    )

    return fig.to_html(full_html=False)

# ==========================================
# Pollution Map
# ==========================================

def pollution_map():
    df = pd.read_sql("""
        SELECT city, latitude, longitude, aqi
        FROM environment_data
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
          AND aqi IS NOT NULL
    """, get_connection())

    if df.empty:
        return None

    df["aqi"] = pd.to_numeric(df["aqi"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    df = df.dropna(subset=["latitude", "longitude", "aqi"])

    if df.empty:
        return None

    fig = px.scatter_map(
        df,
        lat="latitude",
        lon="longitude",
        size="aqi",
        color="aqi",
        hover_name="city",
        hover_data={
            "aqi": True,
            "latitude": False,
            "longitude": False
        },
        zoom=4,
        center={
            "lat": 22.5,
            "lon": 79.0
        },
        height=600
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig.to_html(
        full_html=False,
        include_plotlyjs=True
    )

# ==========================================
# Admin Dashboard Summary
# ==========================================

def admin_summary():

    users = fetch_one("""

    SELECT COUNT(*) AS total_users

    FROM users

    """)

    dataset = fetch_one("""

    SELECT COUNT(*) AS total_rows

    FROM environment_data

    """)

    predictions = fetch_one("""

    SELECT COUNT(*) AS total_predictions

    FROM prediction_history

    """)

    avg_aqi = fetch_one("""

    SELECT ROUND(AVG(aqi),2) AS avg_aqi

    FROM environment_data

    """)

    return {

        "users": users["total_users"],

        "dataset": dataset["total_rows"],

        "predictions": predictions["total_predictions"],

        "avg_aqi": avg_aqi["avg_aqi"]

    }

# ==========================================
# Dataset Status
# ==========================================

import pandas as pd


def dataset_status():

    data = fetch_all("""

    SELECT *

    FROM environment_data

    """)

    df = pd.DataFrame(data)

    if df.empty:

        return {

            "rows":0,

            "columns":0,

            "missing":0,

            "duplicates":0,

            "quality":0

        }

    rows = len(df)

    columns = len(df.columns)

    missing = df.isnull().sum().sum()

    duplicates = df.duplicated().sum()

    quality = round(

        ((rows-missing-duplicates)/rows)*100,

        2

    )

    return {

        "rows":rows,

        "columns":columns,

        "missing":missing,

        "duplicates":duplicates,

        "quality":quality

    }

# ==========================================
# Recent Dataset
# ==========================================

def recent_dataset():

    return fetch_one(
        """
        SELECT
            file_name,
            total_rows,
            uploaded_at
        FROM dataset_history
        ORDER BY uploaded_at DESC
        LIMIT 1
        """
    )

# ==========================================
# Dataset History
# ==========================================

def dataset_history():

    query = """
    SELECT

        dh.file_name,

        dh.total_rows,

        dh.total_columns,

        dh.missing_values,

        dh.duplicate_values,

        dh.quality_percentage,

        dh.uploaded_at,

        u.name

    FROM dataset_history dh

    LEFT JOIN users u

    ON dh.uploaded_by = u.id

    ORDER BY dh.uploaded_at DESC
    """

    return fetch_all(query)

    # ==========================================
# Total Users
# ==========================================

def total_users():

    query = """
    SELECT COUNT(*) AS total
    FROM users
    """

    result = fetch_one(query)

    return result["total"]


# ==========================================
# All Users
# ==========================================

def all_users():

    query = """
    SELECT
        id,
        name,
        email,
        role,
        created_at
    FROM users
    ORDER BY id DESC
    """

    return fetch_all(query)


# ==========================================
# Search Users
# ==========================================

def search_users(keyword):

    query = """
    SELECT
        id,
        name,
        email,
        role,
        created_at
    FROM users
    WHERE
        name LIKE %s
        OR email LIKE %s
    ORDER BY id DESC
    """

    value = "%" + keyword + "%"

    return fetch_all(query, (value, value))


# ==========================================
# Delete User
# ==========================================

def delete_user(user_id):

    execute_query(
        """
        DELETE FROM users
        WHERE id=%s
        """,
        (user_id,)
    )

    # ==========================================
# Average AQI
# ==========================================

def average_aqi():

    result = fetch_one("""
        SELECT ROUND(AVG(aqi),2) AS avg_aqi
        FROM environment_data
    """)

    return result["avg_aqi"] if result["avg_aqi"] else 0


# ==========================================
# Maximum AQI
# ==========================================

def maximum_aqi():

    result = fetch_one("""
        SELECT MAX(aqi) AS max_aqi
        FROM environment_data
    """)

    return result["max_aqi"] if result["max_aqi"] else 0


# ==========================================
# Minimum AQI
# ==========================================

def minimum_aqi():

    result = fetch_one("""
        SELECT MIN(aqi) AS min_aqi
        FROM environment_data
    """)

    return result["min_aqi"] if result["min_aqi"] else 0


# ==========================================
# City Wise AQI Chart
# ==========================================

def city_aqi_chart():

    data = fetch_all("""
        SELECT
            city,
            AVG(aqi) AS avg_aqi
        FROM environment_data
        GROUP BY city
        ORDER BY avg_aqi DESC
    """)

    df = pd.DataFrame(data)

    if df.empty:
        return ""

    fig = px.bar(
        df,
        x="city",
        y="avg_aqi",
        color="avg_aqi",
        title="City Wise Average AQI"
    )

    fig.update_layout(height=450)

    return fig.to_html(full_html=False)


# ==========================================
# AQI Category Distribution
# ==========================================

def aqi_category_chart():

    data = fetch_all("""
        SELECT
            category,
            COUNT(*) AS total
        FROM environment_data
        GROUP BY category
    """)

    df = pd.DataFrame(data)

    if df.empty:
        return ""

    fig = px.pie(
        df,
        names="category",
        values="total",
        title="AQI Category Distribution"
    )

    fig.update_layout(height=450)

    return fig.to_html(full_html=False)


# ==========================================
# Recent AQI Records
# ==========================================

def recent_aqi():

    return fetch_all("""
        SELECT
            date,
            city,
            aqi,
            category
        FROM environment_data
        ORDER BY date DESC
        LIMIT 10
    """)

def total_records():

    result = fetch_one("""
        SELECT COUNT(*) AS total
        FROM environment_data
    """)

    return result["total"]





def air_quality_data():

    return fetch_one("""

    SELECT
        city,
        aqi,
        pm25,
        pm10,
        co,
        no2,
        so2,
        o3

    FROM environment_data

    ORDER BY id DESC

    LIMIT 1

    """)

import plotly.express as px
import pandas as pd

def air_quality_trend():

    data = fetch_all("""

    SELECT
        date,
        aqi

    FROM environment_data

    ORDER BY date

    """)

    df = pd.DataFrame(data)

    if df.empty:

        return ""

    fig = px.line(
        df,
        x="date",
        y="aqi",
        title="AQI Trend",
        markers=True
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig.to_html(full_html=False)

def pollutant_chart():

    data = fetch_one("""

    SELECT

        pm25,
        pm10,
        co,
        no2,
        so2,
        o3

    FROM environment_data

    ORDER BY id DESC

    LIMIT 1

    """)

    if not data:

        return ""

    df = pd.DataFrame({

        "Pollutant":[
            "PM2.5",
            "PM10",
            "CO",
            "NO2",
            "SO2",
            "O3"
        ],

        "Value":[

            data["pm25"],
            data["pm10"],
            data["co"],
            data["no2"],
            data["so2"],
            data["o3"]

        ]

    })

    fig = px.bar(

        df,

        x="Pollutant",

        y="Value",

        title="Pollutant Comparison",

        text="Value"

    )

    fig.update_layout(

        template="plotly_white",

        height=420

    )

    return fig.to_html(full_html=False)


# ==========================================
# LIVE WATER QUALITY
# ==========================================

def live_water_quality():

    query = """
        SELECT
            ph,
            city,
            water_temperature,
            turbidity,
            dissolved_oxygen,
            tds,
            wqi,
            created_at
        FROM water_quality
        ORDER BY created_at DESC
        LIMIT 1
    """

    return fetch_one(query)


def water_quality_trend():

    query = """
        SELECT
            created_at,
            wqi
        FROM water_quality
        WHERE wqi IS NOT NULL
        ORDER BY created_at ASC
        LIMIT 50
    """

    data = fetch_all(query)

    if not data:
        return ""

    df = pd.DataFrame(data)

    fig = px.line(
        df,
        x="created_at",
        y="wqi",
        markers=True,
        title=""
    )

    fig.update_layout(
        template="plotly_white",
        height=300,
        margin=dict(
            l=40,
            r=20,
            t=20,
            b=40
        ),
        xaxis_title="Date",
        yaxis_title="WQI"
    )

    return fig.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    )


# ==========================================
# WATER PARAMETERS
# ==========================================

def water_parameter_chart():

    data = live_water_quality()

    if not data:
        return ""

    parameters = [
        "pH",
        "Turbidity",
        "Dissolved Oxygen",
        "TDS"
    ]

    values = [
        data.get("ph"),
        data.get("turbidity"),
        data.get("dissolved_oxygen"),
        data.get("tds")
    ]

    # Remove empty values
    chart_data = []

    for parameter, value in zip(parameters, values):

        if value is not None:

            chart_data.append({
                "Parameter": parameter,
                "Value": float(value)
            })

    if not chart_data:
        return ""

    df = pd.DataFrame(chart_data)

    fig = px.bar(
        df,
        x="Parameter",
        y="Value",
        title="Current Water Parameters",
        text="Value"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_white",
        height=300,
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    return fig.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    )
