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
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('gemini-pro')
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
    map_data = st_folium(m, height=300, width=700, key="mapa_final_v3")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.rerun()

with t1:
    mesec = datetime.now().strftime("%B")
    st.header(f"📅 Plan za: {mesec}")
    
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    m_info = f"{meteo['t']}°C, kiša {meteo['k']}mm" if meteo else "Sezonski prosek"
    if meteo: st.info(f"🌤️ Trenutno: {m_info}")

    kategorija = st.radio("Kategorija:", ["Plastenik", "Otvoreno polje", "Voćnjak (3. god)"], horizontal=True)
    
    if kategorija == "Plastenik":
        moj_usev = st.selectbox("Biljka:", ["Paradajz", "Krastavac", "Paprika (Makedonka)"])
    elif kategorija == "Otvoreno polje":
        moj_usev = st.selectbox("Biljka:", ["Krompir", "Boranija", "Grašak", "Crni i beli luk", "Lubenica", "Kukuruz šećerac"])
    else:
        moj_usev = st.selectbox("Voćka (70 stabala):", ["Jabuka", "Kruška", "Višnja", "Dunja", "Breskva", "Kajsija", "Trešnja", "Šljiva", "Nektarina", "Lešnik", "Orah"])

    st.caption("💧 Sistem kap po kap: Aktivan | 📍 Lokacija: Kruševac")

    if st.button("✨ Generiši recept i plan", type="primary"):
        # ULTIMATIVNI PROMPT ZA PREPARATE
        prompt = f"""Ti si stručni agronom u Srbiji. Napravi precizan plan za {moj_usev} u mesecu {mesec}.
        KONTEKST:
        - Gajenje: {kategorija}.
        - Navodnjavanje: Sistem kap po kap.
        - Lokacija: Kruševac (Vreme: {m_info}).
        - Starost: Voće je u 3. godini.

        ⚠️ STROGA PRAVILA ZA ODGOVOR:
        1. Za SVAKI zadatak OBAVEZNO navedi tačan naziv komercijalnog preparata ili đubriva dostupnog u apotekama u Srbiji (npr. Signum, Quadris, Chorus, Ridomil, Fitofert, YaraMila, Galenika Fitofarmacija preparati).
        2. Navedi preciznu dozu (npr. 0.3% ili 20g na 10L ili 2kg/ha).
        3. Navedi tačan razlog (npr. protiv plamenjače, suzbijanje vaši, folijarna prihrana).
        4. Ne koristi uopštene reči. Ako pišeš o prihrani preko sistema, navedi tačnu formulaciju đubriva (npr. Fitofert 20:20:20).

        Formatiraj isključivo kao: Zadatak | Detaljan recept sa nazivom preparata i dozom"""

        with st.spinner("AI agronom piše recepte..."):
            try:
                response = model.generate_content(prompt)
                st.subheader(f"📋 Recepti za {moj_usev}:")
                linije = response.text.strip().split('\n')
                for i, linija in enumerate(linije):
                    if "|" in linija:
                        z, d = linija.split("|")
                        with st.expander(f"💊 {z.strip()}", expanded=True):
                            st.write(d.strip())
                            st.checkbox("Izvršeno", key=f"check_v3_{moj_usev}_{i}")
            except Exception as e:
                st.error(f"Greška: {str(e)}")

with t3:
    st.header("💬 Brzi savet")
    upit = st.text_input("Pitaj bilo šta:")
    if st.button("Pošalji"):
        res = model.generate_content(f"Kao agronom odgovori kratko: {upit}")
        st.write(res.text)
