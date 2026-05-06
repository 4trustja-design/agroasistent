import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

# --- 1. KONFIGURACIJA AI MODELA ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = available_models[0] if available_models else "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name)
    except:
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

if 'lat' not in st.session_state: st.session_state.lat, st.session_state.lon = 43.58, 21.32 # Kruševac default

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
    
    # METEO PODACI SA FIX-OM ZA m_info
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    if meteo:
        m_info = f"Temperatura {meteo['t']}°C, padavine {meteo['k']}mm."
        st.info(f"🌤️ Trenutno u Kruševcu: {meteo['t']}°C | Padavine: {meteo['k']}mm")
    else:
        m_info = "Vremenski uslovi su uobičajeni za ovo doba godine."
        st.warning("Prognoza trenutno nije dostupna, koristi se sezonski prosek.")

    # --- TVOJI SPECIFIČNI USEVI ---
    kategorija = st.radio("Kategorija:", ["Plastenik", "Otvoreno polje", "Mrešoviti voćnjak (3. god)"], horizontal=True)
    
    if kategorija == "Plastenik":
        moj_usev = st.selectbox("Biljka:", ["Paradajz", "Krastavac", "Paprika (Makedonka)"])
    elif kategorija == "Otvoreno polje":
        moj_usev = st.selectbox("Biljka:", ["Krompir", "Boranija", "Grašak", "Crni i beli luk", "Lubenica", "Kukuruz šećerac"])
    else:
        moj_usev = st.selectbox("Voćka (70 stabala):", ["Jabuka", "Kruška", "Višnja", "Dunja", "Breskva", "Kajsija", "Trešnja", "Šljiva", "Nektarina", "Lešnik", "Orah"])

    st.caption("💧 Sistem kap po kap: Aktivan | 📍 Lokacija: Kruševac")

   if st.button("✨ Generiši recept i plan"):
        # STROŽI PROMPT ZA KONKRETNE PREPARATE
        prompt = f"""Ti si iskusni agronom u Srbiji. Napravi precizan plan za {moj_usev} u mesecu {mesec}.
        KONTEKST:
        - Tip gajenja: {kategorija}.
        - Tehnologija: Sistem kap po kap (obavezno navedi đubriva za fertirigaciju).
        - Lokacija: Kruševac (vreme: {m_info}).
        - Starost: Ako je voće, 3. je godina.

        ⚠️ OBAVEZNA PRAVILA ZA ODGOVOR:
        1. Za SVAKI zadatak moraš napisati tačan naziv komercijalnog preparata ili đubriva dostupnog u Srbiji (npr. Signum, Chorus, Quadris, Ridomil, Fitofert, YaraMila, itd.).
        2. Navedi preciznu dozu (npr. 0.2% ili 2.5 kg/ha).
        3. Navedi razlog primene (npr. suzbijanje plamenjače, nadoknada kalcijuma).
        4. Ne koristi uopštene termine kao 'fungicid' ili 'đubrivo' bez navođenja brenda.

        Format: Naziv zadatka | Detaljan recept: [Naziv preparata] u dozi [Doza] - [Obrazloženje]"""

        with st.spinner(f"Pišem recept za {moj_usev}..."):
            try:
                response = model.generate_content(prompt)
                st.subheader(f"📋 Personalizovani recept za {moj_usev}:")
                
                odgovor = response.text.strip().split('\n')
                for i, linija in enumerate(odgovor):
                    if "|" in linija:
                        z, d = linija.split("|")
                        with st.expander(f"💊 {z.strip()}", expanded=True):
                            st.write(d.strip())
                            st.checkbox("Zadatak izvršen", key=f"z_{moj_usev}_{i}")
            except Exception as e:
                st.error(f"Greška: {str(e)}")
with t3:
    st.header("💬 Brzi savet")
    pitanje = st.text_input("Pitaj bilo šta (npr. 'čime prskati vaš na paprici?'):")
    if st.button("Pošalji"):
        try:
            res = model.generate_content(pitanje)
            st.write(res.text)
        except: st.error("AI trenutno nije dostupan.")
