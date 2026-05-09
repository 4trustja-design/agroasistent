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
    USER = "4trustja-design"
    REPO = "requirements.txt"
except Exception as e:
    st.error("⚠️ Greška: Niste ispravno popunili Secrets u Streamlit podešavanjima!")
    st.stop()

FILE_PATH = "dnevnik.csv"

# --- FUNKCIJA ZA PISANJE NA GITHUB ---
def snimi_na_github(kultura, radnja):
    # 1. ISPRAVAN URL (bez duplih kosa crta i sa 'api.' poddomenom)
    USER = "4trustja-design"
    REPO = "requirements.txt"
    FILE_PATH = "dnevnik.csv"
    
    url = f"https://github.com"

    
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # Prvo proveravamo da li fajl postoji da uzmemo SHA
        res = requests.get(url, headers=headers, timeout=10)
        sha = None
        stari_sadrzaj = ""
        
        if res.status_code == 200:
            podaci = res.json()
            sha = podaci.get('sha')
            stari_sadrzaj = base64.b64decode(podaci['content']).decode('utf-8')
        
        # Priprema novog reda
        vreme = datetime.now().strftime('%d.%m.%Y %H:%M')
        novi_red = f"{vreme},{kultura},{radnja.replace(',', ' ')}\n"
        
        if not stari_sadrzaj:
            finalni_sadrzaj = "Datum,Kultura,Rad\n" + novi_red
        else:
            finalni_sadrzaj = stari_sadrzaj + ('' if stari_sadrzaj.endswith('\n') else '\n') + novi_red
            
        # Slanje na GitHub
        payload = {
            "message": f"Unos: {kultura}",
            "content": base64.b64encode(finalni_sadrzaj.encode('utf-8')).decode('utf-8'),
            "sha": sha
        }
        
        r = requests.put(url, headers=headers, json=payload, timeout=10)
        
        if r.status_code in [200, 201]:
            st.success("✅ Podaci su uspešno sačuvani!")
            st.rerun()
        else:
            st.error(f"Greška {r.status_code}: {r.text}")
            
    except Exception as e:
        st.error(f"Kritična greška u URL-u: {e}")


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
    # Koristimo direktan link ka radarskoj mapi
    components.html('<iframe src="https://vremeiradar.rs" width="100%" height="600" style="border:none;"></iframe>', height=620)

# --- ČITANJE DNEVNIKA ---
st.write("---")
st.subheader("📓 Tvoj digitalni dnevnik (Uživo)")

try:
    # Ispravljen URL za sirove podatke (dodat / nakon domena)
    url_raw = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{FILE_PATH}"
    df = pd.read_csv(f"{url_raw}?v={datetime.now().timestamp()}")
    st.dataframe(df.tail(20), use_container_width=True)
except Exception as e:
    st.info("Tabela će se pojaviti ovde čim unesete prvi podatak. (Ako je fajl prazan, ovo je normalno)")
