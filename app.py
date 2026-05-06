import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="AgroAsistent Pro", layout="wide")

# --- 2. BAZA RADOVA ---
sveobuhvatni_planovi = {
    1: {"Šljiva": [{"id":"slj_1","zadatak":"Zimska rezidba","tip":"Rad"}],"Malina":[{"id":"mal_1","zadatak":"Sneg na mrežama","tip":"Rad"}],"Paradajz":[{"id":"par_1","zadatak":"Nabavka semena","tip":"Priprema"}]},
    2: {"Šljiva": [{"id":"slj_2","zadatak":"Plavo ulje","tip":"Zaštita"}],"Malina":[{"id":"mal_2","zadatak":"Rezidba dvorodnih","tip":"Rad"}],"Paradajz":[{"id":"par_2","zadatak":"Setva rasada","tip":"Rad"}]},
    3: {"Šljiva": [{"id":"slj_3","zadatak":"NPK đubrenje","tip":"Prehrana"}],"Malina":[{"id":"mal_3","zadatak":"Vezivanje","tip":"Rad"}],"Paradajz":[{"id":"par_3","zadatak":"Pikiranje","tip":"Rad"}]},
    4: {"Šljiva": [{"id":"slj_4","zadatak":"Monilija (cvet)","tip":"Zaštita"}],"Malina":[{"id":"mal_4","zadatak":"Didimela","tip":"Zaštita"}],"Paradajz":[{"id":"par_4","zadatak":"Kaljenje","tip":"Priprema"}]},
    5: {"Šljiva": [{"id":"slj_5","zadatak":"Vaši i šupljikavost","tip":"Zaštita"}],"Malina":[{"id":"mal_5","zadatak":"Zakidanje izdanaka","tip":"Rad"}],"Paradajz":[{"id":"par_5","zadatak":"Sadnja na polje","tip":"Rad"}]},
    6: {"Šljiva": [{"id":"slj_6","zadatak":"Smotavac","tip":"Zaštita"}],"Malina":[{"id":"mal_6","zadatak":"Botritis","tip":"Zaštita"}],"Paradajz":[{"id":"par_6","zadatak":"Zalamanje zaperaka","tip":"Rad"}]},
    7: {"Šljiva": [{"id":"slj_7","zadatak":"Navodnjavanje","tip":"Rad"}],"Malina":[{"id":"mal_7","zadatak":"Berba","tip":"Rad"}],"Paradajz":[{"id":"par_7","zadatak":"Kalijum","tip":"Prehrana"}]},
    8: {"Šljiva": [{"id":"slj_8","zadatak":"Berba","tip":"Rad"}],"Malina":[{"id":"mal_8","zadatak":"Stari izdanci","tip":"Rad"}],"Paradajz":[{"id":"par_8","zadatak":"Plamenjača","tip":"Zaštita"}]},
    9: {"Šljiva": [{"id":"slj_9","zadatak":"Sakupljanje plodova","tip":"Rad"}],"Malina":[{"id":"mal_9","zadatak":"Fosfor i kalijum","tip":"Prehrana"}],"Paradajz":[{"id":"par_9","zadatak":"Sakupljanje semena","tip":"Rad"}]},
    10: {"Šljiva": [{"id":"slj_10","zadatak":"Stajnjak","tip":"Prehrana"}],"Malina":[{"id":"mal_10","zadatak":"Priprema naslona","tip":"Rad"}],"Paradajz":[{"id":"par_10","zadatak":"Čišćenje bašte","tip":"Rad"}]},
    11: {"Šljiva": [{"id":"slj_11","zadatak":"Jesenja sadnja","tip":"Rad"}],"Malina":[{"id":"mal_11","zadatak":"Plavo prskanje","tip":"Zaštita"}],"Paradajz":[{"id":"par_11","zadatak":"Duboko oranje","tip":"Rad"}]},
    12: {"Šljiva": [{"id":"slj_12","zadatak":"Krečenje stabala","tip":"Rad"}],"Malina":[{"id":"mal_12","zadatak":"Kontrola ograde","tip":"Rad"}],"Paradajz":[{"id":"par_12","zadatak":"Plan plodoreda","tip":"Priprema"}]}
}

# --- 3. POMOĆNE FUNKCIJE ---
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

# --- 4. SESSION STATE ---
if 'zavrseni_zadaci' not in st.session_state:
    st.session_state.zavrseni_zadaci = set()
if 'lat' not in st.session_state:
    st.session_state.lat, st.session_state.lon = 44.01, 21.00

# --- 5. UI ---
st.title("🚜 AgroAsistent Pro")
tabs = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📅 Plan", "📍 Lokacija", "🤖 AI"])

