import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="AgroAsistent V3.5", layout="wide")

# =========================
# WEATHER KEY
# =========================
WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

# =========================
# SESSION LOG
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
# PLANOVI
# =========================

vocnjak = {
    "Januar": "Mirovanje",
    "Februar": "Rezidba",
    "Mart": "Start vegetacije",
    "April": "Preventiva",
    "Maj": "Cvetanje",
    "Jun": "Rast ploda",
    "Jul": "Stres",
    "Avgust": "Berba",
    "Septembar": "Kasna berba",
    "Oktobar": "Jesenje đubrenje",
    "Novembar": "Bakar",
    "Decembar": "Mirovanje"
}

povrce = {
    "Januar": "Planiranje",
    "Februar": "Rasad",
    "Mart": "Setva",
    "April": "Rasađivanje",
    "Maj": "Intenzivan rast",
    "Jun": "Formiranje ploda",
    "Jul": "Zaštita",
    "Avgust": "Berba"
}

# =========================
# PREPARATI (BAZA)
# =========================

preparati = {

    "Paradajz": ["Bakarni preparat", "Kalcijum", "Mankozeb", "Biostimulator"],
    "Paprika": ["Kalcijum + bor", "Sumpor", "Biostimulator"],
    "Krastavac": ["Sumpor", "Biološki fungicid", "Sistemični fungicid"]
}

# =========================
# AI PREPORUKA (BEZ CHECKBOX)
# =========================
def ai_preporuka(kultura, mesec, w):

    preporuke = []

    base = preparati.get(kultura, [])

    # logika po vremenu
    if w:

        if w["hum"] > 85:
            preporuke.append("Preventivni fungicid zbog visoke vlage")

        if w["rain"]:
            preporuke.append("Odloži prskanje (kiša)")

        if w["wind"] < 10:
            preporuke.append("Moguća folijarna prihrana")

    # logika po fazi
    if mesec in ["Maj", "Jun"]:

        if kultura in ["Paradajz", "Paprika"]:
            preporuke.append("Kalcijum tretman za kvalitet ploda")

    if mesec in ["Jul", "Avgust"]:

        preporuke.append("Stres zaštita + biostimulator")

    # konkretni preparati
    preporuke.append("Preporučeni preparati:")

    for p in base:
        preporuke.append(f"• {p}")

    return preporuke

# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3.5")

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

    kultura = st.selectbox(
        "Kultura",
        ["Voćnjak", "Paradajz", "Paprika", "Krastavac"]
    )

    mesec = st.selectbox(
        "Mesec",
        list(vocnjak.keys())
    )

    st.subheader("🤖 AI preporuka dana")

    ai = ai_preporuka(kultura, mesec, w)

    for a in ai:
        st.write("• " + a)

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

    st.subheader("🧪 Baza preparata")

    for p in preparati[kultura]:

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
