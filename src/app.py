import streamlit as st
import pandas as pd
import numpy as np
import hopsworks
import os
import requests
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import ssl
import joblib
from datetime import datetime
import shap
from tensorflow.keras.models import load_model

from ui_component import (
    inject_css,
    aqi_level,
    render_hero,
    build_recommendations,
    render_recommendation_cards,
    render_day_card,
    categorize_features,
    render_metric_tiles,
    classify_weather,
)

load_dotenv()

st.set_page_config(
    page_title="AQI Pulse — Karachi",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

KARACHI_LAT, KARACHI_LON = 24.8607, 67.0011


# ────────────────────────────────────────────────────────────────────────────
# WEATHER
# ────────────────────────────────────────────────────────────────────────────
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
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(hours=150)
    query = _feature_group.filter(_feature_group.time >= cutoff)
    df = query.read()
    df["time"] = pd.to_datetime(df["time"])
    return df.sort_values("time").reset_index(drop=True)


@st.cache_data(ttl=900, show_spinner=False)
def load_predictions_log(_predictions_fg):
    pred_df = _predictions_fg.read()
    pred_df["prediction_time"] = pd.to_datetime(pred_df["prediction_time"])
    return pred_df.sort_values("prediction_time")


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

current_aqi = None
if len(df) and "us_aqi" in df.columns:
    current_aqi = float(df["us_aqi"].iloc[-1])
elif len(df) and "aqi" in df.columns:
    current_aqi = float(df["aqi"].iloc[-1])

render_hero(weather, current_aqi, gauge_value)

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
        st.line_chart(combined_df, color=["#DC2626", "#2563EB"])
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