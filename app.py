import streamlit as st
from google import genai
from google.genai import types
import folium
from streamlit_folium import st_folium
import requests

# --- 1. KONFIGURACIJA ---
# Link tvoje forme za upis u tabelu
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSccBzwQSmytB6TSzYLmcj429FiWMVGm7WUTUi5GqZZUHV6C_g/formResponse"

# Inicijalizacija AI Klijenta
try:
    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("Nedostaje GEMINI_API_KEY u Streamlit Secrets podešavanjima!")
except Exception as e:
    st.error(f"Greška pri povezivanju sa AI servisom: {e}")

# --- 2. POMOĆNE FUNKCIJE ---

def posalji_u_tabelu(ime, radnja):
    """Šalje podatke u Google Sheets preko tvoje forme."""
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
    """Preuzima meteo podatke za odabranu tačku."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=precipitation_sum&timezone=auto"
    try:
        r = requests.get(url).json()
        return r['current_weather']['temperature'], r['daily']['precipitation_sum'][0]
    except:
        return None, None

# --- 3. KORISNIČKI INTERFEJS (UI) ---

st.set_page_config(page_title="AgroSmart Srbija", layout="wide", page_icon="🚜")

# Sidebar
with st.sidebar:
    st.header("👤 Profil")
    korisnik = st.text_input("Ime / ID gazdinstva:", "Gost")
    st.divider()
    st.write("📊 [Tabela radova](https://docs.google.com/spreadsheets/d/1DU-w1I6yMuLIq9qQYhMGxdWds9dvaG9QlezJs87vExk/edit)")

st.title(f"🚜 AgroAsistent: {korisnik}")

# Gornji deo: Mapa i Vreme
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📍 Lokacija zasada")
    # Centrirano na Srbiju
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    
    # Interaktivna mapa
    map_data = st_folium(m, height=300, use_container_width=True, key="agro_map_v4")
    
    # Podrazumevane koordinate ako ništa nije kliknuto
    lat, lon = 44.0165, 21.0059
    if map_data and map_data.get('last_clicked'):
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
        st.success(f"Lokacija pinovana: {round(lat,3)}, {round(lon,3)}")

with c2:
    st.subheader("🌦️ Prognoza")
    temp, kisa = dobij_vreme(lat, lon)
    if temp is not None:
        st.metric("Temperatura", f"{temp}°C")
        st.metric("Padavine (24h)", f"{kisa}mm")
    else:
        st.info("Kliknite na mapu za prognozu.")

st.divider()

# Donji deo: AI i Čekiranje
col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("⚙️ Podešavanja")
    grana = st.radio("Grana poljoprivrede:", ["Voćarstvo", "Povrtarstvo"])
    
    if grana == "Voćarstvo":
        kultura = st.selectbox("Kultura:", ["Šljiva", "Jabuka", "Malina", "Trešnja", "Višnja"])
        detalj = st.selectbox("Faza/Starost:", ["1. godina", "2. godina", "3. godina", "Pun rod"])
    else:
        kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Kupus", "Krompir"])
        detalj = st.selectbox("Način uzgoja:", ["Otvoreno polje", "Plastenik"])

    if st.button("Generiši plan radova"):
        with st.spinner("AI agronom analizira..."):
            vreme_info = f"Temp: {temp}C, Kiša: {kisa}mm." if temp else ""
            prompt_text = f"""
            Ti si stručni agronom u Srbiji. Oblast: {grana}. Kultura: {kultura} ({detalj}). 
            Mesec: Maj. Lokacija: Srbija. {vreme_info}
            Daj 3 konkretna zadatka. Za svaki zadatak navedi naziv mere i tačan preparat sa dozom.
            Odgovori isključivo kao lista od 3 stavke.
            """
            
            # UNIVERZALNI POKUŠAJ: Koristimo najnoviji stabilni model bez prefiksa
            try:
                # Koristimo 'gemini-1.5-flash' bez ikakvih dodataka - to je najsigurnija putanja za novi SDK
                odgovor = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt_text
                )
                
                if odgovor and odgovor.text:
                    st.session_state.zadaci = [z.strip() for z in odgovor.text.strip().split('\n') if len(z) > 10][:3]
                else:
                    st.error("AI je vratio prazan odgovor. Pokušajte ponovo.")
                    
            except Exception as e:
                # Ako i dalje prijavljuje 404, koristimo najnoviji model iz 2.0 serije koji je uvek dostupan na novom SDK
                try:
                    odgovor = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt_text
                    )
                    st.session_state.zadaci = [z.strip() for z in odgovor.text.strip().split('\n') if len(z) > 10][:3]
                except Exception as final_e:
                    st.error(f"Kritična greška: {final_e}")

with col_out:
    st.subheader("📋 Preporučeni radovi")
    if 'zadaci' in st.session_state:
        for zadatak in st.session_state.zadaci:
            if st.button(f"✅ Završeno: {zadatak}", use_container_width=True):
                if korisnik != "Gost":
                    if posalji_u_tabelu(korisnik, zadatak):
                        st.success(f"Zapisano u tabelu za: {korisnik}")
                    else:
                        st.error("Greška pri slanju u tabelu.")
                else:
                    st.warning("Unesite svoje ime u levom meniju da biste sačuvali rad.")
    else:
        st.info("Podesite parametre levo i kliknite na dugme za generisanje.")

st.sidebar.warning("⚠️ Napomena: AI saveti su informativni. Uvek proverite uputstvo preparata.")
