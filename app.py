import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Kruševac", layout="wide", page_icon="🌾")

# Učitavanje poverljivih podataka
try:
    TOKEN = st.secrets["GITHUB_TOKEN"].strip()
    USER = st.secrets["GITHUB_USER"].strip()
    REPO = st.secrets["REPO_NAME"].strip()
except Exception as e:
    st.error("⚠️ Greška: Niste ispravno popunili Secrets u Streamlit podešavanjima!")
    st.stop()

FILE_PATH = "dnevnik.csv"

# --- FUNKCIJA ZA PISANJE NA GITHUB (PUT METODA) ---
def snimi_na_github(kultura, radnja):
    # TAČAN URL ZA API (ovako mora da izgleda da bi radilo pisanje)
    url = f"https://github.com{USER}/{REPO}/contents/{FILE_PATH}"
    
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # 1. Uzimamo trenutni fajl da dobijemo SHA i stari sadržaj
        res = requests.get(url, headers=headers, timeout=10)
        sha = None
        stari_sadrzaj = ""
        
        if res.status_code == 200:
            sha = res.json().get('sha')
            stari_sadrzaj = base64.b64decode(res.json()['content']).decode('utf-8')
        
        # 2. Priprema novog reda (Datum, Kultura, Rad)
        vreme = datetime.now().strftime('%d.%m.%Y %H:%M')
        # Čistimo zareze iz opisa da ne pokvarimo CSV tabelu
        cist_opis = radnja.replace(",", " ")
        novi_red = f"{vreme},{kultura},{cist_opis}\n"
        
        if not stari_sadrzaj:
            finalni_sadrzaj = "Datum,Kultura,Rad\n" + novi_red
        else:
            finalni_sadrzaj = stari_sadrzaj + novi_red
            
        # 3. Kodiranje u Base64 i slanje
        payload = {
            "message": f"Zapis: {kultura}",
            "content": base64.b64encode(finalni_sadrzaj.encode('utf-8')).decode('utf-8'),
            "sha": sha
        }
        
        r = requests.put(url, headers=headers, json=payload, timeout=10)
        
        if r.status_code in [200, 201]:
            st.success("✅ Uspešno sačuvano na GitHub!")
            st.balloons()
            st.rerun() # Osvežava aplikaciju da se vidi novi red
        else:
            st.error(f"Greška servera ({r.status_code}): {r.text}")
            
    except Exception as e:
        st.error(f"Problem u komunikaciji sa GitHub-om: {e}")

# --- GLAVNI INTERFEJS ---
st.title("🌾 AgroAsistent: Digitalni Dnevnik i Radar")

tab1, tab2 = st.tabs(["🚜 Unos Radova", "🛰️ Radar Kruševac"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        izbor = st.selectbox("Izaberi kulturu:", ["Paradajz", "Paprika", "Voće", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak", "TROŠAK"])
    with col2:
        opis = st.text_input("Šta si danas radio / kupio?")
    
    if st.button("SAČUVAJ TRAJNO NA GITHUB"):
        if opis:
            with st.spinner("Slanje na server..."):
                snimi_na_github(izbor, opis)
        else:
            st.warning("Prvo upiši opis rada!")

with tab2:
    st.subheader("Radar uživo (VremeRadar.rs)")
    components.html('<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>', height=620)

# --- TVOJ POBOLJŠANI KOD ZA ČITANJE DNEVNIKA ---
st.write("---")
st.subheader("📓 Tvoj digitalni dnevnik (Uživo)")

try:
    # Tvoj ispravljen URL za RAW podatke
    url_raw = f"https://githubusercontent.com{USER}/{REPO}/main/{FILE_PATH}"
    
    # Učitavanje sa 'cache busting' parametrom da se uvek vidi najnoviji red
    df = pd.read_csv(f"{url_raw}?v={datetime.now().timestamp()}")
    
    # Prikaz poslednjih 20 redova (da imaš bolji pregled)
    st.dataframe(df.tail(20), use_container_width=True)
except:
    st.info("Ovde će se pojaviti tabela čim uradiš prvi uspešan upis.")
