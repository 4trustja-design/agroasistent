import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
import requests
import io
from PIL import Image
import base64

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

if 'dnevnik' not in st.session_state: st.session_state.dnevnik = []
if 'troskovi' not in st.session_state: st.session_state.troskovi = []

st.title("🌿 AgroAsistent: Digitalni Savetnik i AI Dijagnoza")

# 2. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    ai_key = st.text_input("Unesi Google Gemini API Ključ:", type="password", help="Potreban za prepoznavanje bolesti sa slike.")
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    st.markdown("---")
    datum_sadnje = st.date_input("Datum sadnje rasada:", datetime.now())

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🍎 Voćnjak", "🥦 Povrtarstvo", "📍 Radar i Savet", "💰 Troškovnik", "📸 Foto Dijagnoza"])

# --- FUNKCIJA ZA AI PREPOZNAVANJE SLIKE ---
def analiziraj_list(image_file, api_key):
    # Pretvaranje slike u format koji AI razume
    img = Image.open(image_file)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    url = f"https://googleapis.com{api_key.strip()}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = "Kao agronom, analiziraj ovu sliku lista biljke. Reci mi: 1. Koja je bolest ili štetočina u pitanju? 2. Koji su ORGANSKI lekovi (soda, mleko, ulja)? 3. Koja je hitna hemijska zaštita sa kratkom karentom?"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_str}}
            ]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Greška AI servera: {response.text}"
    except Exception as e:
        return f"Greška u povezivanju: {str(e)}"

# --- TABOVI 1, 2, 3, 4 (Ostaju isti kao u prethodnom kodu, ovde su skraćeni radi preglednosti) ---
with tab1: st.write("Saveti za voćnjak su u funkciji.") # Ovde ide tvoj stari kod za tab1
with tab2: st.write("Saveti za povrće su u funkciji.") # Ovde ide tvoj stari kod za tab2
with tab3: st.write("Radar i meteo alarm su u funkciji.") # Ovde ide tvoj stari kod za tab3
with tab4: st.write("Troškovnik je u funkciji.") # Ovde ide tvoj stari kod za tab4

# --- TAB 5: AI FOTO DIJAGNOZA ---
with tab5:
    st.header("📸 AI Prepoznavanje bolesti")
    st.write("Uslikaj bolesni list ili postavi sliku iz galerije:")
    
    upozorenje_za_kljuc = ""
    if not ai_key:
        st.warning("⚠️ Da bi ovo radilo, moraš uneti Google Gemini API ključ u meni sa leve strane!")
    
    izvor_slike = st.radio("Izaberi izvor:", ["Kamera telefona", "Postavi sliku"])
    
    if izvor_slike == "Kamera telefona":
        slika = st.camera_input("Uslikaj list")
    else:
        slika = st.file_uploader("Izaberi sliku iz galerije", type=['jpg', 'jpeg', 'png'])

    if slika is not None and ai_key:
        if st.button("🔍 Analiziraj list"):
            with st.spinner("AI Agronom pregleda sliku..."):
                rezultat = analiziraj_list(slika, ai_key)
                st.markdown("### 📋 Rezultat analize:")
                st.write(rezultat)
                
                # Mogućnost da se nalaz sačuva u dnevnik
                if st.button("💾 Zapiši nalaz u dnevnik"):
                    st.session_state.dnevnik.append({
                        "Datum": datetime.now().strftime("%d.%m."),
                        "Kultura": "AI Dijagnoza",
                        "Radovi": "Analiza lista - detektovan problem"
                    })
                    st.success("Nalaz zabeležen!")

# --- FINALNI EKSPORT (Spajanje svega u jedan Excel) ---
# ... (Koristi onaj kod sa dva Sheet-a koji smo poslednji dogovorili)