with tabs[3]: # LOKACIJA
    st.header("📍 Lokacija")
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=350, width=800, key="mapa_v10")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.success("Lokacija ažurirana!")

with tabs[2]: # PLAN
    mesec = datetime.now().month
    meseci = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Maj",6:"Jun",7:"Jul",8:"Avg",9:"Sep",10:"Okt",11:"Nov",12:"Dec"}
    st.header(f"📅 Plan: {meseci[mesec]}")

    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    if meteo:
        c1, c2, c3 = st.columns(3)
        c1.metric("Max", f"{meteo['max_t']}°C")
        c2.metric("Min", f"{meteo['min_t']}°C")
        c3.metric("Kiša", f"{meteo['kisa']}mm")
        
        if meteo['max_t'] > 32:
            st.warning("⚠️ VRUĆINA: Zalivajte rano ujutru.")
        if meteo['min_t'] < 2:
            st.error("❄️ MRAZ: Zaštitite osetljive biljke!")
        if meteo['kisa'] > 10:
            st.info("🌧️ KIŠA: Odložite prskanje.")

    st.divider()
    plan = sveobuhvatni_planovi.get(mesec, {})
    izbor = st.selectbox("Izaberi kulturu:", list(plan.keys()))
    zadaci = plan.get(izbor, [])

    for z in zadaci:
        key = f"{z['id']}_{mesec}"
        is_done = key in st.session_state.zavrseni_zadaci
        col_c, col_t = st.columns([1, 10])
        with col_c:
            if st.checkbox("", key=key, value=is_done, disabled=is_done):
                st.session_state.zavrseni_zadaci.add(key)
                st.rerun()
        with col_t:
            if is_done:
                st.write(f"✅ ~~{z['zadatak']}~~")
            else:
                st.write(f"**{z['zadatak']}** ({z['tip']})")

with tabs[4]: # AI
    st.header("🤖 AI Savetnik")
    pitanje = st.text_input("Pitanje:")
    if st.button("Pitaj"):
        if "GEMINI_API_KEY" in st.secrets:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={st.secrets['GEMINI_API_KEY']}"
            payload = {"contents": [{"parts": [{"text": f"Kratak agro savet: {pitanje}"}]}]}
            try:
                r = requests.post(url, json=payload, timeout=15).json()
                st.info(r["candidates"][0]["content"]["parts"][0]["text"])
            except:
                st.error("AI nije dostupan.")

# --- POPUNJAVANJE TABOVA PODACIMA ---

with tabs[0]: # 🍎 Voćarstvo
    st.header("Saveti za voćare")
    vocarstvo_detalji = {
        "Šljiva": {
            "Opis": "Šljiva zahteva duboka i propusna zemljišta. Najbolje uspeva na blagim nagibima.",
            "Sadnja": "Sadnja se obavlja u jesen ili rano proleće na razmak 5x4m.",
            "Zanimljivost": "Srbija je jedan od najvećih svetskih proizvođača šljive."
        },
        "Malina": {
            "Opis": "Malina traži dosta vlage i specifičnu mikroklimu.",
            "Sadnja": "Sadi se u redove sa naslonom (žicom) na razmak 2.5x0.3m.",
            "Zanimljivost": "Sorta Willamette je najzastupljenija u našim krajevima."
        }
    }
    
    izbor_voce = st.selectbox("Izaberi voćnu vrstu za detalje:", list(vocarstvo_detalji.keys()))
    v = vocarstvo_detalji[izbor_voce]
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.subheader("📖 Opšte informacije")
        st.write(v["Opis"])
    with col_v2:
        st.subheader("🌱 Saveti za sadnju")
        st.write(v["Sadnja"])
    st.info(f"💡 {v['Zanimljivost']}")

with tabs[1]: # 🥦 Povrtarstvo
    st.header("Saveti za povrtare")
    povrce_detalji = {
        "Paradajz": {
            "Tip": "Plastenik i Otvoreno polje",
            "Savet": "Obavezno zakidanje zaperaka radi krupnijeg ploda.",
            "Zalivanje": "Sistem kap po kap je najefikasniji."
        }
    }
    
    izbor_povrce = st.selectbox("Izaberi povrće:", list(povrce_detalji.keys()))
    p = povrce_detalji[izbor_povrce]
    
    st.subheader(f"Gajenje: {izbor_povrce}")
    st.markdown(f"- **Tip uzgoja:** {p['Tip']}")
    st.markdown(f"- **Ključni savet:** {p['Savet']}")
    st.markdown(f"- **Navodnjavanje:** {p['Zalivanje']}")
