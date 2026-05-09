import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Kruševac", layout="wide")

# Učitavanje poverljivih podataka iz Streamlit Secrets
try:
    TOKEN = st.secrets["GITHUB_TOKEN"].strip()
    USER = st.secrets["GITHUB_USER"].strip()
    REPO = st.secrets["REPO_NAME"].strip()
except:
    st.error("⚠️ Greška: Nisi popunio Secrets u Streamlit podešavanjima!")
    st.stop()

FILE_PATH = "dnevnik.csv"

# --- FUNKCIJA ZA PISANJE (TVOJ REPO) ---
def snimi_na_github(kultura, radnja):
    url = f"https://github.com{USER}/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}"}
    
    # Provera da li fajl postoji
    res = requests.get(url, headers=headers)
    sha = res.json().get('sha') if res.status_code == 200 else None
    
    novi_red = f"{datetime.now().strftime('%d.%m.%Y %H:%M')},{kultura},{radnja}\n"
    
    if res.status_code == 200:
        stari_sadrzaj = base64.b64decode(res.json()['content']).decode('utf-8')
        finalni_sadrzaj = stari_sadrzaj + novi_red
    else:
        finalni_sadrzaj = "Vreme,Kultura,Rad\n" + novi_red
        
    payload = {
        "message": f"Zapis: {kultura}",
        "content": base64.b64encode(finalni_sadrzaj.encode('utf-8')).decode('utf-8'),
        "sha": sha
    }
    
    r = requests.put(url, headers=headers, json=payload)
    if r.status_code == 200 or r.status_code == 201:
        st.success("✅ Uspešno sačuvano na GitHub!")
        st.balloons()
        st.rerun()
    else:
        st.error(f"Greška pri slanju: {r.text}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

# --- UNOS RADNIH AKTIVNOSTI ---
tab1, tab2 = st.tabs(["🚜 Radovi", "🛰️ Radar"])

with tab1:
    c1, c2 = st.columns(2)
    kultura = c1.selectbox("Biljka:", ["Paradajz", "Paprika", "Voće", "Krompir", "Luk", "TROŠAK"])
    rad = c2.text_input("Šta si radio/kupio?")
    if st.button("SAČUVAJ TRAJNO"):
        if rad:
            snimi_na_github(kultura, rad)

with tab2:
    st.subheader("Radar Kruševac")
    components.html('<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>', height=620)

# --- TVOJ ISPRAVLJEN KOD ZA ČITANJE ---
st.write("---")
st.subheader("📓 Tvoj dnevnik (Uživo sa GitHub-a)")
try:
    # 1. Tvoj ispravljen URL
    url_raw = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{FILE_PATH}"
    
    # 2. Učitavanje sa tvojim 'cache busting' parametrom
    df = pd.read_csv(f"{url_raw}?v={datetime.now().timestamp()}")
    
    # 3. Prikaz poslednjih 15 redova
    st.dataframe(df.tail(15), use_container_width=True)
except Exception as e:
    st.info("Tabela će se pojaviti ovde nakon prvog uspešnog upisa.")
