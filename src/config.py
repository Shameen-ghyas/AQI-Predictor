# Holds constants and paths
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"

LAT, LON = 24.8607, 67.0011  # Karachi
API_KEY = os.getenv("HOPSWORKS_API_KEY")
