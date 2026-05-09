import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import streamlit.components.v1 as components

# =====================================================
# SETUP
# =====================================================

st.set_page_config(page_title="AgroAsistent V2", layout="wide", page_icon="🌾")

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GITHUB_USER = st.secrets["GITHUB_USER"]
    REPO = st.secrets["REPO_NAME"]
    OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except:
    st.error("❌ Nisi podesio Secrets u Streamlit-u")
    st.stop()

FILE_PATH = "dnevnik.csv"

# =====================================================
# GITHUB SAVE
# =====================================================

def local_backup(line):
    with open("backup.csv", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def save_to_github(kultura, rad):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{FILE_PATH}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        res = requests.get(url, headers=headers)

        sha = None
        content = ""

        if res.status_code == 200:
            data = res.json()
            sha = data["sha"]
            content = base64.b64decode(data["content"]).decode()

        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        line = f"{now},{kultura},{rad}\n"

        full = content + line if content else "Datum,Kultura,Rad\n" + line

        payload = {
            "message": "update log",
            "content": base64.b64encode(full.encode()).decode()
        }

        if sha:
            payload["sha"] = sha

        r = requests.put(url, headers=headers, json=payload)

        if r.status_code in [200, 201]:
            st.success("✔ Sačuvano na GitHub")
            st.rerun()
        else:
            local_backup(line)
            st.warning("⚠ GitHub fail → lokalni backup")

    except:
        local_backup(line)
        st.warning("⚠ Offline backup aktivan")


# =====================================================
# WEATHER
# =====================================================

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Krusevac,RS&appid={OPENWEATHER_API_KEY}&units=metric&lang=sr"
    r = requests.get(url)

    if r.status_code != 200:
        return None

    d = r.json()

    return {
        "temp": d["main"]["temp"],
        "humidity": d["main"]["humidity"],
        "wind": d["wind"]["speed"] * 3.6,
        "desc": d["weather"][0]["description"],
        "rain": "rain" in d
    }


# =====================================================
# AGRO LOGIKA
# =====================================================

def agro_odluka(temp, vlaga, vetar, kisa):

    res = []

    if kisa or vlaga > 85 or vetar > 15:
        res.append(("❌ PRSKANJE", "NE"))
    else:
        res.append(("✅ PRSKANJE", "DA"))

    if kisa:
        res.append(("❌ ZALIVANJE", "NE"))
    elif temp > 30:
        res.append(("💧 ZALIVANJE", "DA (ujutru/uveče)"))
    else:
        res.append(("💧 ZALIVANJE", "PO POTREBI"))

    if vlaga > 85 and temp > 20:
        res.append(("🦠 RIZIK", "VISOK"))
    elif vlaga > 70:
        res.append(("🟡 RIZIK", "SREDNJI"))
    else:
        res.append(("🟢 RIZIK", "NIZAK"))

    return res


# =====================================================
# BOLESTI (OSNOVNO)
# =====================================================

def bolest(kultura, simptom):

    data = {
        "Paradajz": {
            "Žute fleke": {
                "diag": "Plamenjača",
                "org": ["Mleko 1:10", "Soda bikarbona"],
                "chem": [("Ridomil", "14 dana"), ("Revus", "3 dana")]
            }
        }
    }

    return data.get(kultura, {}).get(simptom)


# =====================================================
# UI
# =====================================================

st.title("🌾 AgroAsistent V2")

# =========================
# TABOVI
# =========================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌱 Radovi",
    "🌦️ Vreme",
    "📸 Bolesti",
    "💰 Troškovi",
    "📓 Dnevnik"
])

# =========================
# TAB 1
# =========================

with tab1:

    kultura = st.selectbox("Kultura", ["Paradajz", "Paprika", "Krastavac"])
    rad = st.multiselect("Rad", ["Sadnja", "Prskanje", "Zalivanje", "Berba"])

    if st.button("Sačuvaj"):
        if rad:
            save_to_github(kultura, ", ".join(rad))

# =========================
# TAB 2
# =========================

with tab2:

    weather = get_weather()

    if weather:

        temp = weather["temp"]
        vlaga = weather["humidity"]
        vetar = weather["wind"]
        kisa = weather["rain"]

        st.metric("Temp", temp)
        st.metric("Vlaga", vlaga)

        st.subheader("🧠 Odluke")

        for n, o in agro_odluka(temp, vlaga, vetar, kisa):
            st.info(f"{n} → {o}")

    st.write("🕒 Lokalno:", datetime.now().strftime("%H:%M"))

# =========================
# TAB 3
# =========================

with tab3:

    st.subheader("📸 Kamera")

    img = st.camera_input("Slikaj biljku")

    kultura = st.selectbox("Kultura", ["Paradajz", "Paprika"])
    simptom = st.selectbox("Simptom", ["Žute fleke"])

    if st.button("Analiza"):

        r = bolest(kultura, simptom)

        if r:
            st.error(r["diag"])

            st.subheader("🌱 Organski")
            st.write(r["org"])

            st.subheader("🧪 Hemija + karenca")
            st.write(r["chem"])

# =========================
# TAB 4
# =========================

with tab4:

    t = st.text_input("Trošak")
    v = st.number_input("Iznos")

    if st.button("Dodaj"):
        save_to_github("TROŠAK", f"{t}:{v}")

# =========================
# TAB 5
# =========================

with tab5:

    try:
        url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO}/main/{FILE_PATH}"
        df = pd.read_csv(url)

        st.dataframe(df.tail(30))

    except:
        st.info("Nema podataka još")
