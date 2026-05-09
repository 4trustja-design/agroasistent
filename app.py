import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroAsistent V3 FIX", layout="wide")

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
# AI LOGIKA
# =========================

def agro_odluke(t, h, w, r):

    return [
        ("Prskanje", "NE" if (r or h > 85 or w > 15) else "DA"),
        ("Zalivanje", "NE" if r else "PO POTREBI"),
        ("Rizik bolesti", "VISOK" if h > 85 else "SREDNJI")
    ]


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
# VOĆNJAK (12 MESECI FIX)
# =========================

vocnjak_plan = {
    "Januar": "Mirovanje. Planiranje i rezidba starih grana.",
    "Februar": "Završna rezidba i zaštita od prezimljujućih štetočina.",
    "Mart": "🌱 Start vegetacije + Captan + Bor (jačanje pupoljaka). Karenca 14 dana.",
    "April": "Bakarna zaštita + preventivna kontrola gljivica. Karenca 7–14 dana.",
    "Maj": "Cveta i zametanje ploda. Captan + Bor + Kalcijum. Karenca 7–14 dana.",
    "Jun": "Rast ploda. Coragen + Kalcijum. Karenca 3–14 dana.",
    "Jul": "Stres + navodnjavanje + biostimulatori. Karenca 0–7 dana.",
    "Avgust": "Rana berba + Teldor protiv truleži. Karenca 3–7 dana.",
    "Septembar": "Glavna berba + higijena voćnjaka.",
    "Oktobar": "Jesenje đubrenje NPK 6:12:24.",
    "Novembar": "Bakarna zaštita kore. Karenca 14 dana.",
    "Decembar": "Mirovanje + priprema sledeće sezone."
}

# =========================
# POVRĆE (12 MESECI FIX)
# =========================

povrce_plan = {
    "Januar": "Plastenici / plan setve.",
    "Februar": "Priprema rasada.",
    "Mart": "Setva ranih kultura.",
    "April": "Presađivanje i zaštita mladih biljaka.",
    "Maj": "Kalcijum + zaštita lista.",
    "Jun": "Intenzivan rast + kontrola bolesti.",
    "Jul": "Zalivanje + stres zaštita.",
    "Avgust": "Berba ranih kultura.",
    "Septembar": "Druga setva / priprema jeseni.",
    "Oktobar": "Jesenje kulture (kupus, salata).",
    "Novembar": "Zatvaranje sezone.",
    "Decembar": "Planiranje i održavanje plastenika."
}

# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3 — FULL FIX")

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

    mesec = st.selectbox(
        "Mesec",
        list(vocnjak_plan.keys()),
        key="vocnjak_mesec"
    )

    st.subheader("🍎 Plan voćnjaka")
    st.write(vocnjak_plan[mesec])

# =========================
# POVRĆE
# =========================

with tab2:

    kultura = st.selectbox(
        "Kultura",
        ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk"],
        key="povrce_kultura"
    )

    mesec = st.selectbox(
        "Mesec",
        list(povrce_plan.keys()),
        key="povrce_mesec"
    )

    st.subheader("🥦 Plan povrća")
    st.write(povrce_plan[mesec])

    rad = st.multiselect(
        "Radovi",
        ["Sadnja", "Zalivanje", "Prskanje", "Đubrenje"],
        key="povrce_rad"
    )

    if st.button("Sačuvaj rad"):

        if rad:
            save_github(kultura, ", ".join(rad))

# =========================
# VREME
# =========================

with tab3:

    w = weather()

    if w:

        st.metric("Temp", w["temp"])
        st.metric("Vlaga", w["hum"])

# =========================
# AI KAMERA
# =========================

with tab4:

    st.header("📸 AI kamera")

    st.camera_input("Slikaj biljku")

    kultura = st.selectbox("Kultura", ["Paradajz", "Paprika"], key="ai_kultura")
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
