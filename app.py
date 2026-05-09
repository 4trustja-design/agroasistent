import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Kruševac", layout="wide")

# Učitavanje podataka iz Secrets (čistimo ih od razmaka)
try:
    TOKEN = st.secrets["GITHUB_TOKEN"].strip()
    USER = st.secrets["GITHUB_USER"].strip()
    REPO = st.secrets["REPO_NAME"].strip()
except:
    st.error("⚠️ Greška: Nisu popunjeni Secrets u Streamlit podešavanjima!")
    st.stop()

FILE_PATH = "dnevnik.csv"

# FUNKCIJA ZA SNIMANJE NA GITHUB (POPRAVLJENA)
def snimi_na_github(kultura, radnja):
    # OVDE JE POPRAVLJENO: Adresa je sada razdvojena kako treba
    url = f"https://github.com{USER}/{REPO}/contents/{FILE_PATH}"
    
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # 1. Provera postojanja fajla
        res = requests.get(url, headers=headers, timeout=15)
        sha = None
        stari_sadrzaj = ""
        
        if res.status_code == 200:
            sha = res.json().get('sha')
            stari_sadrzaj = base64.b64decode(res.json()['content']).decode('utf-8')
        
        # 2. Novi red podataka
        vreme = datetime.now().strftime('%d.%m.%Y %H:%M')
        # Čistimo zareze da ne pokvarimo tabelu
        cista_radnja = radnja.replace(",", " ")
        novi_red = f"{vreme},{kultura},{cista_radnja}\n"
        
        if not stari_sadrzaj:
            finalni_sadrzaj = "Datum,Kultura,Rad\n" + novi_red
        else:
            finalni_sadrzaj = stari_sadrzaj + novi_red
            
        # 3. Slanje na GitHub
        payload = {
            "message": f"Zapis: {kultura}",
            "content": base64.b64encode(finalni_sadrzaj.encode('utf-8')).decode('utf-8'),
            "sha": sha
        }
        
        r = requests.put(url, headers=headers, json=payload, timeout=15)
        
        # PROVERA USPEHA (Popravljena linija)
        if r.status_code == 200 or r.status_code == 201:
            st.success("✅ Uspešno sačuvano na GitHub!")
            st.balloons()
            st.rerun()
        else:
            st.error(f"Greška na GitHub-u (Kod {r.status_code}): {r.text}")
            
    except Exception as e:
        st.error(f"Sistemska greška: {str(e)}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

# --- INTERFEJS ---
tab1, tab2 = st.tabs(["🚜 Radovi", "🛰️ Radar"])

with tab1:
    c1, c2 = st.columns(2)
    izbor = c1.selectbox("Kultura:", ["Paradajz", "Paprika", "Voće", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak", "TROŠAK"])
    rad = c2.text_input("Šta si radio/kupio?", key="input_rada")
    
    if st.button("SAČUVAJ TRAJNO"):
        if rad:
            snimi_na_github(izbor, rad)
        else:
            st.warning("Prvo upiši opis rada!")

with tab2:
    st.subheader("Radar Kruševac")
    components.html('<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>', height=620)

# --- PRIKAZ DNEVNIKA ---
st.write("---")
st.subheader("📓 Tvoj digitalni dnevnik")
try:
    # URL za direktne podatke
    url_raw = f"https://githubusercontent.com{USER}/{REPO}/main/{FILE_PATH}"
    # Timestamp tera aplikaciju da ne učitava stare podatke iz memorije
    df = pd.read_csv(f"{url_raw}?v={datetime.now().timestamp()}")
    st.dataframe(df.tail(20), use_container_width=True)
except:
    st.info("Tabela će se pojaviti ovde nakon prvog upisa.")
