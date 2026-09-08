from flask import request, jsonify
from flask import Flask
from dotenv import load_dotenv
load_dotenv()
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
from weather import get_weather, get_weather_by_coordinates
from analytics import pollution_map
import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import send_file
from weather import get_weather
from reports import generate_pdf
from database import *
from analytics import *
from config import *
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from model.predict import predict_aqi
from model.predict import aqi_category

from flask import send_file


from analytics import live_water_quality
from analytics import water_quality_trend
from analytics import water_parameter_chart
from analytics import (
    live_water_quality,
    water_quality_trend,
    water_parameter_chart
)

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)
from reports import generate_water_report

ALLOWED_EXTENSIONS = {"csv"}

def allowed_file(filename):

    return "." in filename and \
        filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS


def get_column(df, names):

    for col in df.columns:

        clean = col.strip().lower()

        if clean in [x.lower() for x in names]:

            return col

    return None

# ==========================================
# Flask App
# ==========================================

app = Flask(__name__)

app.secret_key = SECRET_KEY

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# ==========================================
# Home
# ==========================================

@app.route("/")
def home():

    return redirect(url_for("login"))

# ==========================================
# Login
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = fetch_one(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        if user:

            valid = False

            try:
                valid = check_password_hash(
                    user["password"],
                    password
                )
            except:
                pass

            if not valid:
                if user["password"] == password:
                    valid = True

            if valid:

                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["role"] = user["role"]

                flash("Login Successful", "success")

                if user["role"] == "admin":
                 return redirect(url_for("admin_dashboard"))
                else:
                  return redirect(url_for("dashboard"))

        flash("Invalid Email or Password", "error")

        return redirect(url_for("login"))

    return render_template("login.html")

# ==========================================
# Register
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            flash("Passwords do not match.", "error")

            return redirect(url_for("register"))

        user = fetch_one(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        if user:

            flash("Email already registered.", "error")

            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        execute_query(

            """
            INSERT INTO users
            (name,email,password)
            VALUES(%s,%s,%s)
            """,

            (
                name,
                email,
                hashed_password
            )

        )

        flash("Registration successful. Please login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")

# ==========================================
# Dashboard
# ==========================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get dashboard summary
    summary = dashboard_summary()

    # Prevent None summary error
    if summary is None:
        summary = {
            "aqi": 0,
            "temperature": 0,
            "humidity": 0,
            "pm25": 0,
            "pm10": 0
        }

    weather = None

    lat = session.get("latitude")
    lon = session.get("longitude")

    if lat is not None and lon is not None:
        weather = get_weather_by_coordinates(lat, lon)

    return render_template(
        "dashboard.html",
        summary=summary,
        weather=weather,
        aqi_chart=aqi_chart(),
        temperature_chart=temperature_chart(),
        humidity_chart=humidity_chart(),
        pollution_chart=pollution_chart(),
        aqi_distribution=aqi_distribution()
    )


@app.route("/update_location", methods=["POST"])
def update_location():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "User not logged in"
        })


    data = request.get_json()

    latitude = data.get("latitude")

    longitude = data.get("longitude")


    if latitude is None or longitude is None:

        return jsonify({
            "success": False,
            "message": "Location not received"
        })


    weather = get_weather_by_coordinates(
        latitude,
        longitude
    )


    if weather:

        session["weather"] = weather

        session["latitude"] = latitude

        session["longitude"] = longitude

        return jsonify({
            "success": True
        })


    return jsonify({
        "success": False,
        "message": "Weather data not found"
    })
# ==========================================
# Admin_Dashboard
# ==========================================
@app.route("/admin_dashboard")
def admin_dashboard():

    if "user_id" not in session:

        return redirect(url_for("login"))

    if session["role"] != "admin":

        return redirect(url_for("dashboard"))

    summary = admin_summary()

    status = dataset_status()

    recent = recent_dataset()

    return render_template(

        "admin_dashboard.html",

        summary=summary,

        status=status,

        recent=recent,

        aqi_chart=aqi_chart(),

        temperature_chart=temperature_chart()

    )


# ==========================================
# aqi_prediction
# ==========================================

