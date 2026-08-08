import streamlit as st
import numpy as np



# THEME
 
def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

        :root {
    --bg: #0B0E14;
    --surface: #12161F;
    --surface-2: #181D28;
    --border: #252B3A;
    --border-strong: #323A4D;
    --text: #E6EAF2;
    --text-muted: #8B93A7;
    --text-dim: #5C6578;
    --good: #22C55E;
    --moderate: #EAB308;
    --sensitive: #F97316;
    --unhealthy: #EF4444;
    --very: #A855F7;
    --hazard: #BE185D;
    --accent: #3B82F6;
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


def render_ring(value, label="PEAK · 3-DAY"):
    value = max(0, min(float(value), 500))
    angle = (value / 500.0) * 360
    level, _ = aqi_level(value)
    color = aqi_color(value)

    st.markdown(
        f"""
        <div class="ring-box">
          <div class="ring-wrap">
            <svg class="ring-svg" viewBox="0 0 160 160" width="160" height="160">
              <path d="M80,80 L80,8 A72,72 0 0,1 130.2,28.8 Z" fill="var(--good)">
                <title>Good · AQI 0–50 · Air quality is satisfactory</title>
              </path>
              <path d="M80,80 L130.2,28.8 A72,72 0 0,1 151.2,80 Z" fill="var(--moderate)">
                <title>Moderate · AQI 51–100 · Acceptable; sensitive people may notice</title>
              </path>
              <path d="M80,80 L151.2,80 A72,72 0 0,1 130.2,131.2 Z" fill="var(--sensitive)">
                <title>Unhealthy for Sensitive Groups · AQI 101–150</title>
              </path>
              <path d="M80,80 L130.2,131.2 A72,72 0 0,1 80,152 Z" fill="var(--unhealthy)">
                <title>Unhealthy · AQI 151–200 · Everyone may experience effects</title>
              </path>
              <path d="M80,80 L80,152 A72,72 0 0,1 28.8,131.2 Z" fill="var(--very)">
                <title>Very Unhealthy · AQI 201–300 · Health warnings of emergency conditions</title>
              </path>
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


def weather_icon(kind):
    icons = {
        "clear": "☀",
        "cloudy": "☁",
        "rain": "☂",
        "fog": "≡",
    }
    return icons.get(kind, "☁")


def render_hero(weather, current_aqi, gauge_value):
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
            <div class="day-value">{value:.1f}</div>
            <div class="day-level">{level}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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