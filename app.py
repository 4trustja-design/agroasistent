import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. POSTAVKE ---
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🚜")

# --- 2. KOMPLETNA BAZA RADOVA (Definisana na vrhu da izbegnemo NameError) ---
sveobuhvatni_planovi = {
    1: {"Šljiva": [{"id":"slj_1_1","zadatak":"Zimska rezidba","tip":"Rad"}],"Malina":[{"id":"mal_1_1","zadatak":"Čišćenje snega sa mreža","tip":"Rad"}],"Paradajz":[{"id":"par_1_1","zadatak":"Nabavka semena","tip":"Priprema"}]},
    2: {"Šljiva": [{"id":"slj_2_1","zadatak":"Plavo ulje (bakar)","tip":"Zaštita"}],"Malina":[{"id":"mal_2_1","zadatak":"Rezidba dvorodnih","tip":"Rad"}],"Paradajz":[{"id":"par_2_1","zadatak":"Setva rasada","tip":"Rad"}]},
    3: {"Šljiva": [{"id":"slj_3_1","zadatak":"NPK đubrenje","tip":"Prehrana"}],"Malina":[{"id":"mal_3_1","zadatak":"Vezivanje za žicu","tip":"Rad"}],"Paradajz":[{"id":"par_3_1","zadatak":"Pikiranje rasada","tip":"Rad"}]},
    4: {"Šljiva": [{"id":"slj_4_1","zadatak":"Zaštita od Monilije","tip":"Zaštita"}],"Malina":[{"id":"mal_4_1","zadatak":"Zaštita od didimele","tip":"Zaštita"}],"Paradajz":[{"id":"par_4_1","zadatak":"Kaljenje rasada","tip":"Priprema"}]},
    5: {"Šljiva": [{"id":"slj_5_1","zadatak":"Zaštita od vaši i šupljikavosti","tip":"Zaštita"}],"Malina":[{"id":"mal_5_1","zadatak":"Zakidanje prvih izdanaka","tip":"Rad"}],"Paradajz":[{"id":"par_5_1","zadatak":"Sadnja na otvoreno","tip":"Rad"}]},
    6: {"Šljiva": [{"id":"slj_6_1","zadatak":"Zaštita od smotavca","tip":"Zaštita"}],"Malina":[{"id":"mal_6_1","zadatak":"Zaštita od truleži (Botritis)","tip":"Zaštita"}],"Paradajz":[{"id":"par_6_1","zadatak":"Zalamanje zaperaka","tip":"Rad"}]},
    7: {"Šljiva": [{"id":"slj_7_1","zadatak":"Navodnjavanje","tip":"Rad"}],"Malina":[{"id":"mal_7_1","zadatak":"Berba i vlažnost","tip":"Rad"}],"Paradajz":[{"id":"par_7_1","zadatak":"Prihrana kalijumom","tip":"Prehrana"}]},
    8: {"Šljiva": [{"id":"slj_8_1","zadatak":"Berba","tip":"Rad"}],"Malina":[{"id":"mal_8_1","zadatak":"Izbacivanje starih izdanaka","tip":"Rad"}],"Paradajz":[{"id":"par_8_1","zadatak":"Zaštita od plamenjače","tip":"Zaštita"}]},
    9: {"Šljiva": [{"id":"slj_9_1","zadatak":"Sakupljanje opalih plodova","tip":"Rad"}],"Malina":[{"id":"mal_9_1","zadatak":"Đubrenje fosforom i kalijumom","tip":"Prehrana"}],"Paradajz":[{"id":"par_9_1","zadatak":"Sakupljanje semena","tip":"Rad"}]},
    10: {"Šljiva": [{"id":"slj_10_1","zadatak":"Đubrenje stajnjakom","tip":"Prehrana"}],"Malina":[{"id":"mal_10_1","zadatak":"Priprema naslona","tip":"Rad"}],"Paradajz":[{"id":"par_10_1","zadatak":"Čišćenje bašte","tip":"Rad"}]},
    11: {"Šljiva": [{"id":"slj_11_1","zadatak":"Jesenja sadnja","tip":"Rad"}],"Malina":[{"id":"mal_11_1","zadatak":"Plavo prskanje","tip":"Zaštita"}],"Paradajz":[{"id":"par_11_1","zadatak":"Duboko oranje","tip":"Rad"}]},
    12: {"Šljiva": [{"id":"slj_12_1","zadatak":"Krečenje stabala","tip":"Rad"}],"Malina":[{"id":"mal_12_1","zadatak":"Kontrola ograde","tip":"Rad"}],"Paradajz":[{"id":"par_12_1","zadatak":"Plan plodoreda","tip":"Priprema"}]}
}

# --- 3. POMOĆNE FUNKCIJE ---
def dobij_prognozu(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    try:
        r = requests.get(url, timeout=5).json()
        return {
            "max_t": r['daily']['temperature_2m_max'][0],
            "min_t": r['daily']['temperature_2m_min'][0],
            "kisa": r['daily']['precipitation_sum'][0]
        }
    except:
        return None

# --- 4. INICIJALIZACIJA STANJA ---
if 'zavrseni_zadaci' not in st.session_state:
    st.session_state.zavrseni_zadaci = set()
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 44.0165, 21.0059

# --- 5. GLAVNI UI ---
st.title("🚜 AgroAsistent Pro")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📅 Mesečni Plan", "📍 Lokacija", "🤖 AI Savetnik"])

with tab4:
    st.header("📍 Lokacija")
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=350, width=800, key="global_map")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.success("Lokacija zapamćena!")

with tab3:
    mesec = datetime.now().month
    meseci_nazivi = {1:"Januar",2:"Februar",3:"Mart",4:"April",5:"Maj",6:"Jun",7:"Jul",8:"Avgust",9:"Septembar",10:"Oktobar",11:"Novembar",12:"Decembar"}
    
    st.header(f"📅 Plan za {meseci_nazivi[mesec]}")
    
    # METEO ANALIZA
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    if meteo:
        col1, col2, col3 = st.columns(3)
        col1.metric("Max Temp", f"{meteo['max_t']}°C")
        col2.metric("Min Temp", f"{meteo['min_t']}°C")
        col3.metric("Padavine", f"{meteo['kisa']}mm")
        
        # Automatska upozorenja
        if meteo['max_t'] > 32:
            st.warning("⚠️ EKSTREMNA VRUĆINA: Navodnjavanje obavezno rano ujutru ili kasno uveče!")
        if meteo['min_t'] < 2:
            st.error("❄️ OPASNOST OD MRAZA: Zaštitite o
