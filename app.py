import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Kruševac", layout="wide")

# Čišćenje podataka iz Secrets (uklanjamo slučajne razmake)
try:
    TOKEN = st.secrets["GITHUB_TOKEN"].strip()
    USER = st.secrets["GITHUB_USER"].strip()
    REPO = st.secrets["REPO_NAME"].strip()
except Exception as e:
    st.error("⚠️ Greška: Proveri Streamlit Secrets! Neki podatak nedostaje.")
    st.stop()

FILE_PATH = "dnevnik.csv"

# FUNKCIJA ZA SNIMANJE
def snimi_na_github(kultura, radnja):
    # Pravimo precizan URL
    url = f"https://github.com{USER}/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # 1. Uzimamo trenutni fajl (sa timeout-om od 10 sekundi)
        res = requests.get(url, headers=headers, timeout=10)
        sha = res.json().get('sha') if res.status_code == 200 else None
        
        vreme = datetime.now().strftime('%d.%m.%Y %H:%M')
        novi_red = f"{vreme},{kultura},{radnja}\n"
        
        # 2. Sklapanje novog sadržaja
        if res.status_code == 200:
            stari_sadrzaj = base64.b64decode(res.json()['content']).decode('utf-8')
            finalni_sadrzaj = stari_sadrzaj + novi_red
        else:
            finalni_sadrzaj = "Vreme,Kultura,Rad\n" + novi_red
            
        # 3. Slanje nazad na GitHub
        payload = {
            "message": f"Dnevnik update: {kultura}",
            "content": base64.b64encode(finalni_sadrzaj.encode('utf-8')).decode('utf-8'),
            "sha": sha
        }
        
        r = requests.put(url, headers=headers, json=payload, timeout=10)
        
        if r.status_code in [200, 201]:
            st.success("✅ Uspešno sačuvano na GitHub!")
            st.balloons()
            st.cache_data.clear()
        else:
            st.error(f"Greška na serveru ({r.status_code}): {r.text}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Problem sa internet vezom: {str(e)}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

# --- INTERFEJS ---
tab1, tab2 = st.tabs(["🚜 Radovi", "🛰️ Radar"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        izabrana_kultura = st.selectbox("Biljka:", ["Paradajz", "Paprika", "Voće", "Krompir", "Luk", "Boranija", "Grašak", "Lubenica", "Bundeva", "TROŠAK"])
    with col2:
        opis_rada = st.text_input("Šta si radio/kupio?", key="input_rada")
    
    # Dugme koje pokreće proces
    if st.button("SAČUVAJ TRAJNO"):
        if opis_rada:
            snimi_na_github(izabrana_kultura, opis_rada)
        else:
            st.warning("Upiši opis pre čuvanja.")

with tab2:
    st.subheader("Radar Kruševac")
    components.html('<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>', height=620)

# --- PRIKAZ DNEVNIKA ---
st.write("---")
st.subheader("📓 Tvoj dnevnik")
try:
    url_raw = f"https://githubusercontent.com{USER}/{REPO}/main/{FILE_PATH}"
    # Nateraj internet da ne pamti staru verziju tabele
    df = pd.read_csv(f"{url_raw}?v={datetime.now().timestamp()}")
    st.dataframe(df.tail(20), use_container_width=True)
except:
    st.info("Ovde će se pojaviti tabela nakon prvog unosa.")
