import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="AgroAsistent AI Pro", layout="wide", page_icon="🤖")

# Rečnik meseci dostupan celoj aplikaciji
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

# --- 3. SESSION STATE (PAMĆENJE LOKACIJE) ---
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 44.01, 21.00

# --- 4. GLAVNI INTERFEJS ---
st.title("🚜 AgroAsistent AI: Pametni Agronom")
tabs = st.tabs(["📋 AI Dinamički Planer", "📍 Lokacija", "🍎 Voćarstvo", "🥦 Povrtarstvo", "💬 AI Chat"])

# --- TAB: LOKACIJA (Važno za prognozu) ---
with tabs[1]:
    st.header("📍 Podesi lokaciju svog imanja")
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=350, width=800, key="mapa_finalna")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.success(f"Lokacija ažurirana: {st.session_state.lat:.2f}, {st.session_state.lon:.2f}")

# --- TAB: AI DINAMIČKI PLANER (Glavna Automatizacija) ---
with tabs[0]:
    trenutni_mesec = datetime.now().month
    naziv_meseca = MESECI_NAZIVI[trenutni_mesec]
    
    st.header(f"📅 Planer za {naziv_meseca}")
    
    # Meteo podaci
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    meteo_tekst = "Vreme je uobičajeno."
    if meteo:
        st.info(f"🌤️ **Prognoza:** Max {meteo['max_t']}°C | Min {meteo['min_t']}°C | Padavine {meteo['kisa']}mm")
        meteo_tekst = f"Temperatura {meteo['max_t']} stepeni, padavine {meteo['kisa']}mm."

    # Izbor kulture
    kultura = st.selectbox("Izaberi kulturu za koju želiš AI plan:", 
                          ["Šljiva", "Malina", "Jabuka", "Paradajz", "Paprika", "Borovnica", "Vinova loza"])

    if st.button(f"✨ Generiši stručni plan za {kultura}", type="primary"):
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            prompt = f"""Ti si iskusni agronom u Srbiji. Napravi konkretan plan radova za {kultura} u mesecu {naziv_meseca}.
            Trenutni meteo uslovi: {meteo_tekst}.
            Navedi 4 ključna zadatka. Za svaki zadatak preporuči konkretno zaštitno sredstvo (preparat) ili vrstu đubriva koja se koristi u Srbiji.
            Formatiraj odgovor ovako:
            Zadatak 1 | Detaljan opis i naziv preparata
            Zadatak 2 | Detaljan opis i naziv preparata"""

            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            with st.spinner("AI agronom analizira podatke..."):
                try:
                    r = requests.post(url, json=payload, timeout=20).json()
                    odgovor = r["candidates"][0]["content"]["parts"][0]["text"]
                    
                    st.subheader(f"✅ Tvoji zadaci za {kultura}:")
                    linije = odgovor.split('\n')
                    for i, linija in enumerate(linije):
                        if "|" in linija:
                            zadatak, detalj = linija.split("|")
                            col_c, col_t = st.columns([1, 10])
                            with col_c:
                                st.checkbox("", key=f"ai_task_{i}")
                            with col_t:
                                st.markdown(f"**{zadatak.strip()}**")
                                st.write(detalj.strip())
                except:
                    st.error("Došlo je do greške u komunikaciji sa AI modelom.")
        else:
            st.warning("Molimo podesite API ključ u Secrets (GEMINI_API_KEY).")

# --- OSTALI TABOVI (Katalog znanja) ---
with tabs[2]:
    st.write("Ovde možete držati opšte savete o sortama voća.")
with tabs[3]:
    st.write("Ovde možete držati opšte savete o povrtarstvu.")
with tabs[4]:
    st.header("💬 Pitaj bilo šta")
    user_pitanje = st.text_input("Postavi pitanje agronomu:")
    if st.button("Pošalji"):
        # Logika za chat (slična onoj u planeru)
        st.write("AI odgovara na osnovu vašeg pitanja...")

st.divider()
st.caption("AgroAsistent v2.0 - Automatizovano pomoću AI tehnologije")
