import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroAsistent V3.1", layout="wide")

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

if "reminders" not in st.session_state:
    st.session_state.reminders = []

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
# SMART AGRONOMIST CORE
# =========================

def danasnji_savet(w):

    saveti = []

    if not w:
        return ["⚠️ Nema podataka o vremenu"]

    if w["rain"]:
        saveti.append("🌧️ Kiša → NE PRSKATI, samo pregled biljaka")

    if w["hum"] > 85:
        saveti.append("🌫️ Visoka vlaga → rizik gljivica, proveri zaštitu")

    if w["temp"] > 30:
        saveti.append("☀️ Vrućina → zalivanje rano ujutru ili uveče")

    if 15 <= w["temp"] <= 28:
        saveti.append("🌿 Idealni uslovi → može zaštita i prihrana")

    if w["wind"] > 15:
        saveti.append("💨 Vetar → NE PRSKATI zbog zanošenja")

    return saveti


# =========================
# AI KAMERA (OFFLINE)
# =========================

def ai_camera(kultura, simptom, vlaga, temp):

    score = 0

    if vlaga > 85:
        score += 2
    if temp > 25:
        score += 1

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

    if kultura in bolesti and simptom in bolesti[kultura]:

        b, base = bolesti[kultura][simptom]
        conf = min(0.5 + base + score * 0.1, 0.97)

        return b, round(conf, 2)

    return None, 0


# =========================
# KARANCA
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
# VOĆNJAK
# =========================

vocnjak_plan = {
    "Januar": "Mirovanje i planiranje",
    "Februar": "Rezidba",
    "Mart": "Start vegetacije + Captan + Bor",
    "April": "Preventiva gljivica",
    "Maj": "Cveta + Kalcijum + zaštita",
    "Jun": "Rast ploda + Coragen",
    "Jul": "Stres + voda + biostimulator",
    "Avgust": "Berba + Teldor",
    "Septembar": "Glavna berba",
    "Oktobar": "Jesenje đubrenje",
    "Novembar": "Bakarna zaštita",
    "Decembar": "Mirovanje"
}


# =========================
# POVRĆE
# =========================

povrce_plan = {
    "Januar": "Planiranje plastenika",
    "Februar": "Rasad",
    "Mart": "Setva",
    "April": "Presađivanje",
    "Maj": "Rast + zaštita",
    "Jun": "Intenzivan rast",
    "Jul": "Zalivanje + stres",
    "Avgust": "Berba",
    "Septembar": "Nova setva",
    "Oktobar": "Jesenje kulture",
    "Novembar": "Zatvaranje sezone",
    "Decembar": "Planiranje"
}


# =========================
# GITHUB
# =========================

def save_github(kultura, rad):

    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    try:
        r = requests.get(url, headers=headers)

        sha = None
        content = ""

        if r.status_code == 200:
            data = r.json()
            sha = data["sha"]
            content = base64.b64decode(data["content"]).decode()

        line = f"{datetime.now()},{kultura},{rad}\n"
        full = content + line

        payload = {
            "message": "update",
            "content": base64.b64encode(full.encode()).decode()
        }

        if sha:
            payload["sha"] = sha

        requests.put(url, headers=headers, json=payload)

    except:
        st.warning("GitHub fallback")


# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3.1 — Pametni Agronom")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧠 Danas",
    "🍎 Voćnjak",
    "🥦 Povrće",
    "📸 AI Kamera",
    "⏳ Karenca",
    "📊 Analiza"
])

# =========================
# 🧠 DANAS (KLJUČNA NOVA FUNKCIJA)
# =========================

with tab1:

    st.header("🧠 Šta danas da radiš")

    w = weather()

    saveti = danasnji_savet(w)

    for s in saveti:
        st.info(s)

# =========================
# VOĆNJAK
# =========================

with tab2:

    mesec = st.selectbox("Mesec", list(vocnjak_plan.keys()), key="vocnjak_mesec")

    st.subheader("🍎 Voćnjak")
    st.write(vocnjak_plan[mesec])

# =========================
# POVRĆE
# =========================

with tab3:

    mesec = st.selectbox("Mesec", list(povrce_plan.keys()), key="povrce_mesec")

    st.subheader("🥦 Povrće")
    st.write(povrce_plan[mesec])

# =========================
# AI CAMERA
# =========================

with tab4:

    st.header("📸 AI kamera")

    st.camera_input("Slikaj biljku")

    kultura = st.selectbox("Kultura", ["Paradajz", "Paprika", "Krastavac"], key="ai_kultura")
    simptom = st.selectbox("Simptom", ["Žute fleke", "Bele tačke", "Sušenje lista", "Žutilo lista"], key="ai_simptom")

    if st.button("Analiza"):

        w = weather()

        b, conf = ai_camera(
            kultura,
            simptom,
            w["hum"] if w else 70,
            w["temp"] if w else 20
        )

        if b:
            st.error(b)
            st.info(f"Pouzdanost: {conf*100}%")

# =========================
# KARENCA
# =========================

with tab5:

    st.header("⏳ Karenca")

    for p, d in karenca():
        st.warning(f"{p} → {d} dana")

# =========================
# ANALIZA
# =========================

with tab6:

    st.header("📊 Analiza")

    try:

        url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO}/main/{FILE}"
        df = pd.read_csv(url)

        st.bar_chart(df["Kultura"].value_counts())

    except:
        st.info("Nema podataka")
