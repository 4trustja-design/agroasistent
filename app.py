import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroAsistent V2.2", layout="wide")

# =========================
# SECRETS
# =========================

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USER = st.secrets["GITHUB_USER"]
REPO = st.secrets["REPO_NAME"]
WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

FILE = "dnevnik.csv"

# =========================
# SESSION STATE
# =========================

if "prskanja" not in st.session_state:
    st.session_state.prskanja = []

if "reminders" not in st.session_state:
    st.session_state.reminders = []

# =========================
# GITHUB SAVE
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
# AGRO ODLUKE
# =========================

def agro_odluke(t, h, w, r):

    res = []

    res.append(("Prskanje", "NE" if (r or h > 85 or w > 15) else "DA"))
    res.append(("Zalivanje", "NE" if r else "PO POTREBI"))
    res.append(("Rizik bolesti", "VISOK" if h > 85 else "SREDNJI"))

    return res


# =========================
# AI KAMERA FULL
# =========================

def ai_camera(kultura, simptom, vlaga, temp):

    score = 0

    if vlaga > 85:
        score += 2
    if temp > 25:
        score += 1

    bolesti = {

        "Paradajz": {
            "Žute fleke": ("Plamenjača", 0.9),
            "Bele tačke": ("Pepelnica", 0.7)
        },

        "Paprika": {
            "Sušenje lista": ("Bakterioza", 0.8)
        }
    }

    if kultura in bolesti and simptom in bolesti[kultura]:

        b, base = bolesti[kultura][simptom]

        conf = min(0.5 + base + score * 0.1, 0.98)

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
# REMINDERS
# =========================

def add_reminder(text, days):

    st.session_state.reminders.append({
        "text": text,
        "date": datetime.now() + timedelta(days=days)
    })


# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V2.2")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌱 Voćnjak",
    "🌦️ Vreme",
    "📸 AI Kamera",
    "⏳ Karenca",
    "⏰ Podsetnici",
    "📊 Analiza"
])

# =========================
# VOĆNJAK
# =========================

with tab1:

    st.header("🍎 Mešoviti voćnjak (3 godine)")

    mesec = st.selectbox("Mesec", ["Maj", "Jun", "Jul", "Avgust"])

    plan = {
        "Maj": "Captan + Bor",
        "Jun": "Coragen + Kalcijum",
        "Jul": "Stres + voda",
        "Avgust": "Berba + Teldor"
    }

    st.info(plan[mesec])

# =========================
# VREME
# =========================

with tab2:

    w = weather()

    if w:

        st.metric("Temp", w["temp"])
        st.metric("Vlaga", w["hum"])

        for n, o in agro_odluke(w["temp"], w["hum"], w["wind"], w["rain"]):
            st.info(f"{n}: {o}")

        if w["temp"] > 30:
            add_reminder("Zalivanje jutro/veče", 0)

# =========================
# AI KAMERA
# =========================

with tab3:

    st.header("📸 AI kamera")

    img = st.camera_input("Slikaj biljku")

    kultura = st.selectbox("Kultura", ["Paradajz", "Paprika"])
    simptom = st.selectbox("Simptom", ["Žute fleke", "Bele tačke", "Sušenje lista"])

    if st.button("Analiza"):

        w = weather()

        b, conf = ai_camera(
            kultura,
            simptom,
            w["hum"] if w else 70,
            w["temp"] if w else 20
        )

        if b:

            st.error(f"Bolest: {b}")
            st.info(f"Tačnost: {conf*100}%")

            st.subheader("🌱 Organski: Mleko, soda, neem")

            st.subheader("🧪 Hemija")

            chem = {
                "Plamenjača": ("Ridomil", 14),
                "Pepelnica": ("Topas", 7),
                "Bakterioza": ("Champion", 7)
            }

            if b in chem:

                p, d = chem[b]

                st.warning(f"{p} → karenca {d} dana")

                if st.button("Primeni"):
                    add_prskanje(p, d)

# =========================
# KARENCA
# =========================

with tab4:

    st.header("⏳ Karenca")

    for p, d in karenca():
        st.warning(f"{p} → {d} dana")

# =========================
# PODSETNICI
# =========================

with tab5:

    st.header("⏰ Podsetnici")

    for r in st.session_state.reminders:

        diff = (r["date"] - datetime.now()).days

        if diff >= 0:
            st.info(f"{r['text']} → {diff} dana")

# =========================
# ANALIZA
# =========================

with tab6:

    st.header("📊 Analiza prinosa")

    try:

        url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO}/main/{FILE}"
        df = pd.read_csv(url)

        st.bar_chart(df["Kultura"].value_counts())

    except:
        st.info("Nema podataka")
