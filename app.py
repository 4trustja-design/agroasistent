import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from datetime import datetime
import requests

# --- 1. KONFIGURACIJA I POVEZIVANJE ---
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSccBzwQSmytB6TSzYLmcj429FiWMVGm7WUTUi5GqZZUHV6C_g/formResponse"

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Greška: Proverite GEMINI_API_KEY u Streamlit Secrets.")

# --- 2. POMOĆNE FUNKCIJE ---

def posalji_u_tabelu(ime, radnja):
    payload = {
        "entry.880598687": ime,    
        "entry.31175628": radnja,  
        "entry.1741593922": "Obavljeno" 
    }
    try:
        requests.post(FORM_URL, data=payload)
        return True
    except:
        return False

def dobij_vreme(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=precipitation_sum&timezone=auto"
    try:
        r = requests.get(url).json()
        return r['current_weather']['temperature'], r['daily']['precipitation_sum'][0]
    except:
        return None, None

# --- 3. INTERFEJS APLIKACIJE ---

st.set_page_config(page_title="AgroSmart Srbija", layout="wide", page_icon="🚜")

with st.sidebar:
    st.header("👤 Profil")
    korisnik = st.text_input("Ime / ID gazdinstva:", "Gost")
    st.divider()
    st.write("📊 [Tabela radova](https://docs.google.com/spreadsheets/d/1DU-w1I6yMuLIq9qQYhMGxdWds9dvaG9QlezJs87vExk/edit)")

st.title(f"🚜 AgroAsistent: {korisnik}")

# Gornji blok: Lokacija i Vreme
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📍 Lokacija zasada")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=300, use_container_width=True)
    lat, lon = (map_data['last_clicked']['lat'], map_data['last_clicked']['lng']) if map_data['last_clicked'] else (44.0165, 21.0059)

with c2:
    st.subheader("🌦️ Prognoza")
    temp, kisa = dobij_vreme(lat, lon)
    if temp is not None:
        st.metric("Temperatura", f"{temp}°C")
        st.metric("Padavine (24h)", f"{kisa}mm")
    else:
        st.write("Odaberite lokaciju na mapi.")

st.divider()

# Donji blok: Odabir grane, AI Saveti i Čekiranje
col_input, col_savet = st.columns([1, 2])

with col_input:
    st.subheader("⚙️ Podešavanja")
    
    # DODATO: Odabir između voćarstva i povrtarstva
    grana = st.radio("Izaberite granu poljoprivrede:", ["Voćarstvo", "Povrtarstvo"])
    
    if grana == "Voćarstvo":
        kultura = st.selectbox("Kultura:", ["Šljiva", "Jabuka", "Malina", "Trešnja", "Višnja", "Dunja", "Orah"])
        detalj = st.selectbox("Starost zasada:", ["1. godina", "2. godina", "3. godina", "Pun rod"])
    else:
        kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Kupus", "Luk", "Krompir"])
        detalj = st.selectbox("Način uzgoja:", ["Otvoreno polje", "Plastenik / Staklenik"])

    if st.button("Generiši plan zaštite i ishrane"):
        vreme_txt = f"Temperatura: {temp}C, Padavine: {kisa}mm." if temp else ""
        
        prompt = f"""
        Ti si stručni agronom u Srbiji. 
        Oblast: {grana}. Kultura: {kultura}. Specifičnost: {detalj}. 
        Mesec: Maj. Lokacija: Srbija. {vreme_txt}
        
        Zadatak: Daj 3 konkretna i aktuelna zadatka. 
        Za svaki zadatak navedi:
        1. Naziv mere.
        2. Tačan naziv preparata (npr. Signum, Quadris, Wuxal...) i dozu.
        
        Odgovori isključivo kao lista od 3 stavke.
        """
        
        with st.spinner("AI analizira najbolje preparate..."):
            try:
                odgovor = model.generate_content(prompt).text
                st.session_state.lista_zadataka = [z.strip() for z in odgovor.split('\n') if len(z) > 10][:3]
            except:
                st.error("AI servis trenutno nije dostupan.")

with col_savet:
    st.subheader("📋 Preporučeni radovi")
    if 'lista_zadataka' in st.session_state:
        for zadatak in st.session_state.lista_zadataka:
            if st.button(f"✅ Završeno: {zadatak}", use_container_width=True):
                if korisnik != "Gost":
                    if posalji_u_tabelu(korisnik, zadatak):
                        st.success(f"Zapisano za: {korisnik}")
                    else:
                        st.error("Greška pri slanju u tabelu.")
                else:
                    st.warning("Unesite ime u sidebar-u.")
    else:
        st.info("Podesite parametre levo i kliknite na dugme za generisanje.")

st.sidebar.warning("⚠️ AI saveti su informativni. Uvek pročitajte uputstvo preparata pre upotrebe.")
