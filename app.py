import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

# Rešavanje 404 greške forsiranjem stabilnog modela
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Koristimo direktan naziv bez models/ prefiksa ako v1beta pravi problem
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
    map_data = st_folium(m, height=300, width=700, key="mapa_final_v4")
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
        # STROGI PROMPT ZA PREPARATE
        prompt = f"""Ti si stručni agronom u Srbiji. Napravi precizan plan za {moj_usev} u mesecu {mesec}.
        Lokacija: Kruševac. Navodnjavanje: Kap po kap.
        
        ⚠️ OBAVEZNO ZA SVAKI OD 4 ZADATKA:
        1. Napisati TAČAN komercijalni naziv preparata dostupan u Srbiji (npr. Signum, Chorus, Quadris, Ridomil, Fitofert, YaraMila, itd.).
        2. Napisati preciznu dozu (npr. 25ml na 10L vode ili 2kg/ha).
        3. Napisati razlog primene.
        
        Formatiraj isključivo kao: Zadatak | Detaljan recept sa nazivom preparata i dozom"""

        with st.spinner("AI agronom kreira recepte..."):
            try:
                # Pokušaj generisanja sa primarnim modelom
                response = model.generate_content(prompt)
                st.subheader(f"📋 Recepti za {moj_usev}:")
                
                linije = response.text.strip().split('\n')
                for i, linija in enumerate(linije):
                    if "|" in linija:
                        z, d = linija.split("|")
                        with st.expander(f"💊 {z.strip()}", expanded=True):
                            st.write(d.strip())
                            st.checkbox("Zadatak izvršen", key=f"c_{moj_usev}_{i}")
            except Exception as e:
                # Backup plan ako 1.5-flash i dalje baca 404
                try:
                    model_alt = genai.GenerativeModel('gemini-pro')
                    response = model_alt.generate_content(prompt)
                    st.success("Korišćen stabilni Gemini-Pro model.")
                    # Ponavljanje logike prikaza ovde radi sigurnosti
                    linije = response.text.strip().split('\n')
                    for i, linija in enumerate(linije):
                        if "|" in linija:
                            z, d = linija.split("|")
                            with st.expander(f"💊 {z.strip()}", expanded=True):
                                st.write(d.strip())
                except:
                    st.error("Greška u povezivanju sa Google serverom. Proverite API ključ.")

with t3:
    st.header("💬 Chat sa agronomom")
    upit = st.text_input("Pitaj:")
    if st.button("Pošalji"):
        try:
            res = model.generate_content(upit)
            st.write(res.text)
        except: st.error("AI trenutno nije dostupan.")
