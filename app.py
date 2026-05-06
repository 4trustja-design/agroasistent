import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

# --- 1. KONFIGURACIJA (Stabilna verzija) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    try:
        # Koristimo direktan poziv modelu koji ti je najbolje radio
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('gemini-pro')
else:
    st.error("Podesite GEMINI_API_KEY u Secrets!")

# --- 2. METEO FUNKCIJA (Kruševac centar) ---
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
    map_data = st_folium(m, height=300, width=700, key="mapa_finalna")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']
        st.rerun()

with t1:
    mesec = datetime.now().strftime("%B")
    st.header(f"📅 Plan za: {mesec}")
    
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    m_info = f"Temperatura {meteo['t']}°C, padavine {meteo['k']}mm." if meteo else "Sezonski prosek"
    if meteo: st.info(f"🌤️ Trenutno: {m_info}")

    # TVOJA SPECIFIČNA LISTA
    kategorija = st.radio("Kategorija:", ["Plastenik", "Otvoreno polje", "Mrešoviti voćnjak (3. god)"], horizontal=True)
    
    if kategorija == "Plastenik":
        moj_usev = st.selectbox("Biljka:", ["Paradajz", "Krastavac", "Paprika (Makedonka)"])
    elif kategorija == "Otvoreno polje":
        moj_usev = st.selectbox("Biljka:", ["Krompir", "Boranija", "Grašak", "Crni i beli luk", "Lubenica", "Kukuruz šećerac"])
    else:
        moj_usev = st.selectbox("Voćka (70 stabala):", ["Jabuka", "Kruška", "Višnja", "Dunja", "Breskva", "Kajsija", "Trešnja", "Šljiva", "Nektarina", "Lešnik", "Orah"])

    if st.button("✨ Generiši recept i plan", type="primary"):
        # INSTRUKCIJA KOJA "FORCE-UJE" PREPARATE
        prompt = f"""Ti si iskusni agronom u Srbiji. Napravi plan za {moj_usev} u mesecu {mesec}.
        KONTEKST:
        - Tip gajenja: {kategorija}. Sistem kap po kap (obavezna fertirigacija).
        - Lokacija: Kruševac (vreme: {m_info}).
        - Voće: 3. godina (formiranje krošnje).

        ⚠️ OBAVEZNA PRAVILA ZA ODGOVOR:
        1. Za svaki od 4 zadatka MORAŠ napisati tačan komercijalni naziv preparata dostupan u Srbiji (npr. Signum, Quadris, Ridomil, Fitofert Kristal, YaraMila, itd.).
        2. Navedi preciznu dozu (npr. 0.2% ili 20g na 10L vode).
        3. Ne koristi reč 'fungicid' ili 'đubrivo' bez naziva brenda.

        Format: Zadatak | [PREPARAT] - Doza i uputstvo za rad"""

        with st.spinner("Sastavljam recepte..."):
            try:
                response = model.generate_content(prompt)
                st.subheader(f"📋 Recepti za {moj_usev}:")
                linije = response.text.strip().split('\n')
                for i, linija in enumerate(linije):
                    if "|" in linija:
                        z, d = linija.split("|")
                        with st.expander(f"💊 {z.strip()}", expanded=True):
                            st.write(d.strip())
                            st.checkbox("Urađeno", key=f"check_{moj_usev}_{i}")
            except Exception as e:
                st.error(f"Sistemska greška: {str(e)}")

with t3:
    upit = st.text_input("Pitaj agronoma:")
    if st.button("Pošalji"):
        st.write(model.generate_content(f"Kao agronom odgovori kratko: {upit}").text)
