import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Kruševac", layout="wide")

# Učitavanje Secrets - uklanjamo sve nepotrebne karaktere
try:
    TOKEN = st.secrets["GITHUB_TOKEN"].strip()
    USER = st.secrets["GITHUB_USER"].strip()
    REPO = st.secrets["REPO_NAME"].strip()
except Exception as e:
    st.error("⚠️ Greška: Nisu popunjeni Secrets u Streamlit podešavanjima!")
    st.stop()

FILE_PATH = "dnevnik.csv"

# FUNKCIJA ZA SNIMANJE NA GITHUB
def snimi_na_github(kultura, radnja):
    # OVDE SMO POPRAVILI URL DA SE NE "LEPI"
    url = f"https://github.com{USER}/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # 1. Provera da li fajl već postoji
        res = requests.get(url, headers=headers, timeout=15)
        sha = None
        stari_sadrzaj = ""
        
        if res.status_code == 200:
            sha = res.json().get('sha')
            stari_sadrzaj = base64.b64decode(res.json()['content']).decode('utf-8')
        
        # 2. Priprema novog reda
        vreme = datetime.now().strftime('%d.%m.%Y %H:%M')
        novi_red = f"{vreme},{kultura},{radnja}\n"
        
        # Ako je fajl nov, dodajemo zaglavlje
        if not stari_sadrzaj:
            finalni_sadrzaj = "Datum,Kultura,Rad\n" + novi_red
        else:
            finalni_sadrzaj = stari_sadrzaj + novi_red
            
        # 3. Slanje na GitHub
        payload = {
            "message": f"Zapis za {kultura}",
            "content": base64.b64encode(finalni_sadrzaj.encode('utf-8')).decode('utf-8'),
            "sha": sha
        }
        
        r = requests.put(url, headers=headers, json=payload, timeout=15)
        
        # POPRAVLJENA PROVERA (Sada je ispravna Python sintaksa)
        if r.status_code in [200, 201]:
            st.success("✅ Uspešno sačuvano na GitHub!")
            st.balloons()
            st.rerun()
        else:
            st.error(f"Greška servera: {r.status_code}")
            
    except Exception as e:
        st.error(f"Problem u komunikaciji: {str(e)}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

# --- INTERFEJS ---
tab1, tab2 = st.tabs(["🚜 Radovi", "🛰️ Radar"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        izabrana_kultura = st.selectbox("Izaberi biljku:", ["Paradajz", "Paprika", "Voće", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak", "TROŠAK"])
    with col2:
        opis_rada = st.text_input("Šta si radio/kupio?")
    
    if st.button("SAČUVAJ TRAJNO"):
        if opis_rada:
            snimi_na_github(izabrana_kultura, opis_rada)
        else:
            st.warning("Prvo upiši opis rada!")

with tab2:
    st.subheader("Radar Kruševac")
    components.html('<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>', height=620)

# --- PRIKAZ DNEVNIKA ---
st.write("---")
st.subheader("📓 Tvoj digitalni dnevnik")
try:
    # URL za sirove podatke
    url_raw = f"https://githubusercontent.com{USER}/{REPO}/main/{FILE_PATH}"
    # Dodajemo v= timestamp da nateramo GitHub da nam ne šalje staru verziju iz memorije
    df = pd.read_csv(f"{url_raw}?v={datetime.now().timestamp()}")
    st.dataframe(df.tail(15), use_container_width=True)
except:
    st.info("Ovde će se pojaviti tabela nakon što prvi put klikneš na 'SAČUVAJ'.")
