import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. PROŠIRENA BAZA RADOVA (DODATAK ZA EKSTREME) ---
ekstremni_saveti = {
    "Vrućina": "⚠️ VELIKA VRUĆINA: Povećati zalivanje, vršiti navodnjavanje isključivo kasno uveče ili rano ujutru.",
    "Kiša": "⚠️ PREVIŠE PADAVINA: Visok rizik od plamenjače i truleži! Obavezna zaštita čim se vreme stabilizuje.",
    "Optimalno": "✅ Vremenski uslovi su povoljni za redovne poljske radove."
}

# (Ovde ide onaj tvoj veliki 'sveobuhvatni_planovi' rečnik za 12 meseci)

# --- 2. FUNKCIJA ZA PROVERU METEO USLOVA ---
def proveri_meteo_uslove(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=precipitation_sum,temperature_2m_max&timezone=auto"
    try:
        r = requests.get(url).json()
        temp_max = r['daily']['temperature_2m_max'][0]
        kisa_sum = r['daily']['precipitation_sum'][0]
        return temp_max, kisa_sum
    except:
        return None, None

# --- 3. GLAVNI INTERFEJS ---
st.set_page_config(page_title="AgroAsistent Pro", layout="wide")
st.title("🚜 AgroAsistent: Pametna Automatizacija")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📅 Mesečni Plan", "📍 Lokacija", "🤖 AI Savetnik"])

# Inicijalizacija lokacije (ako korisnik nije kliknuo, stavljamo centar Srbije)
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 44.0165, 21.0059

with tab4:
    st.header("📍 Lokacija imanja")
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=7)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=400, width=800, key="map_v9")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.success("Lokacija ažurirana!")

with tab3:
    mesec_broj = datetime.now().month
    st.header(f"📅 Dinamički plan za Maj")

    # --- AUTOMATIZACIJA PREMA VREMENU ---
    t_max, kisa = proveri_meteo_uslove(st.session_state.lat, st.session_state.lon)
    
    if t_max is not None:
        st.subheader("🌦️ Analiza vremenskih uslova za tvoju lokaciju:")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Prognozirana Max Temp.", f"{t_max}°C")
        col_m2.metric("Očekivane padavine", f"{kisa} mm")

        # Logika za automatske savete
        if t_max > 32:
            st.warning(ekstremni_saveti["Vrućina"])
        elif kisa > 10:
            st.error(ekstremni_saveti["Kiša"])
        else:
            st.success(ekstremni_saveti["Optimalno"])
    
    st.divider()

    # Redovni planovi (To-Do lista)
    plan_za_mesec = sveobuhvatni_planovi.get(mesec_broj, {})
    # ... (ostatak koda za To-Do listu sa checkboxovima ostaje isti)
