import streamlit as st
from google import genai
from google.genai import types
import folium
from streamlit_folium import st_folium
import requests
import time

# --- 1. KONFIGURACIJA I PROVERA KLJUČA ---
st.set_page_config(page_title="AgroSmart Srbija", layout="wide", page_icon="🚜")

# Provera da li postoji API ključ u Secrets
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ Greška: GEMINI_API_KEY nije pronađen u Streamlit Secrets podešavanjima!")
    st.stop()

# Inicijalizacija AI klijenta (Pravimo 'client' jednom ovde da bi bio dostupan svuda)
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"❌ Kritična greška pri inicijalizaciji AI klijenta: {e}")
    st.stop()

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSccBzwQSmytB6TSzYLmcj429FiWMVGm7WUTUi5GqZZUHV6C_g/formResponse"

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

# --- 3. KORISNIČKI INTERFEJS (UI) ---

# Sidebar za profil
with st.sidebar:
    st.header("👤 Profil korisnika")
    korisnik = st.text_input("Ime / ID gazdinstva:", "Gost")
    st.divider()
    st.write("📊 [Pregled Tabele](https://docs.google.com/spreadsheets/d/1DU-w1I6yMuLIq9qQYhMGxdWds9dvaG9QlezJs87vExk/edit)")
    st.caption("v1.5 | AgroSmart AI")

st.title(f"🚜 AgroAsistent: {korisnik}")

# Gornja sekcija: Mapa i Vreme
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📍 Lokacija zasada")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    
    # Prikaz mape
    map_data = st_folium(m, height=300, use_container_width=True, key="agro_map_final")
    
    lat, lon = 44.0165, 21.0059
    if map_data and map_data.get('last_clicked'):
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
        st.success(f"Lokacija pinovana: {round(lat,3)}, {round(lon,3)}")

with c2:
    st.subheader("🌦️ Lokalni meteo")
    temp, kisa = dobij_vreme(lat, lon)
    if temp is not None:
        st.metric("Temperatura", f"{temp}°C")
        st.metric("Padavine (24h)", f"{kisa}mm")
    else:
        st.info("Kliknite na mapu za prognozu.")

st.divider()

# Donja sekcija: Parametri i AI Preporuke
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

    if st.button("Generiši plan radova", type="primary"):
        with st.spinner("AI agronom analizira podatke..."):
            vreme_info = f"Temp: {temp}C, Kiša: {kisa}mm." if temp else ""
            prompt_text = f"Ti si stručni agronom u Srbiji. Oblast: {grana}. Kultura: {kultura} ({detalj}). Mesec: Maj. Lokacija: Srbija. {vreme_info} Daj 3 konkretna zadatka sa preparatima i dozama. Odgovori isključivo kao lista od 3 stavke."
            
            # Rešavanje 429 greške (Retry logika) i 404 greške
            uspeh = False
            pokusaji = 0
            while not uspeh and pokusaji < 2:
                try:
                    # Koristimo stabilan model gemini-1.5-flash
                    odgovor = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=prompt_text
                    )
                    if odgovor and odgovor.text:
                        st.session_state.zadaci = [z.strip() for z in odgovor.text.strip().split('\n') if len(z) > 10][:3]
                        uspeh = True
                    else:
                        st.error("AI je vratio prazan odgovor.")
                        break
                except Exception as e:
                    if "429" in str(e):
                        st.warning("Server je zauzet (Quota limit). Čekam 15 sekundi...")
                        time.sleep(15)
                        pokusaji += 1
                    elif "404" in str(e):
                        # Ako 1.5 flash ne radi, probaj 2.0 verziju
                        try:
                            odgovor = client.models.generate_content(model='gemini-2.0-flash', contents=prompt_text)
                            st.session_state.zadaci = [z.strip() for z in odgovor.text.strip().split('\n') if len(z) > 10][:3]
                            uspeh = True
                        except Exception as e2:
                            st.error(f"Model nije pronađen: {e2}")
                            break
                    else:
                        st.error(f"AI greška: {e}")
                        break

with col_out:
    st.subheader("📋 Preporučeni zadaci")
    if 'zadaci' in st.session_state:
        for zadatak in st.session_state.zadaci:
            if st.button(f"✅ Završeno: {zadatak}", use_container_width=True, key=zadatak):
                if korisnik != "Gost":
                    if posalji_u_tabelu(korisnik, zadatak):
                        st.toast(f"Sačuvano za: {korisnik}", icon="💾")
                    else:
                        st.error("Greška pri upisu u tabelu.")
                else:
                    st.warning("Unesite ime u levom meniju da biste sačuvali rad.")
    else:
        st.info("Podesite parametre i kliknite na dugme za generisanje preporuka.")

st.sidebar.warning("⚠️ AI saveti su informativni. Obavezno pročitajte uputstva na ambalaži preparata.")
