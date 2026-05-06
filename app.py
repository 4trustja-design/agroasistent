import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

# --- 1. FUNKCIJA ZA DIREKTAN POZIV AI (Bez biblioteke) ---
def pozovi_gemini(prompt):
    api_key = st.secrets["GEMINI_API_KEY"]
    # Koristimo v1 endpoint koji je najstabilniji
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 1024,
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        res_json = response.json()
        if response.status_code == 200:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Greška servera: {res_json.get('error', {}).get('message', 'Nepoznato')}"
    except Exception as e:
        return f"Problem sa vezom: {str(e)}"

# --- 2. POMOĆNE FUNKCIJE ---
def dobij_prognozu(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,precipitation_sum&timezone=auto"
    try:
        r = requests.get(url, timeout=5).json()
        return {"t": r['daily']['temperature_2m_max'][0], "k": r['daily']['precipitation_sum'][0]}
    except: return None

if 'lat' not in st.session_state: st.session_state.lat, st.session_state.lon = 43.58, 21.32

# --- 3. UI ---
st.title("🚜 AgroAsistent AI")
t1, t2, t3 = st.tabs(["📋 Pametni Planer", "📍 Lokacija", "💬 Chat"])

with t2:
    st.header("📍 Lokacija imanja")
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=8)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=300, width=700, key="mapa_final_v5")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.rerun()

with t1:
    mesec = datetime.now().strftime("%B")
    st.header(f"📅 Plan za: {mesec}")
    
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    m_info = f"{meteo['t']}°C, kiša {meteo['k']}mm" if meteo else "Sezonski prosek"
    
    kategorija = st.radio("Kategorija:", ["Plastenik", "Otvoreno polje", "Voćnjak (3. god)"], horizontal=True)
    
    # Tvoj spisak useva
    if kategorija == "Plastenik":
        moj_usev = st.selectbox("Biljka:", ["Paradajz", "Krastavac", "Paprika (Makedonka)"])
    elif kategorija == "Otvoreno polje":
        moj_usev = st.selectbox("Biljka:", ["Krompir", "Boranija", "Grašak", "Crni i beli luk", "Lubenica", "Kukuruz šećerac"])
    else:
        moj_usev = st.selectbox("Voćka (70 stabala):", ["Jabuka", "Kruška", "Višnja", "Dunja", "Breskva", "Kajsija", "Trešnja", "Šljiva", "Nektarina", "Lešnik", "Orah"])

    if st.button("✨ Generiši recept i plan", type="primary"):
        prompt = f"""Ti si stručni agronom u Srbiji. Napravi precizan plan za {moj_usev} u mesecu {mesec}.
        Navodnjavanje: Sistem kap po kap. Lokacija: Kruševac (Vreme: {m_info}).
        
        OBAVEZNO ZA SVAKI OD 4 ZADATKA:
        1. Navedi tačan naziv komercijalnog PREPARATA ili ĐUBRIVA (npr. Signum, Chorus, Quadris, Fitofert, itd.).
        2. Navedi preciznu DOZU (npr. 0.2% ili 2kg/ha).
        3. Navedi razlog primene.
        
        Format: Zadatak | Detaljan recept sa nazivom preparata i dozom"""

        with st.spinner("AI agronom piše recept..."):
            odgovor = pozovi_gemini(prompt)
            
            if "Greška" in odgovor or "Problem" in odgovor:
                st.error(odgovor)
            else:
                st.subheader(f"📋 Recepti za {moj_usev}:")
                linije = odgovor.strip().split('\n')
                for i, linija in enumerate(linije):
                    if "|" in linija:
                        z, d = linija.split("|")
                        with st.expander(f"💊 {z.strip()}", expanded=True):
                            st.write(d.strip())
                            st.checkbox("Zadatak izvršen", key=f"v5_{moj_usev}_{i}")

with t3:
    upit = st.text_input("Pitaj:")
    if st.button("Pošalji"):
        st.write(pozovi_gemini(f"Kratko odgovori kao agronom: {upit}"))
