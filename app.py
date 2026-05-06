import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide")

# --- KONFIGURACIJA (Ona koja je radila) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Koristimo model koji ti je dokazano radio na slikama
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Podesite GEMINI_API_KEY u Secrets!")

def dobij_prognozu(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,precipitation_sum&timezone=auto"
    try:
        r = requests.get(url, timeout=5).json()
        return {"t": r['daily']['temperature_2m_max'][0], "k": r['daily']['precipitation_sum'][0]}
    except: return None

if 'lat' not in st.session_state: st.session_state.lat, st.session_state.lon = 43.58, 21.32

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
    mesec = "Maj" # Fiksirano na Maj jer je to sada aktuelno
    st.header(f"Plan za {mesec}")
    
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    m_info = f"{meteo['t']}°C, kiša {meteo['k']}mm" if meteo else "Standardno vreme"
    if meteo: st.info(f"🌤️ Trenutno: {m_info}")

    # TVOJE KATEGORIJE
    kat = st.radio("Kategorija:", ["Plastenik", "Otvoreno polje", "Voćnjak (3. god)"], horizontal=True)
    
    if kat == "Plastenik":
        kultura = st.selectbox("Biljka:", ["Paradajz", "Krastavac", "Paprika (Makedonka)"])
    elif kat == "Otvoreno polje":
        kultura = st.selectbox("Biljka:", ["Krompir", "Boranija", "Grašak", "Crni i beli luk", "Lubenica", "Kukuruz šećerac"])
    else:
        kultura = st.selectbox("Voćka (70 stabala, kap-po-kap):", ["Jabuka", "Kruška", "Višnja", "Dunja", "Breskva", "Kajsija", "Trešnja", "Šljiva", "Nektarina", "Lešnik", "Orah"])

    if st.button("✨ Generiši plan"):
        # POBOLJŠANA INSTRUKCIJA ZA PREPARATE
        prompt = f"""Ti si stručni agronom u Srbiji. Napravi plan za {kultura} u mesecu {mesec}.
        Sistem: Kap po kap. Vreme: {m_info}.
        
        ZAHTEV: Za svaki od 4 zadatka OBAVEZNO navedi:
        1. Naziv komercijalnog preparata ili đubriva (npr. Signum, Chorus, Fitofert, itd.)
        2. Tačnu dozu (npr. 0.2% ili 2kg/ha)
        3. Razlog primene.
        
        Format: Zadatak | Detaljan recept sa preparatom i dozom"""

        with st.spinner("AI radi..."):
            try:
                response = model.generate_content(prompt)
                st.subheader("Zadaci:")
                for i, linija in enumerate(response.text.strip().split('\n')):
                    if "|" in linija:
                        z, d = linija.split("|")
                        with st.expander(f"📌 {z.strip()}"):
                            st.write(d.strip())
                            st.checkbox("Izvršeno", key=f"z_{i}")
            except Exception as e:
                st.error(f"Greška: {str(e)}")

with t3:
    pitanje = st.text_input("Pitaj:")
    if st.button("Pošalji"):
        res = model.generate_content(pitanje)
        st.write(res.text)
