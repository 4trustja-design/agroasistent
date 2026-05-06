import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="AgroAsistent AI Pro", layout="wide", page_icon="🤖")

MESECI_NAZIVI = {1:"Januar", 2:"Februar", 3:"Mart", 4:"April", 5:"Maj", 6:"Jun", 
                 7:"Jul", 8:"Avgust", 9:"Septembar", 10:"Oktobar", 11:"Novembar", 12:"Decembar"}

# --- 2. POMOĆNE FUNKCIJE ---
def dobij_prognozu(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    try:
        r = requests.get(url, timeout=10).json()
        return {
            "max_t": r['daily']['temperature_2m_max'][0],
            "min_t": r['daily']['temperature_2m_min'][0],
            "kisa": r['daily']['precipitation_sum'][0]
        }
    except:
        return None

# --- 3. SESSION STATE ---
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 44.01, 21.00

# --- 4. GLAVNI INTERFEJS ---
st.title("🚜 AgroAsistent AI: Pametni Agronom")
tabs = st.tabs(["📋 AI Planer", "📍 Lokacija", "🍎 Voćarstvo", "🥦 Povrtarstvo", "💬 AI Chat"])

# --- TAB 1: LOKACIJA ---
with tabs[1]:
    st.header("📍 Podesi lokaciju imanja")
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=350, width=800, key="mapa_finalna")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.success("Lokacija ažurirana!")

# --- TAB 0: AI DINAMIČKI PLANER ---
with tabs[0]:
    trenutni_mesec = datetime.now().month
    naziv_meseca = MESECI_NAZIVI[trenutni_mesec]
    st.header(f"📅 Planer za {naziv_meseca}")
    
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    meteo_tekst = "Vreme je uobičajeno."
    if meteo:
        st.info(f"🌤️ Prognoza: Max {meteo['max_t']}°C | Padavine {meteo['kisa']}mm")
        meteo_tekst = f"Temperatura {meteo['max_t']} stepeni, padavine {meteo['kisa']}mm."

    kultura = st.selectbox("Izaberi kulturu:", ["Šljiva", "Malina", "Jabuka", "Paradajz", "Paprika"])

    if st.button(f"✨ Generiši stručni plan", type="primary"):
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            prompt = f"Ti si agronom u Srbiji. Napravi plan za {kultura} u mesecu {naziv_meseca}. Vreme: {meteo_tekst}. Navedi 4 zadatka sa preparatima. Format: Zadatak | Opis"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            with st.spinner("AI analizira..."):
                try:
                    res = requests.post(url, json=payload, timeout=20)
                    data = res.json()
                    if "candidates" in data:
                        odgovor = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.subheader(f"✅ Zadaci za {kultura}:")
                        for i, linija in enumerate(odgovor.strip().split('\n')):
                            if "|" in linija:
                                zadatak, detalj = linija.split("|")
                                col_c, col_t = st.columns([1, 10])
                                with col_c: st.checkbox("", key=f"ai_task_{i}")
                                with col_t: st.markdown(f"**{zadatak.strip()}** - {detalj.strip()}")
                    else:
                        st.error("Problem sa API ključem ili kvotom.")
                except:
                    st.error("Greška u povezivanju.")
        else:
            st.warning("Dodajte GEMINI_API_KEY u Secrets.")

# --- OSTALI TABOVI ---
with tabs[2]: st.write("Saveti za voće u pripremi...")
with tabs[3]: st.write("Saveti za povrće u pripremi...")
with tabs[4]: 
    st.header("💬 AI Chat")
    pitanje = st.text_input("Pitaj agronoma:")
    if st.button("Pošalji"):
        st.write("AI odgovor će se pojaviti ovde.")