@app.route("/aqi_prediction", methods=["GET", "POST"])
def aqi_prediction():

    if "user_id" not in session:

        return redirect(url_for("login"))

    if request.method == "POST":

        pm25 = float(request.form["pm25"])
        pm10 = float(request.form["pm10"])
        co = float(request.form["co"])
        no2 = float(request.form["no2"])
        so2 = float(request.form["so2"])
        o3 = float(request.form["o3"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])

        prediction = predict_aqi(
            pm25,
            pm10,
            co,
            no2,
            so2,
            o3,
            temperature,
            humidity
        )

        category = aqi_category(prediction)

        execute_query(
            """
            INSERT INTO prediction_history
            (
                user_id,
                temperature,
                humidity,
                pm25,
                pm10,
                predicted_aqi
            )
            VALUES
            (%s,%s,%s,%s,%s,%s)
            """,
            (
                session["user_id"],
                temperature,
                humidity,
                pm25,
                pm10,
                prediction
            )
        )

        return render_template(
            "aqi_prediction.html",
            prediction=prediction,
            category=category
        )

    return render_template("aqi_prediction.html")


# ==========================================
# prediction_history
# ==========================================

@app.route("/prediction_history")
def prediction_history():

    if "user_id" not in session:

        return redirect(url_for("login"))

    history = fetch_all(

        """
        SELECT *

        FROM prediction_history

        WHERE user_id=%s

        ORDER BY created_at DESC
        """,

        (session["user_id"],)

    )

    return render_template(

        "prediction_history.html",

        history=history

    )


# ==========================================
# Download_Report
# ==========================================

@app.route("/download_report")
def download_report():

    history = fetch_all(

        """

        SELECT *

        FROM prediction_history

        WHERE user_id=%s

        """,

        (session["user_id"],)

    )

    pdf = generate_pdf(history)

    return send_file(

        pdf,

        download_name="AQI_Report.pdf",

        as_attachment=True,

        mimetype="application/pdf"

    )



# ==========================================
# Pollution Map
# ==========================================


@app.route("/pollution_map")
def pollution_map_page():

    if "user_id" not in session:

        return redirect(url_for("login"))

    return render_template(

        "pollution_map.html",

        pollution_map=pollution_map()

    )



# ==========================================
# Upload Dataset
# ==========================================

