import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

# --- 1. DIREKTNA KOMUNIKACIJA SA GOOGLE API (Bez posrednika) ---
def javi_se_agronomu(prompt):
    if "GEMINI_API_KEY" not in st.secrets:
        return "Greška: Ključ nije u Secrets-u!"
    
    api_key = st.secrets["GEMINI_API_KEY"]
    # Promena na v1beta putanju koja dokazano radi za Free Tier ključeve
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt + " Odgovori isključivo na srpskom jeziku, navodeći konkretne nazive preparata i doze."
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        res_data = response.json()
        
        if response.status_code == 200:
            # Izvlačenje teksta iz odgovora
            return res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            # Detaljan ispis greške ako ponovo zapne
            error_msg = res_data.get('error', {}).get('message', 'Nepoznata greška')
            return f"Greška {response.status_code}: {error_msg}"
            
    except Exception as e:
        return f"Greška u konekciji: {str(e)}"

# --- 2. POMOĆNE FUNKCIJE ---
def dobij_prognozu(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,precipitation_sum&timezone=auto"
    try:
        r = requests.get(url, timeout=5).json()
        return {"t": r['daily']['temperature_2m_max'][0], "k": r['daily']['precipitation_sum'][0]}
    except: return None

if 'lat' not in st.session_state: st.session_state.lat, st.session_state.lon = 43.58, 21.32

# --- 3. UI DIZAJN ---
st.title("🚜 AgroAsistent AI")
t1, t2, t3 = st.tabs(["📋 Pametni Planer", "📍 Lokacija", "💬 Chat"])

with t2:
    st.header("📍 Lokacija imanja")
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=8)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=300, width=700, key="mapa_final_v6")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.rerun()

with t1:
    mesec = datetime.now().strftime("%B")
    st.header(f"📅 Plan za: {mesec}")
    
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    m_info = f"{meteo['t']}°C, kiša {meteo['k']}mm" if meteo else "Sezonski prosek"
    if meteo: st.info(f"🌤️ Trenutna prognoza: {m_info}")

    kategorija = st.radio("Kategorija:", ["Plastenik", "Otvoreno polje", "Voćnjak (3. god)"], horizontal=True)
    
    if kategorija == "Plastenik":
        moj_usev = st.selectbox("Biljka:", ["Paradajz", "Krastavac", "Paprika (Makedonka)"])
    elif kategorija == "Otvoreno polje":
        moj_usev = st.selectbox("Biljka:", ["Krompir", "Boranija", "Grašak", "Crni i beli luk", "Lubenica", "Kukuruz šećerac"])
    else:
        moj_usev = st.selectbox("Voćka (70 stabala):", ["Jabuka", "Kruška", "Višnja", "Dunja", "Breskva", "Kajsija", "Trešnja", "Šljiva", "Nektarina", "Lešnik", "Orah"])

    st.caption("💧 Sistem kap po kap: Aktivan | 📍 Lokacija: Kruševac")

    if st.button("✨ Generiši recept i plan radova", type="primary"):
        prompt = f"""Ti si stručni agronom u Srbiji. Napravi plan za {moj_usev} u mesecu {mesec}.
        Lokacija: Kruševac. Navodnjavanje: Kap po kap. Vreme: {m_info}.
        
        OBAVEZNO ZA SVAKI OD 4 ZADATKA:
        1. Navedi tačan naziv komercijalnog PREPARATA ili ĐUBRIVA dostupnog u Srbiji (npr. Signum, Chorus, Quadris, Fitofert, YaraMila, itd.).
        2. Navedi preciznu DOZU (npr. 0.2% ili 2kg/ha).
        3. Navedi RAZLOG primene.
        
        Formatiraj isključivo kao: Zadatak | Detaljan recept sa nazivom preparata i dozom"""

        with st.spinner("AI agronom kreira plan..."):
            rezultat = javi_se_agronomu(prompt)
            
            if "Greška" in rezultat:
                st.error(rezultat)
            else:
                st.subheader(f"📋 Recepti za {moj_usev}:")
                for i, linija in enumerate(rezultat.strip().split('\n')):
                    if "|" in linija:
                        z, d = linija.split("|")
                        with st.expander(f"💊 {z.strip()}", expanded=True):
                            st.write(d.strip())
                            st.checkbox("Zadatak izvršen", key=f"v6_{moj_usev}_{i}")

with t3:
    upit = st.text_input("Pitaj agronoma:")
    if st.button("Pošalji"):
        with st.spinner("Odgovaram..."):
            st.write(javi_se_agronomu(f"Kao agronom odgovori kratko: {upit}"))
