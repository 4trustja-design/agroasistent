import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroAsistent V3.2", layout="wide")

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
# PAMETNI ALARMI
# =========================

def pametni_alarmi(kultura, w):

    alarmi = []

    if not w:
        return [("⚠️ INFO", "Nema vremenskih podataka")]

    # GLOBALNO
    if w["rain"]:
        alarmi.append(("🚫 KRITIČNO", "Kiša → zabrana prskanja"))

    if w["hum"] > 85:
        alarmi.append(("⚠️ RIZIK", "Visoka vlaga → gljivične bolesti"))

    if w["wind"] > 15:
        alarmi.append(("🚫 KRITIČNO", "Jak vetar → ne prskati"))

    # KULTURA
    if kultura == "Paradajz":
        if w["hum"] > 80:
            alarmi.append(("⚠️ RIZIK", "Plamenjača moguća"))
        if w["temp"] > 30:
            alarmi.append(("ℹ️ INFO", "Kalcijum + zalivanje uveče"))

    if kultura == "Paprika":
        if w["temp"] > 32:
            alarmi.append(("⚠️ RIZIK", "Toplotni stres"))

    if kultura == "Krastavac":
        if w["hum"] > 80:
            alarmi.append(("⚠️ RIZIK", "Pepelnica rizik"))

    if kultura == "Voćnjak":
        if w["hum"] > 80:
            alarmi.append(("⚠️ RIZIK", "Gljivične bolesti u voćnjaku"))

    return alarmi


# =========================
# TOP AKCIJE
# =========================

def top_akcije(alarmi):

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
# VOĆNJAK + POVRĆE (12 MES)
# =========================

vocnjak = {
    "Januar": "Mirovanje i planiranje",
    "Februar": "Rezidba",
    "Mart": "Start vegetacije + zaštita",
    "April": "Preventiva",
    "Maj": "Cvetanje + kalcijum",
    "Jun": "Rast ploda",
    "Jul": "Stres + voda",
    "Avgust": "Berba",
    "Septembar": "Glavna berba",
    "Oktobar": "Jesenje đubrenje",
    "Novembar": "Bakarna zaštita",
    "Decembar": "Mirovanje"
}

povrce = {
    "Januar": "Plan plastenika",
    "Februar": "Rasad",
    "Mart": "Setva",
    "April": "Presađivanje",
    "Maj": "Rast",
    "Jun": "Zaštita",
    "Jul": "Zalivanje",
    "Avgust": "Berba",
    "Septembar": "Nova setva",
    "Oktobar": "Jesenske kulture",
    "Novembar": "Zatvaranje",
    "Decembar": "Plan"
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
        pass


# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3.2 — Pametni Alarmi")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🚨 Danas",
    "🍎 Voćnjak",
    "🥦 Povrće",
    "📸 AI Kamera",
    "⏳ Karenca",
    "📊 Analiza"
])

# =========================
# 🚨 PAMETNI ALARMI
# =========================

with tab1:

    st.header("🚨 Pametni alarmi")

    w = weather()

    kultura = st.selectbox(
        "Kultura",
        ["Voćnjak", "Paradajz", "Paprika", "Krastavac"],
        key="alarm_kultura"
    )

    alarmi = pametni_alarmi(kultura, w)
    hitno, rizik, info = top_akcije(alarmi)

    st.subheader("🔥 HITNO")

    if hitno:
        for h in hitno:
            st.error(h)
    else:
        st.success("Nema hitnih akcija")

    st.subheader("⚠️ RIZIK")

    for r in rizik:
        st.warning(r)

    st.subheader("ℹ️ INFO")

    for i in info:
        st.info(i)


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

    mesec = st.selectbox("Mesec", list(povrce.keys()), key="p")

    st.subheader("🥦 Povrće")
    st.write(povrce[mesec])


# =========================
# AI CAMERA
# =========================

with tab4:

    st.header("📸 AI kamera")

    st.camera_input("Slikaj biljku")

    kultura_ai = st.selectbox("Kultura", ["Paradajz", "Paprika", "Krastavac"], key="ai")
    simptom = st.selectbox("Simptom", ["Žute fleke", "Bele tačke", "Sušenje lista", "Žutilo lista"], key="ai2")

    if st.button("Analiza"):

        w = weather()

        b, conf = ai_camera(
            kultura_ai,
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