@app.route("/upload_dataset", methods=["GET", "POST"])
def upload_dataset():

    if "user_id" not in session:
        return redirect(url_for("login"))

    # Only Admin
    if session.get("role") != "admin":
        flash("Only Admin can upload dataset", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        if "dataset" not in request.files:
            flash("No file selected", "error")
            return redirect(request.url)

        file = request.files["dataset"]

        if file.filename == "":
            flash("Please select a CSV file", "error")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Only CSV files are allowed", "error")
            return redirect(request.url)

        conn = None
        cursor = None
        path = None

        try:

            # ==========================================
            # Save CSV
            # ==========================================

            filename = secure_filename(file.filename)

            path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(path)

            # ==========================================
            # Read CSV
            # ==========================================

            df = pd.read_csv(path)

            # Clean column names
            df.columns = (
                df.columns
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
            )

            print("CSV Columns:", list(df.columns))

            # ==========================================
            # AUTOMATIC DATASET DETECTION
            # ==========================================

            air_columns = {
                "temperature",
                "humidity",
                "pm25",
                "pm10",
                "aqi"
            }

            water_columns = {
                "ph",
                "water_temperature",
                "turbidity",
                "dissolved_oxygen",
                "tds",
                "wqi"
            }

            csv_columns = set(df.columns)

            is_air = len(
                air_columns.intersection(csv_columns)
            ) >= 3

            is_water = len(
                water_columns.intersection(csv_columns)
            ) >= 4

            # ==========================================
            # DATABASE CONNECTION
            # ==========================================

            conn = get_connection()
            cursor = conn.cursor()

            # ==========================================
            # WATER DATASET
            # ==========================================

            if is_water and not is_air:

                print("Detected: WATER DATASET")

                # Required water columns
                required_water = [
                    "date",
                    "city",
                    "ph",
                    "water_temperature",
                    "turbidity",
                    "dissolved_oxygen",
                    "tds",
                    "wqi"
                ]

                missing_columns = [
                    column
                    for column in required_water
                    if column not in df.columns
                ]

                if missing_columns:

                    flash(
                        "Water dataset missing columns: "
                        + ", ".join(missing_columns),
                        "error"
                    )

                    return redirect(request.url)

                # Delete old water data
                cursor.execute(
                    "DELETE FROM water_quality"
                )

                # Insert water data
                for _, row in df.iterrows():

                    cursor.execute(
                        """
                        INSERT INTO water_quality
                        (
                            date,
                            city,
                            ph,
                            water_temperature,
                            turbidity,
                            dissolved_oxygen,
                            tds,
                            wqi
                        )
                        VALUES
                        (%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            row["date"],
                            row["city"],
                            row["ph"],
                            row["water_temperature"],
                            row["turbidity"],
                            row["dissolved_oxygen"],
                            row["tds"],
                            row["wqi"]
                        )
                    )

                conn.commit()

                flash(
                    "Water Dataset Uploaded Successfully",
                    "success"
                )

                return redirect(
                    url_for("admin_dashboard")
                )

            # ==========================================
            # AIR DATASET
            # ==========================================

            elif is_air:

                print("Detected: AIR DATASET")

                required_air = [
                    "date",
                    "city",
                    "temperature",
                    "humidity",
                    "pm25",
                    "pm10",
                    "aqi",
                    "rainfall"
                ]

                missing_columns = [
                    column
                    for column in required_air
                    if column not in df.columns
                ]

                if missing_columns:

                    flash(
                        "Air dataset missing columns: "
                        + ", ".join(missing_columns),
                        "error"
                    )

                    return redirect(request.url)

                # Optional columns
                optional_columns = [
                    "latitude",
                    "longitude",
                    "co",
                    "no2",
                    "so2",
                    "o3",
                    "category"
                ]

                # Delete old air data
                cursor.execute(
                    "DELETE FROM environment_data"
                )

                # Insert air data
                for _, row in df.iterrows():

                    latitude = (
                        row["latitude"]
                        if "latitude" in df.columns
                        else 0
                    )

                    longitude = (
                        row["longitude"]
                        if "longitude" in df.columns
                        else 0
                    )

                    co = (
                        row["co"]
                        if "co" in df.columns
                        else 0
                    )

                    no2 = (
                        row["no2"]
                        if "no2" in df.columns
                        else 0
                    )

                    so2 = (
                        row["so2"]
                        if "so2" in df.columns
                        else 0
                    )

                    o3 = (
                        row["o3"]
                        if "o3" in df.columns
                        else 0
                    )

                    category = (
                        row["category"]
                        if "category" in df.columns
                        else ""
                    )

                    cursor.execute(
                        """
                        INSERT INTO environment_data
                        (
                            date,
                            city,
                            latitude,
                            longitude,
                            temperature,
                            humidity,
                            pm25,
                            pm10,
                            co,
                            no2,
                            so2,
                            o3,
                            category,
                            aqi,
                            rainfall
                        )
                        VALUES
                        (
                            %s,%s,%s,%s,%s,
                            %s,%s,%s,%s,%s,
                            %s,%s,%s,%s,%s
                        )
                        """,
                        (
                            row["date"],
                            row["city"],
                            latitude,
                            longitude,
                            row["temperature"],
                            row["humidity"],
                            row["pm25"],
                            row["pm10"],
                            co,
                            no2,
                            so2,
                            o3,
                            category,
                            row["aqi"],
                            row["rainfall"]
                        )
                    )

                # ======================================
                # Dataset Statistics
                # ======================================

                total_rows = len(df)
                total_columns = len(df.columns)

                missing_values = int(
                    df.isnull().sum().sum()
                )

                duplicate_values = int(
                    df.duplicated().sum()
                )

                if total_rows > 0:

                    quality = round(
                        (
                            (
                                total_rows
                                - missing_values
                                - duplicate_values
                            )
                            / total_rows
                        ) * 100,
                        2
                    )

                    quality = max(0, quality)

                else:
                    quality = 0

                # ======================================
                # Dataset History
                # ======================================

                cursor.execute(
                    """
                    INSERT INTO dataset_history
                    (
                        file_name,
                        total_rows,
                        total_columns,
                        missing_values,
                        duplicate_values,
                        quality_percentage,
                        uploaded_by
                    )
                    VALUES
                    (%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        filename,
                        total_rows,
                        total_columns,
                        missing_values,
                        duplicate_values,
                        quality,
                        session["user_id"]
                    )
                )

                conn.commit()

                flash(
                    "Air Dataset Uploaded Successfully",
                    "success"
                )

                return redirect(
                    url_for("admin_dashboard")
                )

            # ==========================================
            # UNKNOWN DATASET
            # ==========================================

            else:

                flash(
                    "Dataset type could not be detected. "
                    "Please upload a valid Air or Water CSV.",
                    "error"
                )

                return redirect(request.url)

        # ==========================================
        # ERROR HANDLING
        # ==========================================

        except Exception as e:

            if conn:
                conn.rollback()

            print("UPLOAD ERROR:", e)

            flash(
                f"Upload Error: {e}",
                "error"
            )

            return redirect(request.url)

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # ==========================================
    # GET REQUEST
    # ==========================================

    return render_template("upload_dataset.html")


# ==========================================
# Dataset History
# ==========================================

@app.route("/dataset_history")
def view_dataset_history():

    if "user_id" not in session:

        return redirect(url_for("login"))

    if session["role"] != "admin":

        return redirect(url_for("dashboard"))

    history = dataset_history()

    return render_template(

        "dataset_history.html",

        history=history

    )


# ==========================================
# Users Management
# ==========================================

@app.route("/users")
def users():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("dashboard"))

    keyword = request.args.get("search", "").strip()

    if keyword:
        user_list = search_users(keyword)
    else:
        user_list = all_users()

    return render_template(
        "users.html",
        users=user_list,
        total_users=total_users(),
        keyword=keyword
    )


