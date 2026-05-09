import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import streamlit.components.v1 as components

# =========================================================
# PODESAVANJA
# =========================================================

st.set_page_config(
    page_title="AgroAsistent V2",
    layout="wide",
    page_icon="🌾"
)

# =========================================================
# SECRETS
# =========================================================

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"].strip()
    OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"].strip()

    USER = "4trustja-design"
    REPO = "NAZIV_TVOG_REPOZITORIJUMA"

except Exception:
    st.error("⚠️ Popuni Streamlit Secrets!")
    st.stop()

FILE_PATH = "dnevnik.csv"

# =========================================================
# GITHUB UPIS
# =========================================================

def snimi_na_github(kultura, radnja):

    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)

        sha = None
        stari_sadrzaj = ""

        if res.status_code == 200:
            podaci = res.json()

            sha = podaci.get("sha")

            stari_sadrzaj = base64.b64decode(
                podaci["content"]
            ).decode("utf-8")

        vreme = datetime.now().strftime("%d.%m.%Y %H:%M")

        novi_red = (
            f"{vreme},{kultura},{radnja.replace(',', ' ')}\n"
        )

        if not stari_sadrzaj:

            finalni_sadrzaj = (
                "Datum,Kultura,Rad\n"
                + novi_red
            )

        else:

            if not stari_sadrzaj.endswith("\n"):
                stari_sadrzaj += "\n"

            finalni_sadrzaj = stari_sadrzaj + novi_red

        payload = {
            "message": f"Unos: {kultura}",
            "content": base64.b64encode(
                finalni_sadrzaj.encode("utf-8")
            ).decode("utf-8"),
        }

        if sha:
            payload["sha"] = sha

        r = requests.put(
            url,
            headers=headers,
            json=payload,
            timeout=10
        )

        if r.status_code in [200, 201]:

            st.success("✅ Sačuvano!")
            st.balloons()
            st.rerun()

        else:
            st.error(f"Greška: {r.status_code}")

    except Exception as e:
        st.error(f"Greška: {e}")

# =========================================================
# OPENWEATHER
# =========================================================

def get_weather(city="Krusevac"):

    try:

        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={city},RS"
            f"&appid={OPENWEATHER_API_KEY}"
            f"&units=metric"
            f"&lang=sr"
        )

        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return None

        data = r.json()

        return {
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind": round(data["wind"]["speed"] * 3.6, 1),
            "description": data["weather"][0]["description"],
            "rain": "rain" in data
        }

    except:
        return None

# =========================================================
# BOLESTI
# =========================================================

def analiza_bolesti(kultura, simptom):

    baza = {

        "Paradajz": {

            "Žute fleke": {
                "bolest": "Početak plamenjače",

                "organsko": [
                    "Mleko 1:10",
                    "Soda bikarbona",
                    "Bakar dozvoljen u organskoj proizvodnji"
                ],

                "hemija": [
                    ("Ridomil Gold", "14 dana"),
                    ("Revus", "3 dana")
                ]
            },

            "Bele tačke": {
                "bolest": "Pepelnica",

                "organsko": [
                    "Soda bikarbona",
                    "Neem ulje"
                ],

                "hemija": [
                    ("Topas", "7 dana")
                ]
            }
        },

        "Paprika": {

            "Sušenje lista": {
                "bolest": "Bakterioza ili stres",

                "organsko": [
                    "Kopriva",
                    "Bakar"
                ],

                "hemija": [
                    ("Champion", "7 dana")
                ]
            }
        }
    }

    return baza.get(kultura, {}).get(simptom, None)

# =========================================================
# SAVETI
# =========================================================

def savet_po_vremenu(temp, vlaga, vetar, kisa):

    saveti = []

    if kisa:
        saveti.append(
            "🌧️ Najavljena kiša - odloži prskanje."
        )

    if vlaga > 80:
        saveti.append(
            "🛡️ Visoka vlaga - povećan rizik od gljivica."
        )

    if vetar > 15:
        saveti.append(
            "💨 Jak vetar - ne prskaj."
        )

    if temp > 28:
        saveti.append(
            "☀️ Zalivaj rano ujutru ili uveče."
        )

    return saveti

# =========================================================
# HEADER
# =========================================================

st.title("🌾 AgroAsistent V2")

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Podešavanja")

    datum_sadnje = st.date_input(
        "Datum sadnje",
        datetime.now()
    )

    st.markdown("---")

    st.info("Podaci se čuvaju na GitHub-u.")

