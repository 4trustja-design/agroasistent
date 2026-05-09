import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Kruševac", layout="wide")

# Podaci iz Secrets
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    USER = st.secrets["GITHUB_USER"]
    REPO = st.secrets["REPO_NAME"]
except:
    st.error("⚠️ Nisi popunio Secrets u Streamlit podešavanjima!")
    st.stop()

FILE_PATH = "dnevnik.csv"

# FUNKCIJA KOJA SE POKREĆE SAMO NA KLIK
def snimi_na_github(kultura, radnja):
    url = f"https://github.com{USER}/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}"}
    
    # 1. Provera postojanja fajla
    res = requests.get(url, headers=headers)
    sha = res.json().get('sha') if res.status_code == 200 else None
    
    # 2. Formatiranje novog reda
    vreme = datetime.now().strftime('%d.%m.%Y %H:%M')
    novi_red = f"{vreme},{kultura},{radnja}\n"
    
    # 3. Priprema sadržaja
    if res.status_code == 200:
        stari_sadrzaj = base64.b64decode(res.json()['content']).decode('utf-8')
        finalni_sadrzaj = stari_sadrzaj + novi_red
    else:
        finalni_sadrzaj = "Vreme,Kultura,Rad\n" + novi_red
        
    # 4. Slanje na GitHub
    payload = {
        "message": f"Zapis: {kultura}",
        "content": base64.b64encode(finalni_sadrzaj.encode('utf-8')).decode('utf-8'),
        "sha": sha
    }
    
    r = requests.put(url, headers=headers, json=payload)
    if r.status_code in [200, 201]:
        st.success("✅ Rad je trajno sačuvan na GitHub-u!")
        st.balloons()
    else:
        st.error(f"Greška pri čuvanju: {r.text}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

# --- INTERFEJS ---
tab1, tab2 = st.tabs(["🚜 Radovi", "🛰️ Radar"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        izabrana_kultura = st.selectbox("Biljka:", ["Paradajz", "Paprika", "Voće", "Krompir", "Luk", "Boranija", "Grašak", "Lubenica", "Bundeva", "TROŠAK"])
    with col2:
        opis_rada = st.text_input("Šta si radio/kupio?", placeholder="Npr. Zalivanje, Prskanje...")
    
    # DUGME KOJE POKREĆE FUNKCIJU
    if st.button("SAČUVAJ TRAJNO NA GITHUB"):
        if opis_rada:
            with st.spinner("Slanje podataka na server..."):
                snimi_na_github(izabrana_kultura, opis_rada)
        else:
            st.warning("Upiši opis rada pre čuvanja.")

with tab2:
    st.subheader("Radar Kruševac (VremeRadar.rs)")
    components.html('<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>', height=620)

# --- PRIKAZ DNEVNIKA ---
st.write("---")
st.subheader("📓 Tvoj digitalni dnevnik")

try:
    url_raw = f"https://githubusercontent.com{USER}/{REPO}/main/{FILE_PATH}"
    # Nateraj pretraživač da uvek vuče novu verziju
    url_refresh = f"{url_raw}?v={datetime.now().timestamp()}"
    df = pd.read_csv(url_refresh)
    st.dataframe(df.tail(20), use_container_width=True)
except:
    st.info("Tabela će se pojaviti ovde nakon što prvi put klikneš na 'SAČUVAJ'.")