# ==========================================
# Delete User
# ==========================================

@app.route("/delete_user/<int:user_id>")
def delete_user_route(user_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "admin":
        return redirect(url_for("dashboard"))

    if user_id == session["user_id"]:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("users"))

    delete_user(user_id)

    flash("User deleted successfully.", "success")

    return redirect(url_for("users"))


# ==========================================
# AQI Analysis
# ==========================================

@app.route("/aqi_analysis")
def aqi_analysis():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "admin":
        flash("Access Denied", "error")
        return redirect(url_for("dashboard"))

    return render_template(

    "aqi_analysis.html",

    avg_aqi=average_aqi(),

    max_aqi=maximum_aqi(),

    min_aqi=minimum_aqi(),

    total_records=total_records(),

    city_chart=city_aqi_chart(),

    category_chart=aqi_category_chart(),

    recent_records=recent_aqi()

)


# ==========================================
# Settings
# ==========================================

@app.route("/settings")
def settings():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("settings.html")



@app.route("/airquality")
def air_quality():

    if "user_id" not in session:

        return redirect(url_for("login"))

    data = air_quality_data()

    trend = air_quality_trend()

    chart = pollutant_chart()

    return render_template(

        "airquality.html",

        data=data,

        trend=trend,

        chart=chart

    )


# ==========================================
# WATER QUALITY
# ==========================================

@app.route("/water_quality")
def water_quality():

    if "user_id" not in session:
        return redirect(url_for("login"))

    data = live_water_quality()

    trend = water_quality_trend()

    chart = water_parameter_chart()

    if not data:
        data = {
            "location": "No Data",
            "ph": 0,
            "temperature": 0,
            "turbidity": 0,
            "dissolved_oxygen": 0,
            "tds": 0,
            "wqi": 0,
            "created_at": None
        }

    return render_template(
        "water_quality.html",
        data=data,
        trend=trend,
        chart=chart
    )


# ==========================================
# Reports
# ==========================================


@app.route("/reports")
def reports():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("reports.html")

@app.route("/water_report")
def water_report():

    if "user_id" not in session:
        return redirect(url_for("login"))

    data = live_water_quality()

    if not data:
        return "No water quality data available", 404

    pdf = generate_water_report(data)

    return send_file(
        pdf,
        as_attachment=True,
        download_name="water_quality_report.pdf",
        mimetype="application/pdf"
    )

@app.route("/air_report")
def air_report():

    if "user_id" not in session:
        return redirect(url_for("login"))

    data = air_quality_data()

    if not data:
        return "No air quality data available", 404

    pdf = generate_pdf(data)

    return send_file(
        pdf,
        as_attachment=True,
        download_name="air_quality_report.pdf",
        mimetype="application/pdf"
    )


# ==========================================
# Logout
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("login"))

# ==========================================
# Run App
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)
