import streamlit as st
from google import genai
import folium
from streamlit_folium import st_folium
import requests
import time

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="AgroSmart Srbija", layout="wide")

if "GEMINI_API_KEY" not in st.secrets:
    st.error("Nedostaje API ključ u Secrets!")
    st.stop()

# Pravljenje klijenta
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSccBzwQSmytB6TSzYLmcj429FiWMVGm7WUTUi5GqZZUHV6C_g/formResponse"

# --- 2. FUNKCIJE ---
def posalji_u_tabelu(ime, radnja):
    payload = {"entry.880598687": ime, "entry.31175628": radnja, "entry.1741593922": "Obavljeno"}
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

# --- 3. UI ---
with st.sidebar:
    st.header("👤 Profil")
    korisnik = st.text_input("Ime / ID:", "Gost")
    st.divider()
    st.write("📊 [Tabela radova](https://docs.google.com/spreadsheets/d/1DU-w1I6yMuLIq9qQYhMGxdWds9dvaG9QlezJs87vExk/edit)")

st.title(f"🚜 AgroAsistent: {korisnik}")

c1, c2 = st.columns([2, 1])
with c1:
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=300, use_container_width=True, key="agro_map_v6")
    lat, lon = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng']) if map_data and map_data.get('last_clicked') else (44.0165, 21.0059)

with c2:
    st.subheader("🌦️ Prognoza")
    temp, kisa = dobij_vreme(lat, lon)
    if temp is not None:
        st.metric("Temperatura", f"{temp}°C")
        st.metric("Padavine", f"{kisa}mm")

st.divider()
col_in, col_out = st.columns([1, 2])

with col_in:
    grana = st.radio("Grana:", ["Voćarstvo", "Povrtarstvo"])
    kultura = st.selectbox("Kultura:", ["Šljiva", "Jabuka", "Malina", "Paradajz", "Paprika"])
    detalj = st.selectbox("Faza:", ["Mladi zasad", "Pun rod", "Plastenik"])

    if st.button("Generiši plan radova", type="primary"):
        with st.spinner("Konsultujem agronoma..."):
            prompt = f"Agronom Srbija. {grana}: {kultura} ({detalj}). Maj. Temp:{temp}C. Daj 3 kratka zadatka sa preparatima. Lista."
            
            try:
                # Koristimo 1.5-flash jer on ima NAJVEĆU besplatnu kvotu
                response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
                
                if response and response.text:
                    st.session_state.zadaci = [z.strip() for z in response.text.strip().split('\n') if len(z) > 5][:3]
                else:
                    st.error("AI nije vratio tekst. Pokušajte ponovo.")
            except Exception as e:
                if "429" in str(e):
                    st.error("⌛ Kvota je potrošena. Sačekajte 30 sekundi pa kliknite ponovo.")
                else:
                    st.error(f"Greška: {e}")

with col_out:
    st.subheader("📋 Zadaci")
    if 'zadaci' in st.session_state:
        for zadatak in st.session_state.zadaci:
            if st.button(f"✅ Završeno: {zadatak}", use_container_width=True, key=zadatak):
                if korisnik != "Gost":
                    if posalji_u_tabelu(korisnik, zadatak):
                        st.toast("Zapisano!")
                else:
                    st.warning("Unesite ime levo.")
