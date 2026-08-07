import streamlit as st
import pandas as pd
import numpy as np
import hopsworks
import os
# import subprocess
import json
import requests
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import ssl
import joblib
from datetime import datetime

load_dotenv()

st.set_page_config(
    page_title="AQI Pulse — Karachi",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# TF_PYTHON = r"C:\Users\Hp\anaconda3\envs\tensorflow_env\python.exe"
KARACHI_LAT, KARACHI_LON = 24.8607, 67.0011


# ────────────────────────────────────────────────────────────────────────────
# THEME — Professional telemetry dashboard (Grafana / Datadog / Bloomberg style)
# Dense, functional, flat dark surface. Color is reserved for AQI severity.
# ────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

        :root {
    --bg: #F0F4F8;
    --surface: #FFFFFF;
    --surface-2: #E8F0FE;
    --border: #D5DEE8;
    --border-strong: #B8C6D6;
    --text: #1A2332;
    --text-muted: #5C6B7F;
    --text-dim: #8B96A5;
    --good: #16A34A;
    --moderate: #CA8A04;
    --sensitive: #EA580C;
    --unhealthy: #DC2626;
    --very: #9333EA;
    --hazard: #BE185D;
    --accent: #2563EB;
}

        html, body, [class*="css"] {
            color: var(--text);
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
        }
        .ring-svg {
    position: absolute;
    top: 0;
    left: 0;
    width: 160px;
    height: 160px;
}
        .ring-svg path {
            cursor: pointer;
            transition: opacity 0.15s;
        }
        .ring-svg path:hover {
            opacity: 0.85;
        }
        .stApp {
            background: var(--bg);
            background-image:
                linear-gradient(rgba(37, 43, 58, 0.35) 1px, transparent 1px),
                linear-gradient(90deg, rgba(37, 43, 58, 0.35) 1px, transparent 1px);
            background-size: 48px 48px;
            background-attachment: fixed;
        }

        h1, h2, h3, h4, h5, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            font-family: 'IBM Plex Sans', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em;
            color: var(--text) !important;
        }

        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header[data-testid="stHeader"] { background: transparent; }

        section[data-testid="stSidebar"] {
            background: var(--surface);
            border-right: 1px solid var(--border);
        }
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] label {
            color: var(--text-muted) !important;
        }
        section[data-testid="stSidebar"] input {
            background: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            border-radius: 4px !important;
        }
        section[data-testid="stSidebar"] button {
            border-radius: 4px !important;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 600;
            font-size: 13px;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }
        div[data-baseweb="tab-highlight"] {
            background: var(--accent) !important;
            height: 2px !important;
        }
        div[data-baseweb="tab-list"] {
            gap: 0 !important;
            border-bottom: 1px solid var(--border);
        }

        /* Utility */
        .tag {
            display: inline-block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            text-transform: uppercase;
            border: 1px solid var(--border);
            border-radius: 3px;
            padding: 2px 8px;
            margin-bottom: 8px;
            background: var(--surface-2);
        }

        .section-header {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-dim);
            margin: 16px 0 10px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid var(--border);
        }

        .panel {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 14px 16px;
        }

        /* ── Hero ── */
        .hero {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 20px 24px;
            margin-bottom: 16px;
        }
        .hero-grid {
            display: grid;
            grid-template-columns: 1fr auto 220px;
            gap: 24px;
            align-items: center;
        }
        .hero-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 4px;
        }
        .hero-aqi {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 52px;
            font-weight: 700;
            line-height: 1;
            letter-spacing: -0.02em;
        }
        .hero-level {
            display: inline-block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 3px 10px;
            border-radius: 3px;
            margin-top: 8px;
            color: #0B0E14;
        }
        .hero-meta {
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 6px;
        }
        .hero-weather {
            text-align: right;
            border-left: 1px solid var(--border);
            padding-left: 24px;
        }
        .hero-temp {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 36px;
            font-weight: 600;
            line-height: 1;
        }
        .hero-cond {
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 4px;
        }
        .hero-icon {
            font-size: 28px;
            line-height: 1;
            margin-bottom: 6px;
        }

        /* ── Spectrum ring (focal) ── */
        .ring-box {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .ring-wrap {
            width: 160px;
            height: 160px;
            position: relative;
        }
        .ring {
            width: 160px;
            height: 160px;
            border-radius: 50%;
            position: absolute;
            top: 0; left: 0;
            background: conic-gradient(from 0deg,
                var(--good) 0deg 36deg,
                var(--moderate) 36deg 72deg,
                var(--sensitive) 72deg 108deg,
                var(--unhealthy) 108deg 144deg,
                var(--very) 144deg 216deg,
                var(--hazard) 216deg 360deg);
        }
        .ring-mask {
            position: absolute;
            top: 22px; left: 22px;
            width: 116px; height: 116px;
            border-radius: 50%;
            background: var(--surface);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 1px solid var(--border);
        }
        .ring-pointer {
            position: absolute;
            top: 50%; left: 50%;
            width: 68px; height: 2px;
            transform-origin: 0 50%;
            background: transparent;
        }
        .ring-pointer:after {
            content: '';
            position: absolute;
            right: -5px; top: -5px;
            width: 12px; height: 12px;
            border-radius: 50%;
            background: #fff;
            border: 2px solid var(--surface);
        }
        .ring-value {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 28px;
            font-weight: 700;
            line-height: 1;
        }
        .ring-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            text-transform: uppercase;
            text-align: center;
            margin-top: 4px;
            padding: 0 6px;
        }

        /* ── Metric tiles ── */
        .tile {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 12px 14px;
            height: 100%;
        }
        .tile-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 4px;
        }
        .tile-value {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 26px;
            font-weight: 600;
            line-height: 1.15;
            color: var(--text);
        }
        .tile-unit {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
            font-weight: 400;
            color: var(--text-dim);
            margin-left: 2px;
        }

        /* ── Day forecast cards ── */
        .day-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 16px 14px;
            text-align: center;
            border-top: 3px solid var(--day-color, var(--good));
        }
        .day-label {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--text-muted);
        }
        .day-value {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 36px;
            font-weight: 700;
            line-height: 1.1;
            margin: 8px 0 6px 0;
            color: var(--day-color, var(--good));
        }
        .day-level {
            display: inline-block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            padding: 2px 8px;
            border-radius: 3px;
            background: var(--day-color, var(--good));
            color: #0B0E14;
        }

        /* ── Recommendation / alert cards ── */
        .rec-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-left: 3px solid var(--rec-color, var(--good));
            border-radius: 4px;
            padding: 12px 14px;
            margin-bottom: 10px;
        }
        .rec-icon {
            font-size: 18px;
            margin-right: 6px;
            vertical-align: middle;
        }
        .rec-title {
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 600;
            font-size: 13px;
            display: inline;
        }
        .rec-text {
            color: var(--text-muted);
            font-size: 12.5px;
            line-height: 1.4;
            margin-top: 4px;
        }

        /* ── Status ── */
        .status-row {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            font-family: 'IBM Plex Mono', monospace;
            margin-bottom: 6px;
            color: var(--text-muted);
        }
        .dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--good);
            flex-shrink: 0;
        }

        /* ── SHAP bars ── */
        .shap-row {
            margin-bottom: 10px;
        }
        .shap-meta {
            display: flex;
            justify-content: space-between;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 12px;
            margin-bottom: 3px;
        }
        .shap-bar-bg {
            background: var(--surface-2);
            border-radius: 2px;
            height: 6px;
        }
        .shap-bar-fill {
            height: 100%;
            border-radius: 2px;
            background: linear-gradient(90deg, var(--good), var(--moderate), var(--unhealthy));
        }

        /* Streamlit overrides for density */
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 12px;
        }
        div[data-testid="stExpander"] {
            border: 1px solid var(--border);
            border-radius: 4px;
            background: var(--surface);
        }
        hr {
            border-color: var(--border);
            margin: 12px 0;
        }
        .stAlert {
            border-radius: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


LEVEL_COLORS = {
    "Good": "var(--good)",
    "Moderate": "var(--moderate)",
    "Unhealthy for Sensitive Groups": "var(--sensitive)",
    "Unhealthy": "var(--unhealthy)",
    "Very Unhealthy": "var(--very)",
    "Hazardous": "var(--hazard)",
}

# Simplified mapping used by aqi_level (matches original thresholds)
LEVEL_COLORS_SIMPLE = {
    "Good": "var(--good)",
    "Unhealthy": "var(--sensitive)",
    "Very Unhealthy": "var(--unhealthy)",
    "Hazardous": "var(--hazard)",
}


def aqi_level(value):
    if value > 300:
        return "Hazardous", "Stay indoors, use an air purifier, wear an N95 mask if you must go out."
    elif value > 200:
        return "Very Unhealthy", "Limit outdoor activity, wear a mask, keep windows closed."
    elif value > 150:
        return "Unhealthy", "Sensitive groups should reduce prolonged outdoor exertion."
    elif value > 100:
        return "Unhealthy for Sensitive Groups", "Sensitive individuals should limit outdoor activity."
    elif value > 50:
        return "Moderate", "Air quality is acceptable; unusually sensitive people should take care."
    else:
        return "Good", "Air quality is safe for normal outdoor activity."


def aqi_color(value):
    level, _ = aqi_level(value)
    return LEVEL_COLORS.get(level, LEVEL_COLORS_SIMPLE.get(level, "var(--text)"))


# ────────────────────────────────────────────────────────────────────────────
# SPECTRUM RING
# ────────────────────────────────────────────────────────────────────────────
def render_ring(value, label="PEAK · 3-DAY"):
    value = max(0, min(float(value), 500))
    angle = (value / 500.0) * 360
    level, _ = aqi_level(value)
    color = aqi_color(value)

    # SVG arcs (start/end angles match the original conic-gradient)
    # Each <title> becomes the hover tooltip
    st.markdown(
        f"""
        <div class="ring-box">
          <div class="ring-wrap">
            <svg class="ring-svg" viewBox="0 0 160 160" width="160" height="160">
              <!-- Good 0-50 -->
              <path d="M80,80 L80,8 A72,72 0 0,1 130.2,28.8 Z" fill="var(--good)">
                <title>Good · AQI 0–50 · Air quality is satisfactory</title>
              </path>
              <!-- Moderate 51-100 -->
              <path d="M80,80 L130.2,28.8 A72,72 0 0,1 151.2,80 Z" fill="var(--moderate)">
                <title>Moderate · AQI 51–100 · Acceptable; sensitive people may notice</title>
              </path>
              <!-- Sensitive 101-150 -->
              <path d="M80,80 L151.2,80 A72,72 0 0,1 130.2,131.2 Z" fill="var(--sensitive)">
                <title>Unhealthy for Sensitive Groups · AQI 101–150</title>
              </path>
              <!-- Unhealthy 151-200 -->
              <path d="M80,80 L130.2,131.2 A72,72 0 0,1 80,152 Z" fill="var(--unhealthy)">
                <title>Unhealthy · AQI 151–200 · Everyone may experience effects</title>
              </path>
              <!-- Very Unhealthy 201-300 -->
              <path d="M80,80 L80,152 A72,72 0 0,1 28.8,131.2 Z" fill="var(--very)">
                <title>Very Unhealthy · AQI 201–300 · Health warnings of emergency conditions</title>
              </path>
              <!-- Hazardous 301-500 -->
              <path d="M80,80 L28.8,131.2 A72,72 0 0,1 80,8 Z" fill="var(--hazard)">
                <title>Hazardous · AQI 301–500 · Serious health effects for everyone</title>
              </path>
            </svg>
            <div class="ring-pointer" style="transform:rotate(calc(-90deg + {angle}deg));"></div>
            <div class="ring-mask">
              <div class="ring-value" style="color:{color};">{value:.1f}</div>
              <div class="ring-label">{label}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────────────────────────────────
# WEATHER
# ────────────────────────────────────────────────────────────────────────────
WEATHER_CODE_MAP = {
    range(0, 1): ("clear", "Clear"),
    range(1, 4): ("cloudy", "Partly cloudy"),
    range(45, 49): ("fog", "Fog"),
    range(51, 68): ("rain", "Drizzle / rain"),
    range(71, 78): ("rain", "Snow"),
    range(80, 83): ("rain", "Showers"),
    range(95, 100): ("rain", "Thunderstorm"),
}


def classify_weather(code):
    for r, (kind, label) in WEATHER_CODE_MAP.items():
        if code in r:
            return kind, label
    return "cloudy", "Overcast"


@st.cache_data(ttl=1800, show_spinner=False)
def get_weather():
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={KARACHI_LAT}"
            f"&longitude={KARACHI_LON}&current_weather=true"
        )
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        cw = r.json()["current_weather"]
        kind, label = classify_weather(int(cw["weathercode"]))
        return {
            "temp": cw["temperature"],
            "wind": cw["windspeed"],
            "kind": kind,
            "label": label,
            "ok": True,
        }
    except Exception:
        return {"temp": None, "wind": None, "kind": "cloudy", "label": "Unavailable", "ok": False}


def weather_icon(kind):
    # Consistent simple symbols (no mixed emoji styles)
    icons = {
        "clear": "☀",
        "cloudy": "☁",
        "rain": "☂",
        "fog": "≡",
    }
    return icons.get(kind, "☁")


def render_hero(weather, current_aqi, gauge_value):
    # Current AQI from latest reading
    if current_aqi is not None:
        level, _ = aqi_level(current_aqi)
        color = aqi_color(current_aqi)
        aqi_html = f'<div class="hero-aqi" style="color:{color};">{current_aqi:.1f}</div>'
        level_html = f'<div class="hero-level" style="background:{color};">{level}</div>'
    else:
        aqi_html = '<div class="hero-aqi" style="color:var(--text-dim);">—</div>'
        level_html = ""

    temp_html = f'{weather["temp"]:.1f}°C' if weather["ok"] else "—"
    wind_html = f'{weather["wind"]:.1f} km/h' if weather["ok"] else "—"
    icon = weather_icon(weather["kind"])

    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-grid">
            <div>
              <div class="hero-label">Current US AQI · Karachi</div>
              {aqi_html}
              {level_html}
              <div class="hero-meta">Live sensor feed · updates on refresh</div>
            </div>
            <div class="hero-weather">
              <div class="hero-icon">{icon}</div>
              <div class="hero-temp">{temp_html}</div>
              <div class="hero-cond">{weather["label"]} · {wind_html}</div>
            </div>
            <div>
        """,
        unsafe_allow_html=True,
    )
    if gauge_value is not None:
        render_ring(gauge_value)
    else:
        st.caption("Forecast ring appears when model output is ready.")
    st.markdown("</div></div></div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# RECOMMENDATIONS
# ────────────────────────────────────────────────────────────────────────────
def build_recommendations(worst_aqi, weather_kind):
    recs = []
    level, _ = aqi_level(worst_aqi)

    if level == "Hazardous":
        recs.append(("▣", "Wear N95 mask", "AQI hazardous — cover up before going outside.", "var(--hazard)"))
        recs.append(("▣", "Stay indoors", "Avoid outdoor activity until levels drop.", "var(--hazard)"))
        recs.append(("▣", "Run air purifier", "Keep indoor air clean, especially bedrooms.", "var(--hazard)"))
    elif level == "Very Unhealthy":
        recs.append(("▣", "Mask outdoors", "Wear a mask if stepping out for extended periods.", "var(--very)"))
        recs.append(("▣", "Keep windows closed", "Limit outdoor air entering the home.", "var(--very)"))
    elif level in ("Unhealthy", "Unhealthy for Sensitive Groups"):
        recs.append(("▣", "Limit prolonged exertion", "Sensitive groups should shorten outdoor workouts.", "var(--sensitive)"))
        recs.append(("▣", "Carry a mask", "Useful during peak traffic hours.", "var(--sensitive)"))
    elif level == "Moderate":
        recs.append(("▣", "Monitor sensitive groups", "Unusually sensitive people should take care outdoors.", "var(--moderate)"))
    else:
        recs.append(("▣", "Normal outdoor activity", "Air quality is safe for usual routines.", "var(--good)"))

    if weather_kind == "rain":
        recs.append(("▣", "Carry umbrella", "Precipitation expected.", "var(--accent)"))
    elif weather_kind == "clear":
        recs.append(("▣", "UV exposure", "Clear skies — consider sun protection midday.", "var(--moderate)"))
    elif weather_kind == "fog":
        recs.append(("▣", "Low visibility", "Drive carefully this morning.", "var(--very)"))

    if weather_kind != "rain" and level in ("Unhealthy", "Very Unhealthy", "Hazardous", "Unhealthy for Sensitive Groups"):
        recs.append(("▣", "Indoor air circulation", "Prefer fan/AC over open windows.", "var(--moderate)"))

    return recs[:6]


def render_recommendation_cards(recs):
    cols = st.columns(min(len(recs), 3))
    for i, (icon, title, text, color) in enumerate(recs):
        with cols[i % len(cols)]:
            st.markdown(
                f"""
                <div class="rec-card" style="--rec-color:{color};">
                    <span class="rec-icon">{icon}</span>
                    <span class="rec-title">{title}</span>
                    <div class="rec-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_day_card(day, value):
    level, _ = aqi_level(value)
    color = aqi_color(value)
    st.markdown(
        f"""
        <div class="day-card" style="--day-color:{color};">
            <div class="day-label">Day {day}</div>
            <div class="day-value">{value:.0f}</div>
            <div class="day-level">{level}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ────────────────────────────────────────────────────────────────────────────
# FEATURE CATEGORIES
# ────────────────────────────────────────────────────────────────────────────
def categorize_features(feature_cols):
    pollutants = []
    weather = []
    temporal = []
    other = []
    pollutant_keys = ("pm", "no2", "so2", "o3", "co", "nh3", "aqi", "pollut")
    weather_keys = ("temp", "humidity", "wind", "pressure", "precip", "cloud", "dew", "uv", "visib")
    temporal_keys = ("hour", "day", "month", "week", "sin", "cos", "is_", "lag", "rolling")

    for c in feature_cols:
        cl = c.lower()
        if any(k in cl for k in pollutant_keys):
            pollutants.append(c)
        elif any(k in cl for k in weather_keys):
            weather.append(c)
        elif any(k in cl for k in temporal_keys):
            temporal.append(c)
        else:
            other.append(c)
    return {
        "Pollutants": pollutants,
        "Weather & Met": weather,
        "Temporal / Engineered": temporal,
        "Other": other,
    }


def render_metric_tiles(latest, cols_list, n_cols=4):
    if not cols_list:
        return
    cols = st.columns(n_cols)
    for i, col in enumerate(cols_list):
        val = latest[col]
        if isinstance(val, (int, float, np.floating)):
            display_val = f"{val:.2f}" if abs(val) < 1000 else f"{val:.1f}"
        else:
            display_val = str(val)
        with cols[i % n_cols]:
            st.markdown(
                f"""
                <div class="tile" style="margin-bottom:10px;">
                    <div class="tile-label">{col.replace('_', ' ')}</div>
                    <div class="tile-value">{display_val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ────────────────────────────────────────────────────────────────────────────
# EMAIL
# ────────────────────────────────────────────────────────────────────────────
def send_alert_email(to_email, subject, body):
    from_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_APP_PASSWORD")
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(from_email, password)
        server.send_message(msg)


# ────────────────────────────────────────────────────────────────────────────
# HOPSWORKS / MODEL (cached)
# ────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def connect_to_hopsworks():
    return hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY"))


@st.cache_resource(show_spinner=False)
def load_feature_group(_project):
    fs = _project.get_feature_store()
    return fs.get_feature_group("aqi_daily_features", version=5)


@st.cache_resource(show_spinner=False)
def get_model_path(_project):
    mr = _project.get_model_registry()
    model = mr.get_model("aqi_predictor_gru", version=1)
    model_dir = model.download()
    return os.path.join(model_dir, "gru_model.h5")


@st.cache_resource(show_spinner=False)
def get_scaler(_project):
    mr = _project.get_model_registry()
    model = mr.get_model("aqi_scaler", version=1)
    model_dir = model.download()
    return joblib.load(os.path.join(model_dir, "scaler.pkl"))

@st.cache_resource(show_spinner=False)
def get_predictions_fg(_project):
    fs = _project.get_feature_store()
    return fs.get_feature_group("aqi_predictions", version=1)



@st.cache_data(ttl=900, show_spinner=False)
def load_features(_feature_group):
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(hours=150)
    query = _feature_group.filter(_feature_group.time >= cutoff)
    df = query.read()
    df["time"] = pd.to_datetime(df["time"])
    return df.sort_values("time").reset_index(drop=True)


import shap
from tensorflow.keras.models import load_model

@st.cache_resource(show_spinner=False)
def load_gru_model(model_path):
    return load_model(model_path, compile=False)

def predict_with_gru(model_path, X, background):
    model = load_gru_model(model_path)
    prediction = model.predict(X, verbose=0)

    explainer = shap.GradientExplainer(model, background)
    shap_values = explainer.shap_values(X)

    shap_array = np.array(shap_values)
    mean_importance = np.mean(np.abs(shap_array), axis=(0, 1, 3)).tolist()

    return prediction, mean_importance


@st.cache_data(ttl=900, show_spinner=False)
def run_prediction(model_path, latest_ts, _X, _background):
    return predict_with_gru(model_path, _X, _background)


# ────────────────────────────────────────────────────────────────────────────
# APP
# ────────────────────────────────────────────────────────────────────────────
inject_css()

with st.sidebar:
    st.markdown("### ◈ AQI PULSE")
    st.caption("Karachi air-quality telemetry")
    st.markdown("---")
    status_placeholder = st.empty()
    st.markdown("---")
    if st.button("↻ Refresh data", use_container_width=True):
        load_features.clear()
        run_prediction.clear()
        get_weather.clear()
        st.rerun()

weather = get_weather()

with st.spinner("Connecting to station..."):
    project = connect_to_hopsworks()
with st.spinner("Loading model & scaler (cached after first run)..."):
    scaler = get_scaler(project)
    feature_group = load_feature_group(project)
    model_path = get_model_path(project)
    predictions_fg = get_predictions_fg(project)

df = load_features(feature_group)
latest_ts = str(df["time"].max()) if "time" in df.columns and len(df) else "n/a"

with st.sidebar:
    status_placeholder.markdown(
        f"""
        <div class="status-row"><span class="dot"></span> Hopsworks connected</div>
        <div class="status-row"><span class="dot"></span> Scaler + model ready</div>
        <div class="status-row"><span class="dot"></span> Data synced · {latest_ts}</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("**Hazard alerts**")
    with st.form("alert_form", clear_on_submit=False):
        user_email = st.text_input(
            "Email for AQI alerts",
            placeholder="you@example.com",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Send this forecast", use_container_width=True)
    st.caption("Sends the current 3-day forecast once. Does not auto-resend.")

feature_cols = [c for c in df.columns if c not in ["time", "aqi_day1", "aqi_day2", "aqi_day3"]]
recent_data = df[feature_cols].tail(24)

prediction, shap_importance = None, None
if len(recent_data) >= 24:
    X_scaled = scaler.transform(recent_data)
    X_input = np.expand_dims(X_scaled, axis=0)
    background_data = df[feature_cols].tail(100).head(24)
    background_scaled = scaler.transform(background_data)
    background_sequence = np.expand_dims(background_scaled, axis=0)
    with st.spinner("Running forecast model..."):
        prediction, shap_importance = run_prediction(
            model_path, latest_ts, X_input, background_sequence
        )
    if prediction is not None and st.session_state.get("logged_for") != latest_ts:
        log_df = pd.DataFrame({
            "prediction_time": [datetime.now()],
            "aqi_day1": [float(prediction[0][0])],
            "aqi_day2": [float(prediction[0][1])],
            "aqi_day3": [float(prediction[0][2])],
            "model_name": ["GRU"],
            "model_version": [1]
        })
        try:
            predictions_fg.insert(log_df)
            st.session_state["logged_for"] = latest_ts
        except Exception as e:
            st.warning(f"Could not log prediction: {e}")

gauge_value = float(np.max(prediction[0])) if prediction is not None else None

# Current AQI from latest row if available
current_aqi = None
if len(df) and "us_aqi" in df.columns:
    current_aqi = float(df["us_aqi"].iloc[-1])
elif len(df) and "aqi" in df.columns:
    current_aqi = float(df["aqi"].iloc[-1])

render_hero(weather, current_aqi, gauge_value)

# Email send (once per forecast + email)
if submitted and user_email and prediction is not None:
    if st.session_state.get("alert_sent_for") != (latest_ts, user_email):
        alert_messages = []
        for i, val in enumerate(prediction[0], start=1):
            level, advice = aqi_level(val)
            alert_messages.append(f"Day {i}: AQI {val:.1f} ({level})\n{advice}")
        full_body = (
            "Dear user,\n\nHere is your 3-day AQI forecast:\n\n"
            + "\n\n".join(alert_messages)
            + "\n\nRegards,\nAQI Predictor"
        )
        try:
            send_alert_email(user_email, "Your 3-Day AQI Forecast", full_body)
            st.session_state["alert_sent_for"] = (latest_ts, user_email)
            st.toast(f"Forecast emailed to {user_email}", icon="✅")
        except Exception as e:
            st.error(f"Could not send alert email: {e}")

tab_overview, tab_forecast, tab_features, tab_history = st.tabs(
    ["Overview", "Forecast", "Feature insights", "History"]
)

# ── Overview ──
with tab_overview:
    st.markdown('<span class="tag">Latest sensor snapshot</span>', unsafe_allow_html=True)

    if len(df):
        latest = df.iloc[-1]
        categories = categorize_features(feature_cols)

        for cat_name, cols_list in categories.items():
            if not cols_list:
                continue
            st.markdown(f'<div class="section-header">{cat_name}</div>', unsafe_allow_html=True)
            render_metric_tiles(latest, cols_list, n_cols=5)

        st.markdown("<br>", unsafe_allow_html=True)
        if prediction is not None:
            st.markdown('<span class="tag">Recommended actions</span>', unsafe_allow_html=True)
            render_recommendation_cards(build_recommendations(gauge_value, weather["kind"]))
        else:
            st.info("Need 24 hours of recent data for a prediction.")

        with st.expander("Raw latest rows"):
            st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.warning("No feature data available.")

# ── Forecast ──
with tab_forecast:
    if prediction is None:
        st.warning("Not enough recent data (need 24 hours) to make a prediction.")
    else:
        st.markdown('<span class="tag">3-day AQI forecast</span>', unsafe_allow_html=True)
        day_cols = st.columns(len(prediction[0]))
        for i, val in enumerate(prediction[0], start=1):
            with day_cols[i - 1]:
                render_day_card(i, val)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="tag">Precautions</span>', unsafe_allow_html=True)
        render_recommendation_cards(build_recommendations(gauge_value, weather["kind"]))

# ── Feature insights ──
with tab_features:
    if shap_importance is None:
        st.info("Feature importance appears once a forecast is generated.")
    else:
        st.markdown('<span class="tag">SHAP · drivers of current forecast</span>', unsafe_allow_html=True)
        shap_df = pd.DataFrame(
            {"feature": feature_cols, "importance": shap_importance}
        ).sort_values("importance", ascending=False)

        max_imp = shap_df["importance"].abs().max() or 1
        for _, row in shap_df.iterrows():
            pct = abs(row["importance"]) / max_imp * 100
            st.markdown(
                f"""
                <div class="shap-row">
                  <div class="shap-meta">
                    <span>{row['feature'].replace('_', ' ')}</span>
                    <span style="color:var(--text-muted);">{row['importance']:.3f}</span>
                  </div>
                  <div class="shap-bar-bg">
                    <div class="shap-bar-fill" style="width:{pct:.0f}%;"></div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("Full importance table"):
            st.dataframe(
                shap_df.style.background_gradient(cmap="viridis", subset=["importance"]),
                use_container_width=True,
            )
        st.bar_chart(shap_df.set_index("feature"))

# ── History ──
@st.cache_data(ttl=900, show_spinner=False)
def load_predictions_log(_predictions_fg):
    pred_df = _predictions_fg.read()
    pred_df["prediction_time"] = pd.to_datetime(pred_df["prediction_time"])
    return pred_df.sort_values("prediction_time")

with tab_history:
    st.markdown('<span class="tag">Actual vs Predicted AQI</span>', unsafe_allow_html=True)

    combined_df = pd.DataFrame()

    if "us_aqi" in df.columns:
        actual_df = df[["time", "us_aqi"]].tail(72).copy()
        actual_df["time"] = pd.to_datetime(actual_df["time"])
        actual_df = actual_df.rename(columns={"us_aqi": "Actual AQI"}).set_index("time")
        combined_df = actual_df

    pred_log = load_predictions_log(predictions_fg)
    if len(pred_log):
        pred_df = pred_log[["prediction_time", "aqi_day1"]].copy()
        pred_df = pred_df.rename(columns={"prediction_time": "time", "aqi_day1": "Predicted AQI"}).set_index("time")
        combined_df = combined_df.join(pred_df, how="outer") if len(combined_df) else pred_df

    if len(combined_df):
        st.line_chart(combined_df)
    else:
        st.info("Not enough data to show the comparison chart.")

    if len(pred_log):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="tag">Browse a previous prediction</span>', unsafe_allow_html=True)
        options = pred_log["prediction_time"].dt.strftime("%Y-%m-%d %H:%M").tolist()[::-1]
        selected = st.selectbox("Select prediction time", options)
        selected_row = pred_log[pred_log["prediction_time"].dt.strftime("%Y-%m-%d %H:%M") == selected].iloc[0]
        st.write(f"Day 1: {selected_row['aqi_day1']:.1f}  |  Day 2: {selected_row['aqi_day2']:.1f}  |  Day 3: {selected_row['aqi_day3']:.1f}")
    else:
        st.info("No predictions logged yet.")