# =========================================================
# TABOVI
# =========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🥦 Povrće",
    "🛰️ Vreme",
    "📸 Bolesti",
    "💰 Troškovnik",
    "📓 Dnevnik"
])

# =========================================================
# TAB 1 - POVRĆE
# =========================================================

with tab1:

    st.header("🥦 Povrtarstvo")

    kultura = st.selectbox(
        "Kultura",
        [
            "Paradajz",
            "Paprika",
            "Krastavac",
            "Krompir",
            "Luk"
        ]
    )

    radovi = st.multiselect(
        "Šta je urađeno?",
        [
            "Sadnja",
            "Zalivanje",
            "Prskanje",
            "Berba",
            "Đubrenje"
        ]
    )

    if st.button("Sačuvaj rad"):

        if radovi:
            snimi_na_github(
                kultura,
                ", ".join(radovi)
            )

# =========================================================
# TAB 2 - VREME
# =========================================================

with tab2:

    st.header("🛰️ Vremenski uslovi")

    weather = get_weather()

    if weather:

        temp = weather["temp"]
        vlaga = weather["humidity"]
        vetar = weather["wind"]
        kisa = weather["rain"]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🌡️ Temperatura",
            f"{temp}°C"
        )

        col2.metric(
            "💧 Vlažnost",
            f"{vlaga}%"
        )

        col3.metric(
            "💨 Vetar",
            f"{vetar} km/h"
        )

        st.info(
            f"☁️ {weather['description']}"
        )

        st.subheader("📢 Saveti")

        saveti = savet_po_vremenu(
            temp,
            vlaga,
            vetar,
            kisa
        )

        for s in saveti:
            st.warning(s)

    else:
        st.error("Ne mogu da učitam vreme.")

# =========================================================
# TAB 3 - BOLESTI
# =========================================================

with tab3:

    st.header("📸 Analiza bolesti")

    slika = st.camera_input(
        "Slikaj biljku"
    )

    kultura_b = st.selectbox(
        "Kultura",
        [
            "Paradajz",
            "Paprika"
        ],
        key="bolest_kultura"
    )

    simptom = st.selectbox(
        "Simptom",
        [
            "Žute fleke",
            "Bele tačke",
            "Sušenje lista"
        ]
    )

    if st.button("Analiziraj"):

        rezultat = analiza_bolesti(
            kultura_b,
            simptom
        )

        if rezultat:

            st.error(
                f"Moguća bolest: {rezultat['bolest']}"
            )

            st.subheader("🌱 Organska zaštita")

            for o in rezultat["organsko"]:
                st.success(o)

            st.subheader("🧪 Hemijska zaštita")

            for h, k in rezultat["hemija"]:

                st.warning(
                    f"{h} | Karenca: {k}"
                )

        else:
            st.info(
                "Nema preporuke za izabrane simptome."
            )

# =========================================================
# TAB 4 - TROŠKOVI
# =========================================================

with tab4:

    st.header("💰 Troškovnik")

    stavka = st.text_input(
        "Naziv troška"
    )

    iznos = st.number_input(
        "Iznos (RSD)",
        min_value=0.0
    )

    if st.button("Sačuvaj trošak"):

        if stavka:

            snimi_na_github(
                "TROŠAK",
                f"{stavka}: {iznos} RSD"
            )

# =========================================================
# TAB 5 - DNEVNIK
# =========================================================

with tab5:

    st.header("📓 Digitalni dnevnik")

    try:

        url_raw = (
            f"https://raw.githubusercontent.com/"
            f"{USER}/{REPO}/main/{FILE_PATH}"
        )

        df = pd.read_csv(
            f"{url_raw}?v={datetime.now().timestamp()}"
        )

        filter_kultura = st.selectbox(
            "Filter kulture",
            ["Sve"] + list(df["Kultura"].unique())
        )

        if filter_kultura != "Sve":

            df = df[
                df["Kultura"] == filter_kultura
            ]

        st.dataframe(
            df.tail(30),
            use_container_width=True
        )

        st.metric(
            "Ukupno unosa",
            len(df)
        )

        csv = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Preuzmi CSV",
            csv,
            "dnevnik.csv",
            "text/csv"
        )

    except:
        st.info(
            "Dnevnik će se pojaviti nakon prvog upisa."
        )

# =========================================================
# FOOTER
# =========================================================

st.write("---")

st.caption(
    "AgroAsistent V2 | Lični digitalni agronom 🌾"
)
