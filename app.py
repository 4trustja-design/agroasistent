import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

# Postavke aplikacije
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

# --- LAŽNA BAZA PODATAKA (Primer) ---
vocarstvo_data = {
    "Šljiva": {
        "1. Godina": "Sadnja u jesen, skraćivanje sadnice na 80cm.",
        "Zaštita": "Plavo prskanje u fazi mirovanja.",
        "Prehrana": "Unos stajnjaka ili NPK 15:15:15 pre sadnje."
    },
    "Malina": {
        "1. Godina": "Postavljanje naslona, đubrenje azotnim đubrivima u proleće.",
        "Zaštita": "Tretman protiv didimele nakon kretanja vegetacije."
    }
}

povrtarstvo_data = {
    "Paradajz": {
        "Plastenik": "Sadnja rasada u aprilu, sistem kap po kap.",
        "Otvoreno": "Sadnja krajem maja, razmak 50cm.",
        "Zaštita": "Tretman protiv plamenjače nakon svake jače kiše.",
        "Prehrana": "Prihrana kalijumom u fazi formiranja plodova."
    }
}

# --- GLAVNI INTERFEJS ---
st.title("🚜 AgroAsistent: Voćarstvo & Povrtarstvo")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Moja Lokacija & Vreme"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("Saveti za voćare")
    voce = st.selectbox("Izaberite voćnu vrstu:", list(vocarstvo_data.keys()))
    godina = st.select_slider("Godina zasada:", options=["1. Godina", "2. Godina", "3. Godina", "4. Godina", "5. Godina"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠 Radovi i Sadnja")
        st.write(vocarstvo_data[voce].get(godina, "Nema specifičnih saveta za ovu godinu."))
    
    with col2:
        st.subheader("🛡 Zaštita i 🧪 Prehrana")
        st.write(vocarstvo_data[voce]["Zaštita"])
        st.write(vocarstvo_data[voce]["Prehrana"])

    st.markdown("---")
    st.subheader("✅ Ček lista za odrađene poslove")
    st.checkbox(f"Završeno orezivanje ({voce})")
    st.checkbox(f"Završena zaštita ({voce})")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("Saveti za povrtare")
    povrce = st.selectbox("Izaberite povrće:", list(povrtarstvo_data.keys()))
    tip_uzgoja = st.radio("Tip proizvodnje:", ["Plastenik", "Otvoreno"])
    
    st.subheader("📋 Plan proizvodnje")
    st.write(povrtarstvo_data[povrce][tip_uzgoja])
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.warning("⚠️ Zaštita")
        st.write(povrtarstvo_data[povrce]["Zaštita"])
    with col_p2:
        st.success("💧 Prehrana i Navodnjavanje")
        st.write(povrtarstvo_data[povrce]["Prehrana"])

# --- TAB 3: MAPA I VREME ---
with tab3:
    st.header("📍 Lokacija i Vremenska Prognoza")
    st.info("Kliknite na mapu da označite lokaciju vašeg imanja.")
    
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7) # Centar Srbije
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=400, width=800)

    if map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lng = map_data['last_clicked']['lng']
        st.success(f"Lokacija sačuvana! (Lat: {lat:.2f}, Lng: {lng:.2f})")
        
        # Ovde bi se integrisao API za prognozu (npr. OpenWeatherMap)
        st.warning("🔔 PODSETNIK: Očekuju se padavine za 48h. Planirajte zaštitu protiv plamenjače sutra!")
