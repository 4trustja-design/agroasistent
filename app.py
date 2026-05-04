import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from datetime import datetime
import requests

# --- 1. KONFIGURACIJA ---
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSccBzwQSmytB6TSzYLmcj429FiWMVGm7WUTUi5GqZZUHV6C_g/formResponse"

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # DODATO: Isključujemo sigurnosne filtere koji blokiraju nazive preparata
    safety_settings = [
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    ]
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', safety_settings=safety_settings)
except Exception as e:
    st.error("Problem sa API ključem u Secrets podešavanjima.")

# --- 2. FUNKCIJE ---
def posalji_u_tabelu(ime, radnja):
    payload = {"entry.880598687": ime, "entry.31175628": radnja, "entry.1741593922": "Obavljeno"}
    try: requests.post(FORM_URL, data=payload); return True
    except: return False

def dobij_vreme(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=precipitation_sum&timezone=auto"
    try:
        r = requests.get(url).json()
        return r['current_weather']['temperature'], r['daily']['precipitation_sum'][0]
    except: return None, None

# --- 3. UI ---
st.set_page_config(page_title="AgroSmart Srbija", layout="wide")

with st.sidebar:
    st.header("👤 Profil")
    korisnik = st.text_input("Ime / ID:", "Gost")
    st.divider()
    st.write("📊 [Tabela radova](https://docs.google.com/spreadsheets/d/1DU-w1I6yMuLIq9qQYhMGxdWds9dvaG9QlezJs87vExk/edit)")

st.title(f"🚜 AgroAsistent: {korisnik}")

# MAPA I VREME
c1, c2 = st.columns([2, 1])
with c1:
    st.subheader("📍 Odaberi lokaciju")
    # Centar Srbije
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    
    # POBOALJŠANO: Mapa sada bolje hvata klik
    map_data = st_folium(m, height=300, use_container_width=True, key="agro_mapa")
    
    # Logika za koordinate
    lat, lon = 44.0165, 21.0059
    if map_data and map_data.get('last_clicked'):
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
        st.success(f"Lokacija pinovana: {round(lat,3)}, {round(lon,3)}")

with c2:
    st.subheader("🌦️ Prognoza")
    temp, kisa = dobij_vreme(lat, lon)
    if temp is not None:
        st.metric("Temperatura", f"{temp}°C")
        st.metric("Padavine danas", f"{kisa}mm")

st.divider()

# INPUT I AI
col_input, col_savet = st.columns([1, 2])
with col_input:
    st.subheader("⚙️ Podešavanja")
    grana = st.radio("Grana:", ["Voćarstvo", "Povrtarstvo"])
    if grana == "Voćarstvo":
        kultura = st.selectbox("Kultura:", ["Šljiva", "Jabuka", "Malina", "Trešnja"])
        detalj = st.selectbox("Faza:", ["1. godina", "2. godina", "Pun rod"])
    else:
        kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac"])
        detalj = st.selectbox("Način:", ["Otvoreno polje", "Plastenik"])

    if st.button("Generiši plan"):
        with st.spinner("AI analizira..."):
            prompt = f"Stručni agronom Srbija. {grana}, {kultura}, {detalj}. Maj mesec. Temp: {temp}C. Daj 3 kratka zadatka sa nazivima preparata i dozom. Lista od 3 stavke."
            try:
                response = model.generate_content(prompt)
                if response and response.text:
                    st.session_state.lista_zadataka = [z.strip() for z in response.text.split('\n') if len(z) > 10][:3]
                else:
                    st.error("AI je vratio prazan odgovor. Pokušajte ponovo.")
            except Exception as e:
                st.error(f"Greška: {str(e)}")

with col_savet:
    st.subheader("📋 Preporučeni radovi")
    if 'lista_zadataka' in st.session_state:
        for zadatak in st.session_state.lista_zadataka:
            if st.button(f"✅ Završeno: {zadatak}", use_container_width=True):
                if korisnik != "Gost":
                    if posalji_u_tabelu(korisnik, zadatak):
                        st.success("Zapisano!")
                    else: st.error("Greška sa tabelom.")
                else: st.warning("Unesite ime levo.")
