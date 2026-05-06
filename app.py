import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide")

# --- 1. PAMETNA KONFIGURACIJA MODELA ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Pokušavamo da nađemo bilo koji dostupan model na tvom nalogu
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Biramo prvi dostupan (obično gemini-1.5-flash ili gemini-pro)
        model_name = available_models[0] if available_models else "models/gemini-pro"
        model = genai.GenerativeModel(model_name)
    except:
        # Ako list_models zakaže, idemo na najsigurniju varijantu bez 'models/' prefiksa
        model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Podesite GEMINI_API_KEY u Secrets!")

# --- 2. FUNKCIJE ---
def dobij_prognozu(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,precipitation_sum&timezone=auto"
    try:
        r = requests.get(url, timeout=5).json()
        return {"t": r['daily']['temperature_2m_max'][0], "k": r['daily']['precipitation_sum'][0]}
    except: return None

if 'lat' not in st.session_state: st.session_state.lat, st.session_state.lon = 44.01, 21.00

# --- 3. UI ---
st.title("🚜 AgroAsistent AI")
t1, t2, t3 = st.tabs(["📋 Planer", "📍 Lokacija", "💬 Chat"])

with t2:
    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=300, width=700, key="mapa")
    if map_data and map_data.get('last_clicked'):
        st.session_state.lat = map_data['last_clicked']['lat']
        st.session_state.lon = map_data['last_clicked']['lng']

with t1:
    mesec = datetime.now().strftime("%B")
    st.header(f"🌿 Pametni plan za: {mesec}")
    
    # --- TVOJA SPECIFIČNA LISTA USEVA ---
    kategorija = st.radio("Izaberi kategoriju:", ["Plastenik", "Otvoreno polje", "Voćnjak (3. god)"], horizontal=True)
    
    if kategorija == "Plastenik":
        moj_usev = st.selectbox("Biljka u plasteniku:", ["Paradajz", "Krastavac", "Paprika (Makedonka)"])
    elif kategorija == "Otvoreno polje":
        moj_usev = st.selectbox("Usev na otvorenom:", ["Krompir", "Boranija", "Grašak", "Crni i beli luk", "Lubenica", "Kukuruz šećerac"])
    else:
        moj_usev = st.selectbox("Voćka (70 stabala, kap-po-kap):", ["Jabuka", "Kruška", "Višnja", "Dunja", "Breskva", "Kajsija", "Trešnja", "Šljiva", "Nektarina", "Lešnik", "Orah"])

    # Dodatni parametri za AI
    st.caption(f"Sistem: Kap po kap aktiviran | Lokacija: Kruševac")
    
    if st.button("🚀 Generiši recept i plan radova"):
        # INSTRUKCIJA ZA AI (Podešena za Srbiju i tvoje uslove)
        prompt = f"""Ti si stručni agronom u Srbiji. Napravi plan za {moj_usev} u mesecu {mesec}.
        USLOVI: 
        - Kategorija: {kategorija}.
        - Navodnjavanje: Sistem kap po kap (obavezno navedi ako treba prihrana kroz sistem).
        - Starost voćnjaka: 3. godina (ako je izabrano voće).
        - Specifičnost: Paprika je sorta Makedonka (ako je izabrana).
        - Vreme: {m_info}.

        ZAHTEVI:
        1. Navedi 4 ključna zadatka (zaštita, prihrana, nega).
        2. Za svaki zadatak navedi KONKRETAN PREPARAT dostupan u Srbiji (npr. Signum, Quadris, Wuxal, Fitofert, itd.).
        3. Navedi tačnu dozu (npr. 20g na 10L vode ili 2kg po hektaru).
        4. Navedi razlog (npr. protiv plamenjače, za bolji cvet, protiv vaši).

        Formatiraj strogo kao: Zadatak | Detaljan savet sa preparatom i dozom"""

        with st.spinner(f"Analiziram {moj_usev}..."):
            try:
                response = model.generate_content(prompt)
                st.subheader(f"📋 Plan tretmana za {moj_usev}")
                
                for i, linija in enumerate(response.text.strip().split('\n')):
                    if "|" in linija:
                        z, d = linija.split("|")
                        with st.expander(f"📌 {z.strip()}", expanded=True):
                            st.write(d.strip())
                            st.checkbox("Izvršeno", key=f"ch_{moj_usev}_{i}")
            except Exception as e:
                st.error(f"Greška: {str(e)}")

with t3:
    pitanje = st.text_input("Pitaj:")
    if st.button("Pošalji"):
        try:
            res = model.generate_content(pitanje)
            st.write(res.text)
        except: st.error("AI nedostupan.")
