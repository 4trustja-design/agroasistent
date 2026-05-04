import streamlit as st
from google import genai
import folium
from streamlit_folium import st_folium
import requests

# --- 1. KONFIGURACIJA ---
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSccBzwQSmytB6TSzYLmcj429FiWMVGm7WUTUi5GqZZUHV6C_g/formResponse"

if "GEMINI_API_KEY" in st.secrets:
    # NOVA METODA: Pravimo klijenta direktno
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Nedostaje API ključ u Secrets!")
    st.stop()

# --- 2. FUNKCIJE ---
def posalji_u_tabelu(ime, radnja):
    payload = {"entry.880598687": ime, "entry.31175628": radnja, "entry.1741593922": "Obavljeno"}
    try:
        requests.post(FORM_URL, data=payload, timeout=5)
        return True
    except:
        return False

# --- 3. UI ---
st.set_page_config(page_title="AgroSmart Srbija", layout="wide")

with st.sidebar:
    st.header("👤 Korisnik")
    korisnik = st.text_input("Vaše ime:", "Gost")

st.title(f"🚜 AgroAsistent: {korisnik}")

# Mapa
m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
folium.LatLngPopup().add_to(m)
map_data = st_folium(m, height=300, use_container_width=True, key="agro_map_v7")

st.divider()

# Parametri
grana = st.radio("Grana:", ["Voćarstvo", "Povrtarstvo"])
kultura = st.selectbox("Kultura:", ["Šljiva", "Jabuka", "Malina", "Paradajz", "Paprika"])

if st.button("Generiši plan", type="primary"):
    with st.spinner("AI agronom analizira..."):
        prompt = f"Agronom Srbija. {grana}: {kultura}. Mesec: Maj. Daj 3 kratka zadatka sa preparatima. Lista."
        try:
            # NOVA METODA POZIVANJA: Bez 'models/' prefiksa koji pravi 404
            response = client.models.generate_content(
                model='gemini-1.5-flash', 
                contents=prompt
            )
            
            if response.text:
                st.session_state.zadaci = [z.strip() for z in response.text.strip().split('\n') if len(z) > 10][:3]
            else:
                st.error("AI nije vratio odgovor.")
        except Exception as e:
            # Ako je kvota (429), ispisaće jasnu poruku
            if "429" in str(e):
                st.error("⌛ Previše zahteva! Sačekaj 30 sekundi i klikni ponovo.")
            else:
                st.error(f"Greška: {e}")

# Prikaz zadataka
if 'zadaci' in st.session_state:
    for zadatak in st.session_state.zadaci:
        if st.button(f"✅ Završeno: {zadatak}", use_container_width=True):
            if korisnik != "Gost":
                if posalji_u_tabelu(korisnik, zadatak):
                    st.success("Upisano u tabelu!")
