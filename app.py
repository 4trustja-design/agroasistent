import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. POSTAVKE ---
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

# --- 2. PROŠIRENA BAZA PODATAKA ZA TO-DO (MAJ) ---
# Ovde definišemo zadatke samo za Maj
mesecni_planovi = {
    "Šljiva": [
        {"id": "slj_1", "zadatak": "Zaštita protiv šupljikavosti lista (npr. Captan)", "tip": "Zaštita"},
        {"id": "slj_2", "zadatak": "Prihrana preko lista (Bor + Aminokiseline)", "tip": "Prehrana"},
        {"id": "slj_3", "zadatak": "Uklanjanje korova unutar reda", "tip": "Radovi"}
    ],
    "Malina": [
        {"id": "mal_1", "zadatak": "Tretman protiv didimele i rđe (npr. Quadris)", "tip": "Zaštita"},
        {"id": "mal_2", "zadatak": "Druga prihrana KAN đubrivom (pred cvetanje)", "tip": "Prehrana"},
        {"id": "mal_3", "zadatak": "Zakidanje prvih mladih izdanaka", "tip": "Radovi"}
    ],
    "Paradajz": [
        {"id": "par_1", "zadatak": "Preventiva protiv plamenjače (npr. Ridomil)", "tip": "Zaštita"},
        {"id": "par_2", "zadatak": "Prihrana formulacijom 20:20:20 (kap po kap)", "tip": "Prehrana"},
        {"id": "par_3", "zadatak": "Zalamanje zaperaka", "tip": "Radovi"}
    ]
}

# Inicijalizacija baze završenih zadataka u memoriji (Session State)
if 'zavrseni_zadaci' not in st.session_state:
    st.session_state.zavrseni_zadaci = set()

# --- 3. INTERFEJS ---
st.title("🚜 AgroAsistent: Pametni Planer")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🍎 Voćarstvo", 
    "🥦 Povrtarstvo", 
    "📅 Mesečni Plan (MAJ)", 
    "📍 Lokacija", 
    "🤖 AI Savetnik"
])

# (Tabovi 1, 2 i 4 ostaju isti kao u tvom kodu...)

# --- NOVI TAB: MESEČNI PLAN (TO-DO) ---
with tab3:
    st.header(f"📅 Plan radova za: MAJ")
    izbor_kulture = st.selectbox("Izaberite kulturu za plan:", ["Šljiva", "Malina", "Paradajz"])
    
    plan = mesecni_planovi.get(izbor_kulture, [])
    
    if plan:
        st.subheader(f"Lista zadataka za {izbor_kulture}")
        for stavka in plan:
            # Proveravamo da li je zadatak već završen
            is_done = stavka["id"] in st.session_state.zavrseni_zadaci
            
            # Kreiramo kolone za checkbox i opis
            col_check, col_text = st.columns([1, 10])
            
            with col_check:
                # Checkbox koji se onemogućava (disabled) ako je već čekiran
                if st.checkbox("", key=stavka["id"], value=is_done, disabled=is_done):
                    st.session_state.zavrseni_zadaci.add(stavka["id"])
                    st.rerun() # Osvežava stranu da zaključa status
            
            with col_text:
                if is_done:
                    st.write(f"✅ ~~{stavka['zadatak']}~~ (Završeno)")
                else:
                    color = "orange" if stavka["tip"] == "Zaštita" else "green"
                    st.markdown(f"**{stavka['zadatak']}** - *{stavka['tip']}*")
    else:
        st.info("Nema definisanog plana za izabranu kulturu.")

# --- TAB 5: AI SAVETNIK (Direktna metoda) ---
with tab5:
    st.header("🤖 Pitajte AI Agronoma")
    pitanje = st.text_area("Vaše pitanje:", placeholder="Npr: Čime prskati jabuku u maju?")
    if st.button("Pošalji upit", type="primary"):
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": f"Ti si stručni agronom u Srbiji. Odgovori kratko: {pitanje}"}]}]}
            with st.spinner("AI analizira..."):
                try:
                    res = requests.post(url, json=payload, timeout=20)
                    odgovor = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    st.info(odgovor)
                except:
                    st.error("AI trenutno nije dostupan.")
