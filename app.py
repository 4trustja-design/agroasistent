import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from google import genai  # Nova biblioteka
import requests

# --- 1. KONFIGURACIJA AI ---
# Inicijalizujemo klijenta samo ako postoji ključ, inače AI deo preskačemo
client = None
if "GEMINI_API_KEY" in st.secrets:
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except:
        pass

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

# --- 2. TVOJA BAZA PODATAKA (Nepromenjena) ---
vocarstvo_data = {
    "Šljiva": {
        "1. Godina": "Sadnja u jesen, skraćivanje sadnice na 80cm.",
        "Zaštita": "Plavo prskanje u fazi mirovanja.",
        "Prehrana": "Unos stajnjaka ili NPK 15:15:15 pre sadnje."
    },
    "Malina": {
        "1. Godina": "Postavljanje naslona, đubrenje azotnim đubrivima u proleće.",
        "Zaštita": "Tretman protiv didimele nakon kretanja vegetacije."
    }
}

povrtarstvo_data = {
    "Paradajz": {
        "Plastenik": "Sadnja rasada u aprilu, sistem kap po kap.",
        "Otvoreno": "Sadnja krajem maja, razmak 50cm.",
        "Zaštita": "Tretman protiv plamenjače nakon svake jače kiše.",
        "Prehrana": "Prihrana kalijumom u fazi formiranja plodova."
    }
}

# --- 3. GLAVNI INTERFEJS ---
st.title("🚜 AgroAsistent: Voćarstvo & Povrtarstvo")

# --- SIDEBAR: AI AGRONOM (Direktna metoda) ---
with st.sidebar:
    st.header("🤖 AI Konsultacije")
    pitanje = st.text_input("Pitajte AI agronoma:", placeholder="npr. Čime prskati jabuku?")
    
    if st.button("Pitaj AI"):
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            # Direktan URL ka Google API-ju (zaobilazimo biblioteku)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"Ti si stručni agronom u Srbiji. Odgovori kratko: {pitanje}"}]
                }]
            }
            
            with st.spinner("AI razmišlja..."):
                try:
                    res = requests.post(url, json=payload, timeout=15)
                    data = res.json()
                    
                    if "candidates" in data:
                        odgovor = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.info(odgovor)
                    else:
                        # Ako Google vrati grešku, ispiši je precizno
                        st.error(f"Google API Greška: {data.get('error', {}).get('message', 'Nepoznata greška')}")
                except Exception as e:
                    st.error(f"Sistemska greška: {e}")
        else:
            st.warning("API ključ nije podešen.")

# --- TVOJI TABS (Nepromenjeno) ---
tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Moja Lokacija & Vreme"])

with tab1:
    st.header("Saveti za voćare")
    voce = st.selectbox("Izaberite voćnu vrstu:", list(vocarstvo_data.keys()))
    godina = st.select_slider("Godina zasada:", options=["1. Godina", "2. Godina", "3. Godina", "4. Godina", "5. Godina"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠 Radovi i Sadnja")
        st.write(vocarstvo_data[voce].get(godina, "Nema specifičnih saveta za ovu godinu."))
    
    with col2:
        st.subheader("🛡 Zaštita i 🧪 Prehrana")
        st.write(vocarstvo_data[voce]["Zaštita"])
        st.write(vocarstvo_data[voce]["Prehrana"])

with tab2:
    st.header("Saveti za povrtare")
    povrce = st.selectbox("Izaberite povrće:", list(povrtarstvo_data.keys()))
    tip_uzgoja = st.radio("Tip proizvodnje:", ["Plastenik", "Otvoreno"])
    st.subheader("📋 Plan proizvodnje")
    st.write(povrtarstvo_data[povrce][tip_uzgoja])

with tab3:
    st.header("📍 Lokacija i Vremenska Prognoza")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=400, width=800, key="stable_map")

    if map_data and map_data.get('last_clicked'):
        lat = map_data['last_clicked']['lat']
        lng = map_data['last_clicked']['lng']
        st.success(f"Lokacija: {lat:.2f}, {lng:.2f}")
