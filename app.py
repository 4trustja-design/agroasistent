import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroAsistent V3.3", layout="wide")

# =========================
# SECRETS
# =========================

WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

# =========================
# WEATHER
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
        return [("INFO", "Nema podataka o vremenu")]

    if w["rain"]:
        out.append(("KRITIČNO", "Kiša → ne prskati"))

    if w["hum"] > 85:
        out.append(("RIZIK", "Visoka vlaga → gljivice"))

    if w["wind"] > 15:
        out.append(("KRITIČNO", "Jak vetar → zabrana prskanja"))

    if kultura == "Paradajz" and w["hum"] > 80:
        out.append(("RIZIK", "Plamenjača rizik"))

    if kultura == "Krastavac" and w["hum"] > 80:
        out.append(("RIZIK", "Pepelnica rizik"))

    if kultura == "Paprika" and w["temp"] > 32:
        out.append(("RIZIK", "Toplotni stres"))

    return out


def split(a):

    hitno, rizik, info = [], [], []

    for t, m in a:

        if t == "KRITIČNO":
            hitno.append(m)
        elif t == "RIZIK":
            rizik.append(m)
        else:
            info.append(m)

    return hitno, rizik, info

# =========================
# KARENCA
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
    "Mart": "Start vegetacije + bakar + rezidba",
    "April": "Preventiva bolesti",
    "Maj": "Cvetanje + kalcijum",
    "Jun": "Rast ploda",
    "Jul": "Zalivanje + stres",
    "Avgust": "Berba"
}

povrce = {
    "Mart": "Setva",
    "April": "Rasađivanje",
    "Maj": "Rast",
    "Jun": "Zaštita",
    "Jul": "Zalivanje",
    "Avgust": "Berba"
}

# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3.3 — Stabilna verzija")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚨 Danas",
    "🍎 Voćnjak",
    "🥦 Povrće",
    "🌤️ Vreme",
    "⏳ Karenca"
])

# =========================
# TAB 1 — DANAS
# =========================

with tab1:

    st.header("🚨 Pametni alarmi + stanje")

    w = weather()

    kultura = st.selectbox(
        "Kultura",
        ["Voćnjak", "Paradajz", "Paprika", "Krastavac"]
    )

    a = alarms(kultura, w)

    hitno, rizik, info = split(a)

    st.subheader("🔥 HITNO")
    for x in hitno:
        st.error(x)

    st.subheader("⚠️ RIZIK")
    for x in rizik:
        st.warning(x)

    st.subheader("ℹ️ INFO")
    for x in info:
        st.info(x)

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

    kultura = st.selectbox(
        "Kultura",
        ["Paradajz", "Paprika", "Krastavac"]
    )

    mesec = st.selectbox(
        "Mesec",
        list(povrce.keys())
    )

    plan_k = {
        "Paradajz": "Plamenjača + kalcijum",
        "Paprika": "Stres + trips",
        "Krastavac": "Pepelnica"
    }

    st.subheader("📌 Kultura")
    st.info(plan_k[kultura])

    st.subheader("📅 Sezona")
    st.write(povrce[mesec])

# =========================
# TAB 4 — VREME
# =========================

with tab4:

    st.header("🌤️ Vreme")

    w = weather()

    if not w:
        st.error("Nema podataka")
    else:
        st.metric("Temperatura", f"{w['temp']} °C")
        st.metric("Vlažnost", f"{w['hum']} %")
        st.metric("Vetар", f"{w['wind']} km/h")

        if w["rain"]:
            st.warning("Kiša u toku / najavljena")

# =========================
# TAB 5 — KARENCA
# =========================

with tab5:

    st.header("⏳ Karenca")

    data = karenca()

    if not data:
        st.success("Nema aktivne karence")

    for n, d in data:
        st.warning(f"{n} → {d} dana")
