import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroAsistent V3.2.1", layout="wide")

# =========================
# SECRETS
# =========================

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USER = st.secrets["GITHUB_USER"]
REPO = st.secrets["REPO_NAME"]
WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

FILE = "dnevnik.csv"

# =========================
# STATE
# =========================

if "prskanja" not in st.session_state:
    st.session_state.prskanja = []

# =========================
# WEATHER
# =========================

def weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Krusevac,RS&appid={WEATHER_KEY}&units=metric"
    r = requests.get(url)

    if r.status_code != 200:
        return None

    d = r.json()

    return {
        "temp": d["main"]["temp"],
        "hum": d["main"]["humidity"],
        "wind": d["wind"]["speed"] * 3.6,
        "rain": "rain" in d
    }

# =========================
# ALARMI
# =========================

def pametni_alarmi(kultura, w):

    alarmi = []

    if not w:
        return [("⚠️ INFO", "Nema podataka o vremenu")]

    if w["rain"]:
        alarmi.append(("🚫 KRITIČNO", "Kiša → ne prskati"))

    if w["hum"] > 85:
        alarmi.append(("⚠️ RIZIK", "Visoka vlaga → gljivice"))

    if w["wind"] > 15:
        alarmi.append(("🚫 KRITIČNO", "Jak vetar → zabrana prskanja"))

    if kultura == "Paradajz":
        if w["hum"] > 80:
            alarmi.append(("⚠️ RIZIK", "Plamenjača moguća"))
        if w["temp"] > 30:
            alarmi.append(("ℹ️ INFO", "Kalcijum + zalivanje"))

    if kultura == "Paprika":
        if w["temp"] > 32:
            alarmi.append(("⚠️ RIZIK", "Toplotni stres"))

    if kultura == "Krastavac":
        if w["hum"] > 80:
            alarmi.append(("⚠️ RIZIK", "Pepelnica rizik"))

    if kultura == "Voćnjak":
        if w["hum"] > 80:
            alarmi.append(("⚠️ RIZIK", "Gljivične bolesti"))

    return alarmi


def split_alarmi(alarmi):

    hitno, rizik, info = [], [], []

    for tip, msg in alarmi:
        if "KRITIČNO" in tip:
            hitno.append(msg)
        elif "RIZIK" in tip:
            rizik.append(msg)
        else:
            info.append(msg)

    return hitno, rizik, info

# =========================
# AI KAMERA
# =========================

def ai_camera(kultura, simptom, vlaga, temp):

    bolesti = {
        "Paradajz": {
            "Žute fleke": ("Plamenjača", 0.90),
            "Bele tačke": ("Pepelnica", 0.75)
        },
        "Paprika": {
            "Sušenje lista": ("Bakterioza", 0.80)
        },
        "Krastavac": {
            "Žutilo lista": ("Virus / stres", 0.70)
        }
    }

    score = 0
    if vlaga > 85:
        score += 2
    if temp > 25:
        score += 1

    if kultura in bolesti and simptom in bolesti[kultura]:

        b, base = bolesti[kultura][simptom]
        conf = min(0.5 + base + score * 0.1, 0.97)

        return b, round(conf, 2)

    return None, 0

# =========================
# KARENCA
# =========================

def add_prskanje(p, d):
    st.session_state.prskanja.append({
        "p": p,
        "date": datetime.now(),
        "karenca": d
    })


def karenca():

    now = datetime.now()
    active = []

    for p in st.session_state.prskanja:

        end = p["date"] + timedelta(days=p["karenca"])
        diff = (end - now).days

        if diff > 0:
            active.append((p["p"], diff))

    return active

# =========================
# PLANOVI
# =========================

vocnjak = {
    "Januar": "Mirovanje",
    "Februar": "Rezidba",
    "Mart": "Start vegetacije + zaštita",
    "April": "Preventiva",
    "Maj": "Cvetanje + kalcijum",
    "Jun": "Rast ploda",
    "Jul": "Stres + voda",
    "Avgust": "Berba",
    "Septembar": "Glavna berba",
    "Oktobar": "Đubrenje",
    "Novembar": "Bakar",
    "Decembar": "Mirovanje"
}

povrce = {
    "Januar": "Plan",
    "Februar": "Rasad",
    "Mart": "Setva",
    "April": "Presađivanje",
    "Maj": "Rast",
    "Jun": "Zaštita",
    "Jul": "Zalivanje",
    "Avgust": "Berba",
    "Septembar": "Setva",
    "Oktobar": "Jesenje kulture",
    "Novembar": "Zatvaranje",
    "Decembar": "Plan"
}

# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3.2.1")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🚨 Danas",
    "🍎 Voćnjak",
    "🥦 Povrće",
    "📸 AI Kamera",
    "⏳ Karenca",
    "📊 Analiza"
])

# =========================
# DANAS
# =========================

with tab1:

    st.header("🚨 Pametni alarmi")

    w = weather()

    kultura = st.selectbox(
        "Kultura",
        ["Voćnjak", "Paradajz", "Paprika", "Krastavac"]
    )

    alarmi = pametni_alarmi(kultura, w)
    hitno, rizik, info = split_alarmi(alarmi)

    st.subheader("🔥 HITNO")
    for h in hitno:
        st.error(h)

    st.subheader("⚠️ RIZIK")
    for r in rizik:
        st.warning(r)

    st.subheader("ℹ️ INFO")
    for i in info:
        st.info(i)

    st.subheader("⏳ Karenca")
    for p, d in karenca():
        st.warning(f"{p} → {d} dana")

# =========================
# VOĆNJAK
# =========================

with tab2:

    mesec = st.selectbox("Mesec", list(vocnjak.keys()), key="v")

    st.subheader("🍎 Voćnjak")
    st.write(vocnjak[mesec])

# =========================
# POVRĆE
# =========================

with tab3:

    kultura_p = st.selectbox("Kultura", ["Paradajz", "Paprika", "Krastavac"])

    mesec = st.selectbox("Mesec", list(povrce.keys()), key="p")

    plan = {
        "Paradajz": "Plamenjača + kalcijum",
        "Paprika": "Stres + trips",
        "Krastavac": "Pepelnica"
    }

    st.info(plan[kultura_p])
    st.write(povrce[mesec])

# =========================
# AI CAMERA
# =========================

with tab4:

    st.header("📸 AI kamera")

    st.camera_input("Slikaj")

    k = st.selectbox("Kultura", ["Paradajz", "Paprika", "Krastavac"])
    s = st.selectbox("Simptom", ["Žute fleke", "Bele tačke", "Sušenje lista", "Žutilo lista"])

    if st.button("Analiza"):

        w = weather()

        b, c = ai_camera(k, s, w["hum"] if w else 70, w["temp"] if w else 20)

        if b:
            st.error(b)
            st.info(f"{c*100}%")

# =========================
# ANALIZA
# =========================

with tab6:

    st.header("📊 Analiza")

    st.info("Dodaj kasnije podatke iz GitHub-a")
