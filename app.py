import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroAsistent V3.2.2", layout="wide")

# =========================
# SECRETS (OBAVEZNO)
# =========================

WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

# =========================
# WEATHER SAFE
# =========================

def weather():

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Krusevac,RS&appid={WEATHER_KEY}&units=metric"
        r = requests.get(url, timeout=5)
        d = r.json()

        return {
            "temp": d["main"]["temp"],
            "hum": d["main"]["humidity"],
            "wind": d["wind"]["speed"] * 3.6,
            "rain": "rain" in d
        }

    except:
        return None

# =========================
# ALARMI
# =========================

def alarms(kultura, w):

    out = []

    if not w:
        return [("⚠️ INFO", "Nema vremenskih podataka")]

    if w["rain"]:
        out.append(("KRITIČNO", "Kiša → bez prskanja"))

    if w["hum"] > 85:
        out.append(("RIZIK", "Visoka vlaga → gljivice"))

    if w["wind"] > 15:
        out.append(("KRITIČNO", "Jak vetar"))

    if kultura == "Paradajz" and w["hum"] > 80:
        out.append(("RIZIK", "Plamenjača"))

    if kultura == "Krastavac" and w["hum"] > 80:
        out.append(("RIZIK", "Pepelnica"))

    return out

# =========================
# KARENCA (SIMPLE)
# =========================

if "spray" not in st.session_state:
    st.session_state.spray = []

def add_spray(name, days):
    st.session_state.spray.append({
        "name": name,
        "end": datetime.now() + timedelta(days=days)
    })

def karenca():

    now = datetime.now()
    active = []

    for s in st.session_state.spray:
        diff = (s["end"] - now).days
        if diff > 0:
            active.append((s["name"], diff))

    return active

# =========================
# PLANOVI
# =========================

vocnjak = {
    "Mart": "Start vegetacije + zaštita (bakar + rezidba)",
    "April": "Preventiva bolesti + prskanje",
    "Maj": "Cvetanje + kalcijum",
    "Jun": "Rast ploda + zaštita",
    "Jul": "Stres + zalivanje",
    "Avgust": "Berba"
}

povrce = {
    "Mart": "Setva",
    "April": "Rasađivanje",
    "Maj": "Rast biljke",
    "Jun": "Zaštita (plamenjača / pepelnica)",
    "Jul": "Intenzivno zalivanje",
    "Avgust": "Berba"
}

# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3.2.2 (Stable)")

tab1, tab2, tab3, tab4 = st.tabs([
    "🚨 Danas",
    "🍎 Voćnjak",
    "🥦 Povrće",
    "📊 Karenca"
])

# =========================
# TAB 1 — DANAS
# =========================

with tab1:

    st.header("🚨 Pametni alarmi")

    w = weather()

    kultura = st.selectbox(
        "Kultura",
        ["Voćnjak", "Paradajz", "Paprika", "Krastavac"]
    )

    a = alarms(kultura, w)

    if not a:
        st.success("Sve OK")

    for t, m in a:

        if t == "KRITIČNO":
            st.error(m)
        else:
            st.warning(m)

    st.subheader("⏳ Karenca")
    for n, d in karenca():
        st.info(f"{n} → {d} dana")

# =========================
# TAB 2 — VOĆNJAK
# =========================

with tab2:

    mesec = st.selectbox("Mesec", list(vocnjak.keys()), key="v")

    st.subheader("🍎 Voćnjak")
    st.info(vocnjak[mesec])

# =========================
# TAB 3 — POVRĆE
# =========================

with tab3:

    kultura = st.selectbox("Kultura", list(povrce.keys()), key="p1")

    mesec = st.selectbox("Mesec", list(povrce.keys()), key="p2")

    st.subheader("🥦 Povrće")
    st.info(povrce[mesec])

# =========================
# TAB 4 — KARENCA
# =========================

with tab4:

    st.header("⏳ Karenca (aktivna)")

    data = karenca()

    if not data:
        st.success("Nema aktivne karence")

    for n, d in data:
        st.warning(f"{n} → {d} dana")
