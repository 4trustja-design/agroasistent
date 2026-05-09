import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroAsistent V3", layout="wide")

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
        st.warning("GitHub fallback aktivan")


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

    out = []

    out.append(("Prskanje", "NE" if (r or h > 85 or w > 15) else "DA"))
    out.append(("Zalivanje", "NE" if r else "PO POTREBI"))
    out.append(("Rizik bolesti", "VISOK" if h > 85 else "SREDNJI"))

    return out


# =========================
# AI KAMERA (OFFLINE SMART LOGIC)
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

        bolest, base = bolesti[kultura][simptom]

        confidence = min(0.5 + base + (score * 0.1), 0.97)

        return bolest, round(confidence, 2)

    return None, 0


# =========================
# KARANCA
# =========================

def add_prskanje(preparat, karenca_dani):

    st.session_state.prskanja.append({
        "p": preparat,
        "date": datetime.now(),
        "karenca": karenca_dani
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
# PODSETNICI
# =========================

def add_reminder(text, days):

    st.session_state.reminders.append({
        "text": text,
        "date": datetime.now() + timedelta(days=days)
    })


# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3 — Stabilni Sistem")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🍎 Voćnjak",
    "🥦 Povrće",
    "🌦️ Vreme",
    "📸 AI Kamera",
    "⏳ Karenca",
    "📊 Analiza"
])

# =========================
# VOĆNJAK
# =========================

with tab1:

    st.header("🍎 Mešoviti voćnjak")

    mesec = st.selectbox(
        "Mesec",
        ["Maj", "Jun", "Jul", "Avgust"],
        key="vocnjak_mesec"
    )

    plan = {
        "Maj": "Start vegetacije + zaštita (Captan + Bor)",
        "Jun": "Rast ploda (Coragen + Kalcijum)",
        "Jul": "Stres + navodnjavanje",
        "Avgust": "Berba + završna zaštita (Teldor)"
    }

    st.info(plan[mesec])

# =========================
# POVRĆE
# =========================

with tab2:

    st.header("🥦 Povrće")

    kultura = st.selectbox(
        "Kultura",
        ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk"],
        key="povrce_kultura"
    )

    mesec = st.selectbox(
        "Mesec",
        ["Maj", "Jun", "Jul", "Avgust"],
        key="povrce_mesec"
    )

    plan = {
        "Paradajz": "Kalcijum + zaštita lista",
        "Paprika": "Prihrana + trips kontrola",
        "Krastavac": "Pepelnica preventiva",
        "Krompir": "Zlatica + fungicid",
        "Luk": "Bakarna zaštita"
    }

    st.info(plan.get(kultura, "Prati stanje"))

    rad = st.multiselect(
        "Radovi",
        ["Sadnja", "Zalivanje", "Prskanje", "Đubrenje"],
        key="povrce_rad"
    )

    if st.button("Sačuvaj rad"):

        if rad:
            save_github(kultura, ", ".join(rad))
            st.success("Sačuvano")

# =========================
# VREME
# =========================

with tab3:

    w = weather()

    if w:

        st.metric("Temperatura", w["temp"])
        st.metric("Vlaga", w["hum"])

        for n, o in agro_odluke(w["temp"], w["hum"], w["wind"], w["rain"]):
            st.info(f"{n}: {o}")

        if w["temp"] > 30:
            add_reminder("Zalivanje rano ujutru", 0)

# =========================
# AI KAMERA
# =========================

with tab4:

    st.header("📸 AI Kamera (Offline)")

    img = st.camera_input("Slikaj biljku")

    kultura = st.selectbox("Kultura", ["Paradajz", "Paprika", "Krastavac"], key="ai_kultura")
    simptom = st.selectbox("Simptom", ["Žute fleke", "Bele tačke", "Sušenje lista", "Žutilo lista"], key="ai_simptom")

    if st.button("Analiza"):

        w = weather()

        bolest, conf = ai_camera(
            kultura,
            simptom,
            w["hum"] if w else 70,
            w["temp"] if w else 20
        )

        if bolest:

            st.error(f"Bolest: {bolest}")
            st.info(f"Pouzdanost: {conf * 100}%")

            tretmani = {
                "Plamenjača": ("Ridomil", 14),
                "Pepelnica": ("Topas", 7),
                "Bakterioza": ("Champion", 7),
                "Virus / stres": ("Biostimulator", 0)
            }

            if bolest in tretmani:

                p, d = tretmani[bolest]

                st.warning(f"{p} → karenca {d} dana")

                if st.button("Primeni tretman"):
                    add_prskanje(p, d)

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

    st.header("📊 Analiza prinosa")

    try:

        url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO}/main/{FILE}"
        df = pd.read_csv(url)

        st.bar_chart(df["Kultura"].value_counts())

    except:
        st.info("Nema podataka još")
