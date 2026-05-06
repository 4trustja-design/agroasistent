import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. POSTAVKE APLIKACIJE ---
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide", page_icon="🚜")

# --- 2. DINAMIČKA BAZA RADOVA PO MESECIMA (TO-DO) ---
sveobuhvatni_planovi = {
    5: { # MAJ
        "Šljiva": [
            {"id": "slj_maj_1", "zadatak": "Zaštita protiv šupljikavosti lista (Captan)", "tip": "Zaštita"},
            {"id": "slj_maj_2", "zadatak": "Prihrana preko lista (Bor + Aminokiseline)", "tip": "Prehrana"},
            {"id": "slj_maj_3", "zadatak": "Uklanjanje korova unutar reda", "tip": "Radovi"}
        ],
        "Malina": [
            {"id": "mal_maj_1", "zadatak": "Tretman protiv didimele i rđe (Quadris)", "tip": "Zaštita"},
            {"id": "mal_maj_2", "zadatak": "Druga prihrana KAN đubrivom", "tip": "Prehrana"},
            {"id": "mal_maj_3", "zadatak": "Zakidanje prvih mladih izdanaka", "tip": "Radovi"}
        ],
        "Paradajz": [
            {"id": "par_maj_1", "zadatak": "Preventiva plamenjače (Ridomil Gold)", "tip": "Zaštita"},
            {"id": "par_maj_2", "zadatak": "Prihrana 20:20:20 kroz sistem", "tip": "Prehrana"},
            {"id": "par_maj_3", "zadatak": "Zalamanje zaperaka redovno", "tip": "Radovi"}
        ]
    },
    6: { # JUN
        "Šljiva": [
            {"id": "slj_jun_1", "zadatak": "Zaštita protiv šljivine ose i smotavca", "tip": "Zaštita"},
            {"id": "slj_jun_2", "zadatak": "Folijarna prihrana kalcijumom", "tip": "Prehrana"}
        ],
        "Malina": [
            {"id": "mal_jun_1", "zadatak": "Zaštita protiv truleži ploda (Botritis)", "tip": "Zaštita"},
            {"id": "mal_jun_2", "zadatak": "Berba i klasiranje plodova", "tip": "Radovi"}
        ],
        "Paradajz": [
            {"id": "par_jun_1", "zadatak": "Vezivanje stabljika uz naslon", "tip": "Radovi"},
            {"id": "par_jun_2", "zadatak": "Prihrana kalijumom za zrenje", "tip": "Prehrana"}
        ]
    }
}

# --- 3. INICIJALIZACIJA MEMORIJE (Za zaključavanje zadataka) ---
if 'zavrseni_zadaci' not in st.session_state:
    st.session_state.zavrseni_zadaci = set()

# --- 4. OSNOVNI PODACI (Tvoja stabilna baza) ---
vocarstvo_data = {
    "Šljiva": {"Opšte": "Gajenje šljive zahteva duboka, propusna zemljišta.", "Zimski_radovi": "Rezidba u fazi mirovanja."},
    "Malina": {"Opšte": "Najbolje uspeva na nadmorskim visinama preko 400m.", "Zimski_radovi": "Vezivanje izdanaka za žicu."}
}

# --- 5. GLAVNI INTERFEJS ---
st.title("🚜 AgroAsistent: Vaš Digitalni Agronom")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🍎 Voćarstvo", 
    "🥦 Povrtarstvo", 
    "📅 Mesečni Plan (To-Do)", 
    "📍 Lokacija", 
    "🤖 AI Savetnik"
])

# --- TAB 1 & 2: FIKSNI SAVETI ---
with tab1:
    st.header("Saveti za voćare")
    voce = st.selectbox("Vrsta:", list(vocarstvo_data.keys()))
    st.write(vocarstvo_data[voce]["Opšte"])

with tab2:
    st.header("Saveti za povrtare")
    st.write("Ovde možete dodati vaše fiksne savete za povrtarstvo.")

# --- TAB 3: DINAMIČKI PLAN RADOVA (TO-DO) ---
with tab3:
    mesec_broj = datetime.now().month
    meseci_imena = {1:"Januar", 2:"Februar", 3:"Mart", 4:"April", 5:"Maj", 6:"Jun", 
                    7:"Jul", 8:"Avgust", 9:"Septembar", 10:"Oktobar", 11:"Novembar", 12:"Decembar"}
    
    st.header(f"📅 Plan radova za {meseci_imena[mesec_broj]}")
    
    plan_za_mesec = sveobuhvatni_planovi.get(mesec_broj, {})
    
    if not plan_za_mesec:
        st.info("Nema definisanih radova za ovaj mesec.")
    else:
        kultura_plan = st.selectbox("Izaberite kulturu za planer:", list(plan_za_mesec.keys()))
        zadaci = plan_za_mesec.get(kultura_plan, [])
        
        for stavka in zadaci:
            is_done = stavka["id"] in st.session_state.zavrseni_zadaci
            
            c1, c2 = st.columns([1, 10])
            with c1:
                # Checkbox se zaključava (disabled) ako je već jednom čekiran
                if st.checkbox("", key=stavka["id"], value=is_done, disabled=is_done):
                    st.session_state.zavrseni_zadaci.add(stavka["id"])
                    st.rerun()
            
            with c2:
                if is_done:
                    st.write(f"✅ ~~{stavka['zadatak']}~~ (Završeno)")
                else:
                    boja = "orange" if stavka["tip"] == "Zaštita" else "green"
                    st.markdown(f"**{stavka['zadatak']}** - *{stavka['tip']}*")

# --- TAB 4: LOKACIJA ---
with tab4:
    st.header("📍 Lokacija imanja")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    m.add_child(folium.LatLngPopup())
    st_folium(m, height=400, width=800, key="agro_map_vFinal")

# --- TAB 5: AI SAVETNIK (Direktna metoda) ---
with tab5:
    st.header("🤖 Pitajte AI Agronoma")
    upit = st.text_area("Vaše pitanje:", placeholder="Npr: Zašto lišće maline dobija žute fleke?")
    
    if st.button("Pošalji AI upit", type="primary"):
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": f"Ti si stručni agronom u Srbiji. Odgovori stručno: {upit}"}]}]}
            
            with st.spinner("AI analizira..."):
                try:
                    res = requests.post(url, json=payload, timeout=20)
                    data = res.json()
                    odgovor = data["candidates"][0]["content"]["parts"][0]["text"]
                    st.info(odgovor)
                except:
                    st.error("AI servis je trenutno preopterećen. Pokušajte malo kasnije.")
        else:
            st.warning("Dodajte GEMINI_API_KEY u Secrets.")

st.markdown("---")
st.caption(f"AgroAsistent 2026 | Trenutni mesec: {meseci_imena[mesec_broj]}")
