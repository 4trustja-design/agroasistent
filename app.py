import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from datetime import datetime
import requests
import pandas as pd

# --- KONFIGURACIJA ---
# ZAMENI OVE PODATKE SVOJIM LINKOVIMA
GOOGLE_FORM_URL = "OVDE_ZALEPI_LINK_TVOJE_FORME/formResponse"
# Primer entry ID-jeva (ovo ćemo podesiti kad mi pošalješ link forme)
# entry.12345 = Korisnik, entry.67890 = Akcija

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Greška sa AI ključem: {e}")

# Funkcija za slanje podataka u tvoju tabelu
def zapisi_u_tabelu(ime, radnja):
    # Formiramo podatke za Google Formu
    payload = {
        "entry.12345678": ime,   # Ovo ćemo zameniti tvojim ID-jevima
        "entry.87654321": radnja,
        "entry.11223344": "Obavljeno"
    }
    try:
        requests.post(GOOGLE_FORM_URL, data=payload)
        return True
    except:
        return False

# --- POMOĆNE FUNKCIJE ---
def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=precipitation_sum&timezone=auto"
    try:
        res = requests.get(url).json()
        return res['current_weather']['temperature'], res['daily']['precipitation_sum'][0]
    except: return None, None

def ai_agronom(kultura, starost, temp, kisa):
    prompt = f"Kao agronom, daj 3 kratka zadatka za {kultura} ({starost}) za maj mesec. Temp: {temp}C, kisa: {kisa}mm. Odgovori u formatu: 1. [zadatak] 2. [zadatak]"
    try:
        odgovor = model.generate_content(prompt).text
        return [linija.strip() for linija in odgovor.split('\n') if len(linija) > 5][:3]
    except: return ["AI trenutno odmara..."]

# --- UI ---
st.set_page_config(page_title="AgroSmart Srbija", layout="wide")

# Bočna traka za korisnike
with st.sidebar:
    st.header("👤 Profil")
    moje_ime = st.text_input("Unesite vaše ime (ID):", "Gost")
    st.info("Svaki korisnik unosi svoje ime da bi mu se radovi odvojeno beležili.")

st.title(f"🚜 AgroAsistent za: {moje_ime}")

# Mapa i Prognoza
col1, col2 = st.columns([2, 1])
with col1:
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    m.add_child(folium.LatLngPopup())
    mapa = st_folium(m, height=300, use_container_width=True)
    lat, lon = (mapa['last_clicked']['lat'], mapa['last_clicked']['lng']) if mapa['last_clicked'] else (44.0165, 21.0059)

with col2:
    t, k = get_weather(lat, lon)
    if t:
        st.metric("Trenutna Temp", f"{t}°C")
        st.metric("Padavine danas", f"{k}mm")

st.divider()

# Generisanje i Čekiranje
c1, c2 = st.columns(2)
with c1:
    st.subheader("📋 Preporuka za vaše imanje")
    biljka = st.text_input("Šta gajite?", "Šljiva")
    starost = st.text_input("Faza/Starost:", "2 godine")
    
    if st.button("Prikaži plan radova"):
        st.session_state.zadaci = ai_agronom(biljka, starost, t, k)

    if 'zadaci' in st.session_state:
        for z in st.session_state.zadaci:
            if st.button(f"✅ Završio sam: {z}"):
                if moje_ime != "Gost":
                    uspeh = zapisi_u_tabelu(moje_ime, z)
                    st.toast(f"Sačuvano u tabelu za: {moje_ime}!")
                else:
                    st.warning("Prijavite se (unesite ime) da bi se rad sačuvao.")

with c2:
    st.subheader("📊 Vaša istorija (Live)")
    st.write(f"Ovde će se pojaviti link ka tvojoj tabeli da svi mogu da vide: [Pogledaj tabelu](https://docs.google.com/spreadsheets/d/1DU-w1I6yMuLIq9qQYhMGxdWds9dvaG9QlezJs87vExk/edit)")
