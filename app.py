import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AgroAsistent V3.3.4", layout="wide")

WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

# =========================
# LOG
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
def alarms(kultura, w):

    out = []

    if not w:
        return [("INFO", "Nema podataka")]

    if w["rain"]:
        out.append(("KRITIČNO", "Kiša → bez prskanja"))

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
# VOĆNJAK (OSTAJE ISTO)
# =========================

vocnjak = {
    "Januar": "Mirovanje",
    "Februar": "Rezidba",
    "Mart": "Start vegetacije + zaštita",
    "April": "Preventiva bolesti",
    "Maj": "Cvetanje",
    "Jun": "Rast ploda",
    "Jul": "Zalivanje",
    "Avgust": "Berba",
    "Septembar": "Kasna berba",
    "Oktobar": "Jesenje đubrenje",
    "Novembar": "Bakar",
    "Decembar": "Mirovanje"
}

# =========================
# POVRĆE PLAN
# =========================

povrce = {
    "Januar": "Planiranje",
    "Februar": "Rasad",
    "Mart": "Setva",
    "April": "Rasađivanje",
    "Maj": "Rast intenzivan",
    "Jun": "Formiranje ploda",
    "Jul": "Zaštita + stres",
    "Avgust": "Berba"
}

# =========================
# PREPARATI PO MESECU + KULTURI (FIX)
# =========================

preparati = {

    "Paradajz": {

        "Maj": [
            ("Bakarni preparat", "Start zaštita od plamenjače.", "7 dana"),
            ("Kalcijum", "Jača cvet i plod.", "0 dana")
        ],

        "Jun": [
            ("Mankozeb", "Intenzivna zaštita lista.", "10 dana"),
            ("Kalcijum", "Sprečava trulež vrha.", "0 dana")
        ],

        "Jul": [
            ("Biostimulator", "Ublažava stres i sušu.", "0 dana"),
            ("Sistemični fungicid", "Jača zaštita ploda.", "14 dana")
        ],

        "Avgust": [
            ("Kratka karenca fungicid", "Finalna zaštita pred berbu.", "7 dana")
        ]
    },

    "Paprika": {

        "Maj": [
            ("Kalcijum + bor", "Cvetanje i zametanje ploda.", "0 dana")
        ],

        "Jun": [
            ("Sumpor", "Pepelnica kontrola.", "5 dana")
        ],

        "Jul": [
            ("Biostimulator", "Stres zaštita.", "0 dana")
        ],

        "Avgust": [
            ("Blagi fungicid", "Održavanje zdravlja biljke.", "3–5 dana")
        ]
    },

    "Krastavac": {

        "Maj": [
            ("Sumpor", "Preventiva pepelnice.", "5 dana")
        ],

        "Jun": [
            ("Biološki fungicid", "Organska zaštita.", "0 dana")
        ],

        "Jul": [
            ("Sistemična zaštita", "Jača infekcioni pritisak.", "7–10 dana")
        ],

        "Avgust": [
            ("Kratka karenca preparat", "Završna zaštita.", "3–5 dana")
        ]
    }
}

# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3.3.4")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🚨 Danas",
    "🍎 Voćnjak",
    "🥦 Povrće",
    "🌤️ Vreme",
    "📊 Karenca",
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

    a = alarms(kultura, w)
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

    mesec = st.selectbox("Mesec", list(vocnjak.keys()))

    st.info(vocnjak[mesec])

# =========================
# TAB 3
# =========================

with tab3:

    kultura = st.selectbox("Kultura", ["Paradajz", "Paprika", "Krastavac"])
    mesec = st.selectbox("Mesec", ["Maj", "Jun", "Jul", "Avgust"])

    st.info(povrce[mesec])

    st.subheader("🧪 Preparati po fazi")

    if kultura in preparati and mesec in preparati[kultura]:

        for naziv, opis, karenca in preparati[kultura][mesec]:

            col1, col2 = st.columns([0.1, 0.9])

            with col1:

                if st.checkbox("", key=f"{kultura}_{mesec}_{naziv}"):

                    log_action(kultura, naziv)
                    st.success("Zabeleženo")

            with col2:

                st.markdown(f"""
### {naziv}

{opis}

⏳ Karenca: **{karenca}**
""")

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

    st.header("📊 Karenca")

    st.info("Evidencija preko čekiranih preparata")

# =========================
# TAB 6
# =========================

with tab6:

    st.header("📓 Dnevnik")

    if not st.session_state.log:
        st.info("Nema unosa")
    else:
        st.dataframe(pd.DataFrame(st.session_state.log))
