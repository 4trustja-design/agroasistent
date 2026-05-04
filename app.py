import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests

# --- 1. KONFIGURACIJA ---
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSccBzwQSmytB6TSzYLmcj429FiWMVGm7WUTUi5GqZZUHV6C_g/formResponse"

# Povezivanje sa Google AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Koristimo 'gemini-pro' jer je on bio najstabilniji u tvojoj prvoj verziji
    model = genai.GenerativeModel('gemini-pro')
else:
    st.error("Nedostaje API ključ u Secrets podešavanjima!")
    st.stop()

# --- 2. FUNKCIJE ---
def posalji_u_tabelu(ime, radnja):
    payload = {
        "entry.880598687": ime,    
        "entry.31175628": radnja,  
        "entry.1741593922": "Obavljeno" 
    }
    try:
        requests.post(FORM_URL, data=payload, timeout=5)
        return True
    except:
        return False

def dobij_vreme(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=precipitation_sum&timezone=auto"
    try:
        r = requests.get(url, timeout=5).json()
        return r['current_weather']['temperature'], r['daily']['precipitation_sum'][0]
    except:
        return None, None

# --- 3. UI DIZAJN ---
st.set_page_config(page_title="AgroSmart Srbija", layout="wide")

with st.sidebar:
    st.header("👤 Korisnik")
    korisnik = st.text_input("Vaše ime (ID):", "Gost")
    st.divider()
    st.write("📊 [Tabela radova](https://docs.google.com/spreadsheets/d/1DU-w1I6yMuLIq9qQYhMGxdWds9dvaG9QlezJs87vExk/edit)")

st.title(f"🚜 AgroAsistent: {korisnik}")

c1, c2 = st.columns([2, 1])
with c1:
    st.subheader("📍 Lokacija imanja")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=300, use_container_width=True, key="agro_map_stable")
    
    lat, lon = 44.0165, 21.0059
    if map_data and map_data.get('last_clicked'):
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
        st.success(f"Lokacija potvrđena!")

with c2:
    st.subheader("🌦️ Prognoza")
    temp, kisa = dobij_vreme(lat, lon)
    if temp is not None:
        st.metric("Temperatura", f"{temp}°C")
        st.metric("Padavine danas", f"{kisa}mm")
    else:
        st.info("Kliknite na mapu.")

st.divider()
col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("⚙️ Parametri")
    grana = st.radio("Grana:", ["Voćarstvo", "Povrtarstvo"])
    kultura = st.selectbox("Kultura:", ["Šljiva", "Jabuka", "Malina", "Paradajz", "Paprika"])
    detalj = st.selectbox("Faza:", ["Mladi zasad", "Pun rod", "Plastenik"])

    if st.button("Generiši plan"):
        with st.spinner("AI analizira..."):
            prompt = f"Agronom Srbija. {grana}: {kultura} ({detalj}). Maj. Temp: {temp}C. Daj 3 kratka zadatka sa preparatima. Lista."
            try:
                response = model.generate_content(prompt)
                if response.text:
                    st.session_state.zadaci = [z.strip() for z in response.text.strip().split('\n') if len(z) > 10][:3]
                else:
                    st.error("AI nije vratio odgovor.")
            except Exception as e:
                st.error(f"Greška: {e}")

with col_out:
    st.subheader("📋 Zadaci")
    if 'zadaci' in st.session_state:
        for zadatak in st.session_state.zadaci:
            if st.button(f"✅ Završeno: {zadatak}", use_container_width=True, key=zadatak):
                if korisnik != "Gost":
                    if posalji_u_tabelu(korisnik, zadatak):
                        st.success("Upisano!")
                    else:
                        st.error("Greška pri upisu.")
                else:
                    st.warning("Unesite ime levo.")
