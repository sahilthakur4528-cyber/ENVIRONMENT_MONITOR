# ==========================================
# Environment Monitoring System
# Configuration File
# ==========================================

import os
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


# ==========================================
# Flask Secret Key
# ==========================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "environment123"
)


# ==========================================
# MySQL Database
# ==========================================

DB_HOST = os.getenv(
    "DB_HOST"
)

DB_PORT = int(
    os.getenv(
        "DB_PORT",
        3306
    )
)

DB_USER = os.getenv(
    "DB_USER"
)

DB_PASSWORD = os.getenv(
    "DB_PASSWORD"
)

DB_NAME = os.getenv(
    "DB_NAME"
)


# ==========================================
# Admin
# ==========================================

ADMIN_EMAIL = "admin@gmail.com"


# ==========================================
# Upload Folder
# ==========================================

UPLOAD_FOLDER = "uploads"


# Maximum Upload Size
# 20 MB

MAX_CONTENT_LENGTH = 20 * 1024 * 1024


# ==========================================
# Allowed Dataset Extensions
# ==========================================

ALLOWED_EXTENSIONS = {
    "csv",
    "xlsx"
}


# ==========================================
# Model Paths
# ==========================================

AQI_MODEL = "models/aqi_model.pkl"

SCALER_MODEL = "models/scaler.pkl"


# ==========================================
# Weather API
# ==========================================

OPENWEATHER_API_KEY = os.getenv(
    "OPENWEATHER_API_KEY"
)