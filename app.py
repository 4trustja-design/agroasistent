import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroAsistent V3.3.1", layout="wide")

# =========================
# SECRETS
# =========================

WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

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
# KARENCA
# =========================

if "spray" not in st.session_state:
    st.session_state.spray = []


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
# PREPARATI (NOVO)
# =========================

preparati = {

    "Paradajz": [
        ("Bakarni preparat (organski ili hemijski)", 
         "Preventiva protiv plamenjače. Prskati ujutru ili uveče, ne po suncu.",
         "3–7 dana (zavisi od preparata)"),

        ("Kalcijum (folijarno đubrivo)",
         "Poboljšava čvrstinu ploda i sprečava trulež. Primena 1x nedeljno.",
         "0 dana"),

        ("Mankozeb (hemija)",
         "Snažna zaštita od gljivica, koristiti preventivno, ne čekati infekciju.",
         "7–14 dana")
    ],

    "Paprika": [
        ("Kalcijum + bor",
         "Jača cvet i sprečava opadanje plodova. Prskati u fazi cvetanja.",
         "0 dana"),

        ("Sumporni preparat",
         "Protiv pepelnice i grinja. Koristiti u suvom i toplom periodu.",
         "3–5 dana")
    ],

    "Krastavac": [
        ("Sumpor",
         "Protiv pepelnice. Ne koristiti na visokim temperaturama.",
         "3–5 dana"),

        ("Biološki fungicid",
         "Blaga zaštita, pogodan za organsku proizvodnju.",
         "0 dana")
    ]
}

# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3.3.1")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚨 Danas",
    "🍎 Voćnjak",
    "🥦 Povrće",
    "🌤️ Vreme",
    "⏳ Karenca"
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
# TAB 3 — POVRĆE + PREPARATI
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

    st.subheader("📌 Osnovni plan")
    st.info(povrce[mesec])

    st.subheader("🧪 Preporučeni preparati")

    if kultura in preparati:

        for naziv, opis, karenca_dana in preparati[kultura]:

            st.markdown(f"""
### {naziv}

{opis}

⏳ Karenca: **{karenca_dana}**
""")

    else:
        st.info("Nema definisanih preparata za ovu kulturu.")

# =========================
# TAB 4
# =========================

with tab4:

    st.header("🌤️ Vreme")

    w = weather()

    if not w:
        st.error("Nema podataka")
    else:
        st.metric("Temperatura", f"{w['temp']} °C")
        st.metric("Vlažnost", f"{w['hum']} %")
        st.metric("Vetар", f"{w['wind']} km/h")

# =========================
# TAB 5
# =========================

with tab5:

    st.header("⏳ Karenca")

    data = karenca()

    if not data:
        st.success("Nema aktivne karence")

    for n, d in data:
        st.warning(f"{n} → {d} dana")
