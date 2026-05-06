import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. POSTAVKE ---
st.set_page_config(page_title="AgroAsistent AI Pro", layout="wide")

# --- 2. KONFIGURACIJA AI MODELA ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("KLJUČ NIJE PRONAĐEN U SECRETS!")

# --- 3. POMOĆNE FUNKCIJE ---
def dobij_prognozu(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    try:
        r = requests.get(url, timeout=10).json()
        return {
            "max_t": r['daily']['temperature_2m_max'][0],
            "kisa": r['daily']['precipitation_sum'][0]
        }
    except: return None

# --- 4. SESSION STATE ---
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 44.01, 21.00

# --- 5. UI ---
st.title("🚜 AgroAsistent AI")
tabs = st.tabs(["📋 AI Planer", "📍 Lokacija", "🍎 Voćarstvo", "💬 AI Chat"])

with tabs[1]: # LOKACIJA
    st.header("📍 Lokacija")
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=350, width=800, key="mapa_v11")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.success("Lokacija sačuvana!")

with tabs[0]: # PLANER
    meseci = {1:"Januar",2:"Februar",3:"Mart",4:"April",5:"Maj",6:"Jun",7:"Jul",8:"Avgust",9:"Septembar",10:"Oktobar",11:"Novembar",12:"Decembar"}
    mesec_naziv = meseci[datetime.now().month]
    
    st.header(f"📅 Planer za {mesec_naziv}")
    
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    meteo_info = "Vreme je uobičajeno."
    if meteo:
        st.info(f"🌤️ Max: {meteo['max_t']}°C | Kiša: {meteo['kisa']}mm")
        meteo_info = f"Temperatura {meteo['max_t']}C, padavine {meteo['kisa']}mm."

    kultura = st.selectbox("Kultura:", ["Šljiva", "Malina", "Paradajz", "Paprika"])

    if st.button("✨ Generiši AI plan", type="primary"):
        prompt = f"Ti si agronom. Napravi plan za {kultura} u Srbiji za mesec {mesec_naziv}. Vreme: {meteo_info}. Navedi 4 zadatka sa preparatima. Format: Zadatak | Opis i preparat"
        
        with st.spinner("AI razmišlja..."):
            try:
                # Zvanična metoda koja je najsigurnija
                response = model.generate_content(prompt)
                tekst = response.text
                
                st.subheader(f"✅ Zadaci za {kultura}:")
                for i, linija in enumerate(tekst.strip().split('\n')):
                    if "|" in linija:
                        zadatak, detalj = linija.split("|")
                        c1, c2 = st.columns([1, 10])
                        with c1: st.checkbox("", key=f"t_{kultura}_{i}")
                        with c2: st.markdown(f"**{zadatak.strip()}** - {detalj.strip()}")
            except Exception as e:
                st.error(f"AI Greška: {str(e)}")
                st.info("Savet: Proverite da li je API ključ u AI Studiju označen kao aktivan.")

with tabs[3]: # CHAT
    st.header("💬 Pitaj agronoma")
    pitanje = st.text_input("Tvoje pitanje:")
    if st.button("Pošalji"):
        if pitanje:
            try:
                res = model.generate_content(f"Kratko odgovori: {pitanje}")
                st.info(res.text)
            except: st.error("AI trenutno ne odgovara.")

with tabs[2]: st.write("Katalog voća u pripremi...")
