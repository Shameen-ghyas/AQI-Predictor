from altair import value
import streamlit as st
import pandas as pd
import numpy as np
import hopsworks
import os
import subprocess
import json
import requests
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import ssl

load_dotenv()

st.set_page_config(page_title="AQI Pulse — Karachi", page_icon="🌈", layout="wide")

TF_PYTHON = r"C:\Users\Hp\anaconda3\envs\tensorflow_env\python.exe"
KARACHI_LAT, KARACHI_LON = 24.8607, 67.0011


# ────────────────────────────────────────────────────────────────────────────
# THEME — "AQI Pulse": the palette IS the real-world AQI colour spectrum
# (green → yellow → orange → red → purple → maroon), full saturation, on a
# deep aurora backdrop. The spectrum ring is the signature element — the
# forecast literally lights up the colour it represents.
# ────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600;700&display=swap');

        :root{
            --bg:#0A0818;
            --panel:rgba(255,255,255,0.055);
            --panel-solid:#14112A;
            --line:rgba(255,255,255,0.10);
            --ink:#F6F4FF;
            --ink-dim:#B3ADD6;
            --good:#2FE07C;
            --moderate:#FFDB4D;
            --sensitive:#FF9E3D;
            --unhealthy:#FF4D6D;
            --very:#B45CFF;
            --hazard:#FF2E9E;
        }

        html, body, [class*="css"]{ color:var(--ink); }
        body, p, div, span, li { font-family:'Inter', sans-serif; }

        .stApp{
            background:var(--bg);
            background-image:
                radial-gradient(900px 600px at 8% 0%, rgba(47,224,124,0.20), transparent 55%),
                radial-gradient(900px 650px at 95% 10%, rgba(180,92,255,0.22), transparent 55%),
                radial-gradient(800px 600px at 50% 100%, rgba(255,78,110,0.16), transparent 55%),
                linear-gradient(180deg, #0A0818 0%, #100C24 100%);
            background-attachment:fixed;
            animation:hue 30s ease-in-out infinite alternate;
        }
        @keyframes hue{
            0%{ filter:hue-rotate(0deg); }
            100%{ filter:hue-rotate(14deg); }
        }

        h1,h2,h3,h4,h5, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3{
            font-family:'Outfit', sans-serif !important;
            font-weight:700 !important;
            letter-spacing:-0.01em;
            color:var(--ink) !important;
        }

        #MainMenu {visibility:hidden;}
        footer {visibility:hidden;}
        header[data-testid="stHeader"]{ background:transparent; }

        section[data-testid="stSidebar"]{
            background:#0D0A1F;
            border-right:1px solid var(--line);
        }
        section[data-testid="stSidebar"] input{
            background:#1B1836 !important; border:1px solid rgba(255,255,255,0.15) !important; color:var(--ink) !important;
        }

        button[data-baseweb="tab"]{ font-family:'Outfit', sans-serif; font-weight:600; }
        div[data-baseweb="tab-highlight"]{
            background:linear-gradient(90deg,var(--good),var(--moderate),var(--unhealthy),var(--very)) !important;
            height:3px !important;
        }

        .tag{
            display:inline-block;font-family:'JetBrains Mono',monospace;font-size:0.68rem;
            letter-spacing:0.09em;color:var(--ink-dim);text-transform:uppercase;
            border:1px solid var(--line);border-radius:20px;padding:3px 11px;margin-bottom:10px;
            background:rgba(255,255,255,0.03);
        }

        .panel{
            background:var(--panel);border:1px solid var(--line);border-radius:18px;
            padding:20px 22px;backdrop-filter:blur(10px);
        }

        /* ---- hero ---- */
        .hero-head{display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:14px;}
        .hero-title{font-family:'Outfit',sans-serif;font-size:1.7rem;font-weight:800;margin:0;
            background:linear-gradient(90deg,#fff,var(--ink-dim));-webkit-background-clip:text;background-clip:text;}
        .hero-sub{color:var(--ink-dim);font-size:0.82rem;}
        .hero-temp{font-family:'JetBrains Mono',monospace;font-size:2.4rem;font-weight:700;}
        .hero-cond{color:var(--ink-dim);font-size:0.85rem;text-align:right;}

        /* ---- weather icon ---- */
        .wicon{width:54px;height:54px;display:flex;align-items:center;justify-content:center;}
        .sun{width:36px;height:36px;border-radius:50%;
             background:radial-gradient(circle at 35% 35%, #FFF3B0, var(--moderate));
             box-shadow:0 0 26px 6px rgba(255,219,77,0.55);animation:spin 14s linear infinite;}
        @keyframes spin{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}
        .cloud{width:44px;height:22px;background:linear-gradient(135deg,#8FE1FF,#B45CFF);border-radius:40px;position:relative;animation:drift 4.5s ease-in-out infinite;opacity:0.9;}
        .cloud:before,.cloud:after{content:'';position:absolute;background:inherit;border-radius:50%;}
        .cloud:before{width:22px;height:22px;top:-11px;left:6px;}
        .cloud:after{width:16px;height:16px;top:-8px;left:24px;}
        @keyframes drift{0%,100%{transform:translateX(0);}50%{transform:translateX(6px);}}
        .rain{position:relative;width:54px;height:44px;}
        .rain .cloud{position:absolute;top:0;left:2px;}
        .drop{width:3px;height:9px;background:var(--good);border-radius:2px;position:absolute;top:26px;animation:fall 1s linear infinite;}
        .drop:nth-child(2){left:13px;animation-delay:0.2s;}
        .drop:nth-child(3){left:24px;animation-delay:0.4s;}
        .drop:nth-child(4){left:35px;animation-delay:0.6s;}
        @keyframes fall{0%{transform:translateY(0);opacity:1;}100%{transform:translateY(14px);opacity:0;}}
        .fog{width:54px;display:flex;flex-direction:column;gap:6px;justify-content:center;}
        .fog-line{height:5px;border-radius:3px;background:linear-gradient(90deg,var(--very),var(--ink-dim));opacity:0.65;animation:driftf 3s ease-in-out infinite;}
        .fog-line:nth-child(2){opacity:0.5;animation-delay:0.4s;}
        .fog-line:nth-child(3){opacity:0.35;animation-delay:0.8s;}
        @keyframes driftf{0%,100%{transform:translateX(-4px);}50%{transform:translateX(4px);}}

        /* ---- spectrum ring (signature element) ---- */
        .ring-box{display:flex;flex-direction:column;align-items:center;}
        .ring-wrap{width:190px;height:190px;position:relative;}
        .ring{
            width:190px;height:190px;border-radius:50%;position:absolute;top:0;left:0;
            background:conic-gradient(from 0deg,
                var(--good) 0deg 36deg,
                var(--moderate) 36deg 72deg,
                var(--sensitive) 72deg 108deg,
                var(--unhealthy) 108deg 144deg,
                var(--very) 144deg 216deg,
                var(--hazard) 216deg 360deg);
            filter:saturate(1.15);
        }
        .ring-mask{
            position:absolute;top:30px;left:30px;width:130px;height:130px;border-radius:50%;
            background:var(--panel-solid);display:flex;flex-direction:column;align-items:center;justify-content:center;
            border:1px solid var(--line);
        }
        .ring-pointer{
            position:absolute;top:50%;left:50%;width:95px;height:2px;transform-origin:0 50%;
        }
        .ring-pointer:after{
            content:'';position:absolute;right:-7px;top:-7px;width:16px;height:16px;border-radius:50%;
            background:#fff;box-shadow:0 0 14px 5px rgba(255,255,255,0.9);
            animation:pulse 1.6s ease-in-out infinite;
        }
        @keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.25);}}
        .ring-value{font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;}
        .ring-label{font-family:'JetBrains Mono',monospace;font-size:0.65rem;letter-spacing:0.08em;color:var(--ink-dim);text-transform:uppercase;text-align:center;padding:0 8px;}

        /* ---- recommendation card ---- */
        .rec-card{
            border:1px solid var(--line);border-radius:16px;padding:16px 18px;background:var(--panel);height:100%;
            box-shadow:0 0 0 1px rgba(255,255,255,0.02), 0 8px 24px -12px var(--rec-color, var(--good));
            border-top:3px solid var(--rec-color, var(--good));
        }
        .rec-icon{font-size:1.6rem;}
        .rec-title{font-family:'Outfit',sans-serif;font-weight:700;font-size:0.95rem;margin:8px 0 4px 0;}
        .rec-text{color:var(--ink-dim);font-size:0.83rem;line-height:1.45;}

        /* ---- day forecast card ---- */
        .day-card{
            border:1px solid var(--line);border-radius:18px;padding:18px;background:var(--panel);text-align:center;
            box-shadow:0 8px 28px -14px var(--day-color, var(--good));
        }
        .day-label{font-family:'JetBrains Mono',monospace;color:var(--ink-dim);font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase;}
        .day-value{font-family:'JetBrains Mono',monospace;font-size:2.2rem;font-weight:700;margin:6px 0;
            color:var(--day-color, var(--good));}
        .day-level{display:inline-block;padding:3px 11px;border-radius:20px;font-size:0.72rem;font-weight:700;
            font-family:'JetBrains Mono',monospace;background:var(--day-color, var(--good));color:#0A0818;}

        /* ---- feature tile ---- */
        .tile{border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:var(--panel);}
        .tile-label{font-family:'JetBrains Mono',monospace;color:var(--ink-dim);font-size:0.66rem;letter-spacing:0.05em;text-transform:uppercase;}
        .tile-value{font-family:'JetBrains Mono',monospace;font-size:1.25rem;font-weight:700;margin-top:2px;
            background:linear-gradient(90deg,var(--good),var(--very));-webkit-background-clip:text;background-clip:text;color:transparent;}

        .status-row{display:flex;align-items:center;gap:8px;font-size:0.78rem;margin-bottom:5px;color:var(--ink-dim);}
        .dot{width:7px;height:7px;border-radius:50%;background:var(--good);box-shadow:0 0 8px var(--good);}

        hr{border-color:var(--line);}
        </style>
        """,
        unsafe_allow_html=True,
    )


LEVEL_COLORS = {
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
    else:
        return "Good", "Air quality is safe for normal outdoor activity."


# ────────────────────────────────────────────────────────────────────────────
# SPECTRUM RING (signature visual element) — full AQI colour scale as a ring,
# with a glowing marker at the forecast value's position.
# ────────────────────────────────────────────────────────────────────────────
def render_ring(value, label="TOMORROW · PEAK AQI"):
    value = max(0, min(value, 500))
    angle = (value / 500.0) * 360
    level, _ = aqi_level(value)
    color = LEVEL_COLORS[level]
    st.markdown(
        f"""
        <div class="ring-box">
          <div class="ring-wrap">
            <div class="ring"></div>
            <div class="ring-pointer" style="transform:rotate(calc(-90deg + {angle}deg));"></div>
            <div class="ring-mask">
              <div class="ring-value" style="color:{color};">{value:.0f}</div>
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
    range(0, 1): ("clear", "Clear sky"),
    range(1, 4): ("cloudy", "Partly cloudy"),
    range(45, 49): ("fog", "Foggy"),
    range(51, 68): ("rain", "Drizzle / rain"),
    range(71, 78): ("rain", "Snow"),
    range(80, 83): ("rain", "Rain showers"),
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
        return {"temp": cw["temperature"], "wind": cw["windspeed"], "kind": kind, "label": label, "ok": True}
    except Exception:
        return {"temp": None, "wind": None, "kind": "cloudy", "label": "Unavailable", "ok": False}


def weather_icon_html(kind):
    if kind == "clear":
        return '<div class="wicon"><div class="sun"></div></div>'
    if kind == "fog":
        return '<div class="wicon"><div class="fog"><div class="fog-line" style="width:38px"></div><div class="fog-line" style="width:28px"></div><div class="fog-line" style="width:32px"></div></div></div>'
    if kind == "rain":
        return '<div class="wicon"><div class="rain"><div class="cloud"></div><div class="drop"></div><div class="drop"></div><div class="drop"></div><div class="drop"></div></div></div>'
    return '<div class="wicon"><div class="cloud"></div></div>'


def render_hero(weather, gauge_value):
    icon_html = weather_icon_html(weather["kind"])
    temp_html = f'{weather["temp"]:.0f}°C' if weather["ok"] else "—"
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown('<span class="tag">🜁 Live · Karachi</span>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="panel" style="margin-bottom:16px;">
              <div class="hero-head">
                <div style="display:flex;align-items:center;gap:14px;">
                  {icon_html}
                  <div>
                    <p class="hero-title">Karachi</p>
                    <p class="hero-sub">Ambient conditions · refreshes every 30 min</p>
                  </div>
                </div>
                <div>
                  <div class="hero-temp" style="text-align:right;">{temp_html}</div>
                  <div class="hero-cond">{weather["label"]}{f" · wind {weather['wind']:.0f} km/h" if weather["ok"] else ""}</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<span class="tag">Spectrum forecast</span>', unsafe_allow_html=True)
        st.markdown('<div class="panel" style="display:flex;justify-content:center;">', unsafe_allow_html=True)
        if gauge_value is not None:
            render_ring(gauge_value)
        else:
            st.caption("The ring lights up once tomorrow's forecast is ready.")
        st.markdown("</div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# RECOMMENDATIONS
# ────────────────────────────────────────────────────────────────────────────
def build_recommendations(worst_aqi, weather_kind):
    recs = []
    level, _ = aqi_level(worst_aqi)

    if level == "Hazardous":
        recs.append(("😷", "Wear an N95 mask", "AQI is hazardous — cover up before stepping outside.", "var(--hazard)"))
        recs.append(("🚪", "Stay indoors", "Avoid outdoor activity entirely until levels drop.", "var(--hazard)"))
        recs.append(("🌬️", "Run an air purifier", "Keep indoor air clean, especially in bedrooms.", "var(--hazard)"))
    elif level == "Very Unhealthy":
        recs.append(("😷", "Mask up outdoors", "Wear a mask if you need to step out for long.", "var(--unhealthy)"))
        recs.append(("🪟", "Keep windows closed", "Limit outdoor air from entering your home.", "var(--unhealthy)"))
    elif level == "Unhealthy":
        recs.append(("🏃", "Limit prolonged exertion", "Sensitive groups should shorten outdoor workouts.", "var(--sensitive)"))
        recs.append(("😷", "Carry a mask", "Useful during peak traffic hours.", "var(--sensitive)"))
    else:
        recs.append(("🌳", "Enjoy the outdoors", "Air quality is safe for normal activity today.", "var(--good)"))

    if weather_kind == "rain":
        recs.append(("☂️", "Carry an umbrella", "Rain expected — pack one before heading out.", "var(--good)"))
    elif weather_kind == "clear":
        recs.append(("🧴", "Use sunscreen", "Clear skies mean stronger UV exposure midday.", "var(--moderate)"))
    elif weather_kind == "fog":
        recs.append(("🚗", "Drive carefully", "Low visibility on the roads this morning.", "var(--very)"))

    if weather_kind != "rain" and level in ("Unhealthy", "Very Unhealthy", "Hazardous"):
        recs.append(("🌀", "Use a fan/AC indoors", "Keep air circulating instead of opening windows.", "var(--moderate)"))

    return recs[:6]


def render_recommendation_cards(recs):
    cols = st.columns(min(len(recs), 3))
    for i, (icon, title, text, color) in enumerate(recs):
        with cols[i % len(cols)]:
            st.markdown(
                f"""
                <div class="rec-card" style="--rec-color:{color}; margin-bottom:14px;">
                    <div class="rec-icon">{icon}</div>
                    <div class="rec-title">{title}</div>
                    <div class="rec-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_day_card(day, value):
    level, _ = aqi_level(value)
    color = LEVEL_COLORS[level]
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
# HOPSWORKS / MODEL LOADING — cached so they run once per session, not once
# per rerun. This is the main lever for perceived speed.
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


import joblib


@st.cache_resource(show_spinner=False)
def get_scaler(_project):
    mr = _project.get_model_registry()
    model = mr.get_model("aqi_scaler", version=1)
    model_dir = model.download()
    return joblib.load(os.path.join(model_dir, "scaler.pkl"))


# Cache the feature-store READ itself — this was re-fetched over the network
# on every single rerun before (e.g. every keystroke in the email box).
@st.cache_data(ttl=900, show_spinner=False)
def load_features(_feature_group):
    return _feature_group.read()


def predict_with_gru(model_path, X, background):
    input_data = json.dumps({"X": X.tolist(), "background": background.tolist()})
    result = subprocess.run(
        [TF_PYTHON, "src/predict_worker.py", model_path],
        input=input_data,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        st.error(f"Prediction failed: {result.stderr}")
        return None, None
    output = json.loads(result.stdout)
    return np.array(output["prediction"]), output["shap_importance"]


# Cache the (slow) subprocess prediction call itself, keyed only on the
# latest timestamp in the data — so it only re-runs when new data actually
# lands, not on every widget interaction. Leading underscore = not hashed.
@st.cache_data(ttl=900, show_spinner=False)
def run_prediction(model_path, latest_ts, _X, _background):
    return predict_with_gru(model_path, _X, _background)


# ────────────────────────────────────────────────────────────────────────────
# APP
# ────────────────────────────────────────────────────────────────────────────
inject_css()

with st.sidebar:
    st.markdown("### 🌈 AQI PULSE")
    st.caption("Karachi air-quality telemetry")
    st.markdown("---")
    status_placeholder = st.empty()
    st.markdown("---")
    if st.button("↻ Refresh data now", use_container_width=True):
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
    st.markdown("**🔔 Hazard alerts**")
    with st.form("alert_form", clear_on_submit=False):
        user_email = st.text_input("Email for AQI alerts", placeholder="you@example.com", label_visibility="collapsed")
        submitted = st.form_submit_button("Send me this forecast", use_container_width=True)
    st.caption("Submitting sends the current 3-day forecast once — it won't resend on its own.")

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
        prediction, shap_importance = run_prediction(model_path, latest_ts, X_input, background_sequence)

gauge_value = float(np.max(prediction[0])) if prediction is not None else None
render_hero(weather, gauge_value)

# ---- Send email only once per new forecast, on explicit form submit ----
if submitted and user_email and prediction is not None:
    if st.session_state.get("alert_sent_for") != (latest_ts, user_email):
        alert_messages = []
        for i, val in enumerate(prediction[0], start=1):
            level, advice = aqi_level(val)
            alert_messages.append(f"Day {i}: AQI {val:.0f} ({level})\n{advice}")
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
    ["🏠 Overview", "📈 Forecast & alerts", "🔍 Feature insights", "📊 History"]
)

# ---- Overview: every feature covers the page, not just a handful ----
with tab_overview:
    st.markdown('<span class="tag">All sensor channels · latest reading</span>', unsafe_allow_html=True)
    latest = df.iloc[-1]
    n_cols = 5
    cols = st.columns(n_cols)
    for i, col in enumerate(feature_cols):
        val = latest[col]
        display_val = f"{val:.2f}" if isinstance(val, (int, float, np.floating)) else str(val)
        with cols[i % n_cols]:
            st.markdown(
                f"""
                <div class="tile" style="margin-bottom:12px;">
                    <div class="tile-label">{col.replace('_',' ')}</div>
                    <div class="tile-value">{display_val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    if prediction is not None:
        st.markdown('<span class="tag">Tomorrow at a glance</span>', unsafe_allow_html=True)
        render_recommendation_cards(build_recommendations(gauge_value, weather["kind"]))
    else:
        st.info("Not enough recent data (need 24 hours) to make a prediction yet.")

    with st.expander("View raw latest rows"):
        st.dataframe(df.tail(10), use_container_width=True)

# ---- Forecast ----
with tab_forecast:
    if prediction is None:
        st.warning("Not enough recent data (need 24 hours) to make a prediction.")
    else:
        st.markdown('<span class="tag">3-day forecast</span>', unsafe_allow_html=True)
        day_cols = st.columns(len(prediction[0]))
        for i, val in enumerate(prediction[0], start=1):
            with day_cols[i - 1]:
                render_day_card(i, val)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="tag">Recommended precautions</span>', unsafe_allow_html=True)
        render_recommendation_cards(build_recommendations(gauge_value, weather["kind"]))

# ---- Feature insights ----
with tab_features:
    if shap_importance is None:
        st.info("Feature importance will appear here once a forecast is generated.")
    else:
        st.markdown('<span class="tag">What is driving the forecast</span>', unsafe_allow_html=True)
        shap_df = pd.DataFrame(
            {"feature": feature_cols, "importance": shap_importance}
        ).sort_values("importance", ascending=False)

        max_imp = shap_df["importance"].abs().max() or 1
        for _, row in shap_df.iterrows():
            pct = abs(row["importance"]) / max_imp * 100
            st.markdown(
                f"""
                <div style="margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:3px;font-family:'JetBrains Mono',monospace;">
                    <span>{row['feature'].replace('_',' ')}</span>
                    <span style="color:var(--ink-dim);">{row['importance']:.3f}</span>
                  </div>
                  <div style="background:rgba(255,255,255,0.08);border-radius:6px;height:8px;">
                    <div style="width:{pct:.0f}%;background:linear-gradient(90deg,var(--good),var(--moderate),var(--unhealthy),var(--very));height:100%;border-radius:6px;"></div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("View full feature importance table"):
            st.dataframe(
                shap_df.style.background_gradient(cmap="plasma", subset=["importance"]),
                use_container_width=True,
            )
        st.bar_chart(shap_df.set_index("feature"))

# ---- History ----
with tab_history:
    st.markdown('<span class="tag">Historical AQI · last 72 hours</span>', unsafe_allow_html=True)
    history_df = df[["time", "us_aqi"]].tail(72).copy()
    history_df["time"] = pd.to_datetime(history_df["time"])
    history_df = history_df.set_index("time")
    st.line_chart(history_df.rename(columns={"us_aqi": "Actual AQI"}))