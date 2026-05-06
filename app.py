import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Koristimo samo naziv modela, bez verzije API-ja u nazivu
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Podesite GEMINI_API_KEY u Secrets!")

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
    map_data = st_folium(m, height=300, width=700, key="mapa_final_fixed")
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
    
    if kategorija == "Plastenik":
        moj_usev = st.selectbox("Biljka:", ["Paradajz", "Krastavac", "Paprika (Makedonka)"])
    elif kategorija == "Otvoreno polje":
        moj_usev = st.selectbox("Biljka:", ["Krompir", "Boranija", "Grašak", "Crni i beli luk", "Lubenica", "Kukuruz šećerac"])
    else:
        moj_usev = st.selectbox("Voćka (70 stabala):", ["Jabuka", "Kruška", "Višnja", "Dunja", "Breskva", "Kajsija", "Trešnja", "Šljiva", "Nektarina", "Lešnik", "Orah"])

    if st.button("✨ Generiši recept i plan", type="primary"):
        # Prompt je sada još agresivniji u zahtevanju brendova
        prompt = f"""Ti si stručni agronom u Srbiji. Napravi precizan plan za {moj_usev} u mesecu {mesec}.
        Lokacija: Kruševac. Navodnjavanje: Kap po kap.
        
        OBAVEZNO ZA SVAKI OD 4 ZADATKA:
        1. Napisat tačan komercijalni naziv preparata (npr. Signum, Chorus, Quadris, Ridomil, Fitofert 20:20:20, itd.).
        2. Napisati preciznu dozu (npr. 25ml na 10L vode ili 2kg/ha).
        3. Napisati razlog primene.
        
        Formatiraj isključivo kao: Zadatak | Detaljan recept sa nazivom preparata i dozom"""

        with st.spinner("AI agronom kreira recepte..."):
            try:
                # Direktno generisanje bez ListModels da bismo izbegli 404
                response = model.generate_content(prompt)
                st.subheader(f"📋 Recepti za {moj_usev}:")
                
                linije = response.text.strip().split('\n')
                for i, linija in enumerate(linije):
                    if "|" in linija:
                        z, d = linija.split("|")
                        with st.expander(f"💊 {z.strip()}", expanded=True):
                            st.write(d.strip())
                            st.checkbox("Izvršeno", key=f"c_{moj_usev}_{i}")
            except Exception as e:
                # Ako 1.5-flash i dalje pravi problem, automatski prebaci na gemini-pro
                try:
                    model_backup = genai.GenerativeModel('gemini-pro')
                    response = model_backup.generate_content(prompt)
                    st.success("Korišćen rezervni model.")
                    # (Ponavljanje logike prikaza...)
                except:
                    st.error(f"Sistemski problem: {str(e)}")

with t3:
    st.header("💬 Chat sa agronomom")
    upit = st.text_input("Pitaj:")
    if st.button("Pošalji"):
        res = model.generate_content(upit)
        st.write(res.text)
