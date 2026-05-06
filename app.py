import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

# --- 1. KONFIGURACIJA (Ona koja ti je radila) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Koristimo direktno model bez ListModels funkcije koja je pravila 404 grešku
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
    map_data = st_folium(m, height=300, width=700, key="mapa_final")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.rerun()

with t1:
    mesec = datetime.now().strftime("%B")
    st.header(f"📅 Plan za: {mesec}")
    
    # Prvo definišemo m_info da bismo izbegli NameError sa slike
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    if meteo:
        m_info = f"Temperatura {meteo['t']}°C, padavine {meteo['k']}mm."
        st.info(f"🌤️ Trenutno u Kruševcu: {m_info}")
    else:
        m_info = "Sezonski prosek za Kruševac."
        st.warning("Prognoza trenutno nije dostupna.")

    kategorija = st.radio("Kategorija:", ["Plastenik", "Otvoreno polje", "Voćnjak (3. god)"], horizontal=True)
    
    if kategorija == "Plastenik":
        moj_usev = st.selectbox("Biljka:", ["Paradajz", "Krastavac", "Paprika (Makedonka)"])
    elif kategorija == "Otvoreno polje":
        moj_usev = st.selectbox("Biljka:", ["Krompir", "Boranija", "Grašak", "Crni i beli luk", "Lubenica", "Kukuruz šećerac"])
    else:
        moj_usev = st.selectbox("Voćka (70 stabala):", ["Jabuka", "Kruška", "Višnja", "Dunja", "Breskva", "Kajsija", "Trešnja", "Šljiva", "Nektarina", "Lešnik", "Orah"])

    st.caption("💧 Sistem kap po kap: Aktivan | 📍 Lokacija: Kruševac")

    if st.button("✨ Generiši recept i plan", type="primary"):
        # IZMENA SAMO OVDE: Dodat zahtev za konkretna sredstva
        prompt = f"""Ti si iskusni agronom u Srbiji. Napravi precizan plan za {moj_usev} u mesecu {mesec}.
        Lokacija: Kruševac. Vreme: {m_info}. Navodnjavanje: Kap po kap.
        
        ZAHTEV: Navedi 4 ključna zadatka. Za SVAKI zadatak moraš napisati:
        1. TAČAN NAZIV komercijalnog preparata ili đubriva (npr. Signum, Chorus, Quadris, Fitofert, YaraMila itd.).
        2. Preciznu DOZU (npr. 0.2% ili 2kg/ha).
        3. RAZLOG primene.
        
        Format: Zadatak | Detaljan recept sa nazivom preparata i dozom"""

        with st.spinner("AI agronom analizira..."):
            try:
                response = model.generate_content(prompt)
                st.subheader(f"📋 Recepti za {moj_usev}:")
                # Formatiranje koje ti se dopalo
                for i, linija in enumerate(response.text.strip().split('\n')):
                    if "|" in linija:
                        z, d = linija.split("|")
                        with st.expander(f"💊 {z.strip()}", expanded=True):
                            st.write(d.strip())
                            st.checkbox("Izvršeno", key=f"z_{moj_usev}_{i}")
            except Exception as e:
                st.error(f"Sistemska greška: {str(e)}")

with t3:
    st.header("💬 Chat")
    upit = st.text_input("Pitaj bilo šta:")
    if st.button("Pošalji"):
        try:
            res = model.generate_content(upit)
            st.write(res.text)
        except: st.error("AI trenutno nije dostupan.")
