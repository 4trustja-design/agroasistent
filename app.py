import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide")

# --- 1. PAMETNA KONFIGURACIJA MODELA ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Pokušavamo da nađemo bilo koji dostupan model na tvom nalogu
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Biramo prvi dostupan (obično gemini-1.5-flash ili gemini-pro)
        model_name = available_models[0] if available_models else "models/gemini-pro"
        model = genai.GenerativeModel(model_name)
    except:
        # Ako list_models zakaže, idemo na najsigurniju varijantu bez 'models/' prefiksa
        model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Podesite GEMINI_API_KEY u Secrets!")

# --- 2. FUNKCIJE ---
def dobij_prognozu(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,precipitation_sum&timezone=auto"
    try:
        r = requests.get(url, timeout=5).json()
        return {"t": r['daily']['temperature_2m_max'][0], "k": r['daily']['precipitation_sum'][0]}
    except: return None

if 'lat' not in st.session_state: st.session_state.lat, st.session_state.lon = 44.01, 21.00

# --- 3. UI ---
st.title("🚜 AgroAsistent AI")
t1, t2, t3 = st.tabs(["📋 Planer", "📍 Lokacija", "💬 Chat"])

with t2:
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=300, width=700, key="mapa")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']

with t1:
    mesec = datetime.now().strftime("%B")
    st.header(f"Plan za {mesec}")
    
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    m_info = f"{meteo['t']}°C, kiša {meteo['k']}mm" if meteo else "Standardno vreme"
    if meteo: st.info(f"🌤️ Trenutno: {m_info}")

    kultura = st.selectbox("Kultura:", ["Šljiva", "Malina", "Paradajz"])
    
    if st.button("✨ Generiši plan"):
        prompt = f"Ti si agronom. Kratka lista 4 zadatka za {kultura} u mesecu {mesec}. Vreme: {m_info}. Format: Zadatak | Opis"
        with st.spinner("AI radi..."):
            try:
                # Slanje upita
                response = model.generate_content(prompt)
                
                # Prikazivanje rezultata
                st.subheader(f"Zadaci:")
                for i, linija in enumerate(response.text.strip().split('\n')):
                    if "|" in linija:
                        z, d = linija.split("|")
                        st.checkbox(f"**{z.strip()}** - {d.strip()}", key=f"z_{i}")
            except Exception as e:
                st.error(f"Greška: {str(e)}")
                st.info("Pokušajte da osvežite stranicu (Refresh).")

with t3:
    pitanje = st.text_input("Pitaj:")
    if st.button("Pošalji"):
        try:
            res = model.generate_content(pitanje)
            st.write(res.text)
        except: st.error("AI nedostupan.")
