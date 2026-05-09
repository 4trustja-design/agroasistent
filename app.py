import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AgroAsistent V3.4.3", layout="wide")

# =========================
# WEATHER KEY
# =========================
WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

# =========================
# DNEVNIK
# =========================
if "log" not in st.session_state:
    st.session_state.log = []

def log_action(kultura, preparat):
    st.session_state.log.append({
        "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "kultura": kultura,
        "radnja": preparat
    })

# =========================
# VREME
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
def alarms(w):
    out = []

    if not w:
        return [("INFO", "Nema podataka")]

    if w["rain"]:
        out.append(("KRITIČNO", "Kiša → ne prskati"))

    if w["hum"] > 85:
        out.append(("RIZIK", "Visoka vlaga"))

    if w["wind"] > 15:
        out.append(("KRITIČNO", "Jak vetar"))

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
# VOĆNJAK
# =========================
vocnjak = {
    "Januar": "Mirovanje",
    "Februar": "Rezidba",
    "Mart": "Start vegetacije + zaštita",
    "April": "Cvetanje",
    "Maj": "Formiranje ploda",
    "Jun": "Rast ploda",
    "Jul": "Zalivanje",
    "Avgust": "Berba",
    "Septembar": "Kasna berba",
    "Oktobar": "Jesenje đubrenje",
    "Novembar": "Bakar",
    "Decembar": "Mirovanje"
}

# =========================
# POVRĆE
# =========================
povrce = {
    "Januar": "Planiranje",
    "Februar": "Rasad",
    "Mart": "Setva",
    "April": "Rasađivanje",
    "Maj": "Rast",
    "Jun": "Formiranje ploda",
    "Jul": "Zaštita",
    "Avgust": "Berba"
}

# =========================
# PREPARATI (KULTURA + MESEC)
# =========================
preparati = {
    "Paradajz": {
        "Maj": ["Bakarni preparat", "Kalcijum", "Biostimulator"],
        "Jun": ["Mankozeb", "Kalcijum", "Biostimulator"],
        "Jul": ["Biostimulator", "Fungicid"],
        "Avgust": ["Fungicid završni"]
    },
    "Paprika": {
        "Maj": ["Kalcijum + bor", "Biostimulator"],
        "Jun": ["Sumpor", "Kalcijum"],
        "Jul": ["Biostimulator", "Zaštita od gljivica"],
        "Avgust": ["Blagi fungicid"]
    },
    "Krastavac": {
        "Maj": ["Sumpor", "Biološki fungicid"],
        "Jun": ["Biološki fungicid", "Kalcijum"],
        "Jul": ["Sistemični fungicid"],
        "Avgust": ["Završna zaštita"]
    }
}

# =========================
# AI PREPORUKA DANA
# =========================
def ai_preporuka_dana(kultura, mesec, w):

    saveti = []

    if w:

        if w["rain"]:
            saveti.append("🌧️ Kiša → bez zaštite danas")

        if w["hum"] > 85:
            saveti.append("🌫️ Visoka vlaga → rizik gljivica")

        if w["wind"] > 15:
            saveti.append("💨 Jak vetar → ne prskati")

        if w["wind"] < 10 and not w["rain"]:
            saveti.append("🌿 Stabilni uslovi → pogodno za tretman")

    if kultura in ["Paradajz", "Paprika"] and mesec in ["Maj", "Jun"]:
        saveti.append("🧪 Kalcijum je prioritet u ovoj fazi")

    if mesec in ["Jul", "Avgust"]:
        saveti.append("🔥 Stres period → koristi biostimulatore")

    return saveti

# =========================
# UI
# =========================
st.title("🌾 AgroAsistent V3.4.3")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚨 Danas",
    "🍎 Voćnjak",
    "🥦 Povrće",
    "🌤️ Vreme",
    "📓 Dnevnik"
])

# =========================
# TAB 1
# =========================
with tab1:

    w = weather()

    kultura = st.selectbox("Kultura", ["Voćnjak", "Paradajz", "Paprika", "Krastavac"])
    mesec = st.selectbox("Mesec", list(vocnjak.keys()))

    st.subheader("🤖 AI preporuka dana")
    for s in ai_preporuka_dana(kultura, mesec, w):
        st.info(s)

    a = alarms(w)
    h, r, i = split(a)

    st.subheader("🔥 HITNO")
    for x in h:
        st.error(x)

    st.subheader("⚠️ RIZIK")
    for x in r:
        st.warning(x)

    st.subheader("ℹ️ INFO")
    for x in i:
        st.info(x)

# =========================
# TAB 2
# =========================
with tab2:

    mesec = st.selectbox("Mesec", list(vocnjak.keys()), key="v")

    st.info(vocnjak[mesec])

# =========================
# TAB 3
# =========================
with tab3:

    kultura = st.selectbox("Kultura", ["Paradajz", "Paprika", "Krastavac"])
    mesec = st.selectbox("Mesec", list(povrce.keys()))

    st.info(povrce[mesec])

    st.subheader("🧪 Preparati (čekiraj šta si uradio)")

    if mesec in preparati[kultura]:

        for p in preparati[kultura][mesec]:

            col1, col2 = st.columns([0.1, 0.9])

            with col1:

                if st.checkbox("", key=f"{kultura}_{mesec}_{p}"):

                    log_action(kultura, p)
                    st.success("Zabeleženo")

            with col2:

                st.write("• " + p)

# =========================
# TAB 4
# =========================
with tab4:

    w = weather()

    if not w:
        st.error("Nema podataka")
    else:
        st.metric("Temp", w["temp"])
        st.metric("Vlaga", w["hum"])
        st.metric("Vetar", w["wind"])

# =========================
# TAB 5
# =========================
with tab5:

    st.header("📓 Dnevnik")

    if not st.session_state.log:
        st.info("Nema unosa")
    else:
        st.dataframe(pd.DataFrame(st.session_state.log))
