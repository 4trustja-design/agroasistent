import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import urllib.parse
from bs4 import BeautifulSoup

st.set_page_config(page_title="AgroAsistent V3.4", layout="wide")

# =========================
# WEATHER KEY
# =========================
WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

# =========================
# SESSION LOG
# =========================
if "log" not in st.session_state:
    st.session_state.log = []

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
        out.append(("KRITIČNO", "Kiša → ne prskati"))

    if w["hum"] > 85:
        out.append(("RIZIK", "Visoka vlaga → gljivice"))

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
# VOĆNJAK
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
# POVRĆE
# =========================

povrce = {
    "Januar": "Planiranje",
    "Februar": "Rasad",
    "Mart": "Setva",
    "April": "Rasađivanje",
    "Maj": "Rast",
    "Jun": "Formiranje ploda",
    "Jul": "Zaštita",
    "Avgust": "Berba"
}

# =========================
# PREPARATI
# =========================

preparati = {

    "Paradajz": {
        "Maj": [("Bakarni preparat", "Start zaštita", "7 dana"),
                ("Kalcijum", "Jača plod", "0 dana")],
        "Jun": [("Mankozeb", "Zaštita lista", "10 dana"),
                ("Kalcijum", "Protiv truleži", "0 dana")],
        "Jul": [("Biostimulator", "Stres zaštita", "0 dana")],
        "Avgust": [("Fungicid završni", "Pred berbu", "7 dana")]
    },

    "Paprika": {
        "Maj": [("Kalcijum + bor", "Cvetanje", "0 dana")],
        "Jun": [("Sumpor", "Pepelnica", "5 dana")],
        "Jul": [("Biostimulator", "Stres", "0 dana")],
        "Avgust": [("Blagi fungicid", "Održavanje", "3–5 dana")]
    },

    "Krastavac": {
        "Maj": [("Sumpor", "Pepelnica", "5 dana")],
        "Jun": [("Biološki fungicid", "Organski", "0 dana")],
        "Jul": [("Sistemična zaštita", "Infekcije", "7–10 dana")],
        "Avgust": [("Završna zaštita", "Pred berbu", "3–5 dana")]
    }
}

# =========================
# AI PRETRAGA PREPARATA
# =========================
def ai_pretraga_preparata(termin):

    try:
        query = urllib.parse.quote(termin + " biostimulator Srbija poljoprivreda")

        url = f"https://duckduckgo.com/html/?q={query}"
        r = requests.get(url, timeout=5)

        soup = BeautifulSoup(r.text, "html.parser")

        results = []

        for a in soup.find_all("a"):

            text = a.get_text()

            if any(x in text.lower() for x in ["megafol", "algex", "atonik", "fertil", "biostim"]):
                results.append(text)

            if len(results) >= 5:
                break

        if results:
            return results

        return [
            "Megafol (Valagro)",
            "Algex",
            "Atonik",
            "Sprintene",
            "Fertileader"
        ]

    except:

        return [
            "Megafol (Valagro)",
            "Algex",
            "Atonik",
            "Sprintene"
        ]

# =========================
# UI
# =========================

st.title("🌾 AgroAsistent V3.4")

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
    mesec = st.selectbox("Mesec", list(povrce.keys()))

    st.info(povrce[mesec])

    st.subheader("🧪 Preparati")

    if kultura in preparati and mesec in preparati[kultura]:

        for naziv, opis, karenca in preparati[kultura][mesec]:

            col1, col2 = st.columns([0.1, 0.9])

            with col1:

                if st.checkbox("", key=f"{kultura}_{mesec}_{naziv}"):

                    log_action(kultura, naziv)
                    st.success("Zabeleženo")

                    # 🤖 AI DODATAK
                    if naziv in ["Biostimulator", "Sistemična zaštita", "Kalcijum"]:

                        st.subheader("🤖 AI preporuka")

                        for p in ai_pretraga_preparata(naziv):
                            st.write("• " + p)

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
    st.info("Prati se kroz dnevnik")

# =========================
# TAB 6
# =========================

with tab6:

    st.header("📓 Dnevnik")

    if not st.session_state.log:
        st.info("Nema unosa")

    else:
        st.dataframe(pd.DataFrame(st.session_state.log))
