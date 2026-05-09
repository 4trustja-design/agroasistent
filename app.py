import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroAsistent V3.3.2", layout="wide")

# =========================
# WEATHER KEY
# =========================
WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

# =========================
# SESSION LOG
# =========================
if "log" not in st.session_state:
    st.session_state.log = []

if "spray" not in st.session_state:
    st.session_state.spray = []

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
        out.append(("KRITIČNO", "Jak vetar"))

    if kultura == "Paradajz" and w["hum"] > 80:
        out.append(("RIZIK", "Plamenjača"))

    if kultura == "Krastavac" and w["hum"] > 80:
        out.append(("RIZIK", "Pepelnica"))

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
# LOG FUNKCIJA
# =========================
def log_action(kultura, preparat):

    st.session_state.log.append({
        "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "kultura": kultura,
        "radnja": preparat
    })

# =========================
# KARENCA
# =========================
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
# PREPARATI
# =========================

preparati = {

    "Paradajz": [
        ("Bakarni preparat", "Preventiva protiv plamenjače. Prskati uveče ili rano ujutru.", "3–7 dana"),
        ("Kalcijum", "Jača plod i sprečava trulež. 1x nedeljno.", "0 dana"),
        ("Mankozeb", "Jaka hemijska zaštita protiv gljivica.", "7–14 dana")
    ],

    "Paprika": [
        ("Kalcijum + bor", "Bolje cvetanje i manje opadanja ploda.", "0 dana"),
        ("Sumpor", "Protiv pepelnice, koristiti u suvom vremenu.", "3–5 dana")
    ],

    "Krastavac": [
        ("Sumpor", "Pepelnica zaštita, ne koristiti na +30°C.", "3–5 dana"),
        ("Biološki fungicid", "Organska zaštita, blaga primena.", "0 dana")
    ]
}

# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3.3.2")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🚨 Danas",
    "🍎 Voćnjak",
    "🥦 Povrće",
    "🌤️ Vreme",
    "⏳ Karenca",
    "📊 Dnevnik"
])

# =========================
# TAB 1
# =========================

with tab1:

    st.header("🚨 Pametni alarmi")

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
# TAB 2
# =========================

with tab2:

    mesec = st.selectbox("Mesec", list(vocnjak.keys()), key="v")

    st.subheader("🍎 Voćnjak")
    st.info(vocnjak[mesec])

# =========================
# TAB 3
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

    st.subheader("📌 Plan")
    st.info(povrce[mesec])

    st.subheader("🧪 Preparati + evidencija")

    if kultura in preparati:

        for naziv, opis, karenca in preparati[kultura]:

            col1, col2 = st.columns([0.1, 0.9])

            with col1:

                if st.checkbox("", key=f"{kultura}_{naziv}"):

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

    st.header("🌤️ Vreme")

    w = weather()

    if not w:
        st.error("Nema podataka")
    else:
        st.metric("Temp", f"{w['temp']} °C")
        st.metric("Vlaga", f"{w['hum']} %")
        st.metric("Vetar", f"{w['wind']} km/h")

# =========================
# TAB 5
# =========================

with tab5:

    st.header("⏳ Karenca")

    if not st.session_state.spray:
        st.success("Nema aktivne karence")

    for s in st.session_state.spray:
        st.warning(f"{s['name']} → aktivno")

# =========================
# TAB 6
# =========================

with tab6:

    st.header("📊 Dnevnik rada")

    if not st.session_state.log:
        st.info("Nema unosa")

    else:
        df = pd.DataFrame(st.session_state.log)
        st.dataframe(df, use_container_width=True)
