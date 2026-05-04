import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from datetime import datetime
import requests

# --- 1. KONFIGURACIJA I POVEZIVANJE ---

# Link tvoje Google forme za automatsko upisivanje u tabelu
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSccBzwQSmytB6TSzYLmcj429FiWMVGm7WUTUi5GqZZUHV6C_g/formResponse"

# Povezivanje sa AI modelom
try:
    # Ključ mora biti unesen u Streamlit Secrets pod nazivom GEMINI_API_KEY
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Greška: Proverite da li je GEMINI_API_KEY ispravno unet u Streamlit Secrets.")

# --- 2. POMOĆNE FUNKCIJE ---

def posalji_u_tabelu(ime, radnja):
    """Šalje podatke direktno u Google tabelu preko entry ID-jeva forme."""
    payload = {
        "entry.880598687": ime,    # ID za polje Korisnik
        "entry.31175628": radnja,  # ID za polje Akcija
        "entry.1741593922": "Obavljeno" # ID za polje Status
    }
    try:
        requests.post(FORM_URL, data=payload)
        return True
    except:
        return False

def dobij_vreme(lat, lon):
    """Preuzima temperaturu i padavine sa Open-Meteo API-ja."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=precipitation_sum&timezone=auto"
    try:
        r = requests.get(url).json()
        temp = r['current_weather']['temperature']
        kisa = r['daily']['precipitation_sum'][0]
        return temp, kisa
    except:
        return None, None

# --- 3. INTERFEJS APLIKACIJE ---

st.set_page_config(page_title="AgroSmart Srbija", layout="wide", page_icon="🚜")

# Sidebar - Korisnički profil i linkovi
with st.sidebar:
    st.header("👤 Korisnički profil")
    korisnik = st.text_input("Vaše ime / ID gazdinstva:", "Gost")
    st.info("Prijatelji mogu uneti svoje ime kako bi se radovi odvojeno beležili u vašoj tabeli.")
    st.divider()
    st.write("📊 [Pogledaj zajednički dnevnik](https://docs.google.com/spreadsheets/d/1DU-w1I6yMuLIq9qQYhMGxdWds9dvaG9QlezJs87vExk/edit)")
    st.caption("Savet: Podatke u tabeli možeš filtrirati po imenu korisnika.")

st.title(f"🚜 AgroAsistent: {korisnik}")

# Gornji blok: Lokacija i Meteorološki podaci
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📍 Lokacija zasada")
    # Inicijalna mapa (Srbija centar)
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    map_data = st_folium(m, height=300, use_container_width=True)
    
    # Hvatanje koordinata na klik
    if map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
    else:
        lat, lon = 44.0165, 21.0059 # Kruševac/Centar kao default

with c2:
    st.subheader("🌦️ Prognoza")
    temp, kisa = dobij_vreme(lat, lon)
    if temp is not None:
        st.metric("Trenutna Temperatura", f"{temp}°C")
        st.metric("Padavine (24h)", f"{kisa}mm")
        if kisa > 5:
            st.warning("Povećana vlaga: Rizik od gljivičnih oboljenja!")
    else:
        st.write("Kliknite na mapu za učitavanje vremenskih podataka.")

st.divider()

# Donji blok: AI Saveti, Preparati i Čekiranje
col_savet, col_info = st.columns([2, 1])

with col_savet:
    st.subheader("📋 Preporuka agronoma: Zaštita i Prihrana")
    
    # Parametri za AI
    c_biljka, c_faza = st.columns(2)
    with c_biljka:
        biljka = st.text_input("Kultura (npr. Šljiva, Malina):", "Šljiva")
    with c_faza:
        starost = st.text_input("Faza razvoja / Starost:", "2 godine")

    if st.button("Generiši plan sa preparatima"):
        vreme_txt = f"Temperatura: {temp}C, Padavine: {kisa}mm." if temp else ""
        
        # Napredni prompt koji traži konkretne preparate za Srbiju
        prompt = f"""
        Ti si stručni agronom specijalizovan za zaštitu bilja u Srbiji. 
        Kultura: {biljka}, faza/starost: {starost}. 
        Mesec: Maj. Lokacija: Srbija. {vreme_txt}
        
        Zadatak: Daj 3 konkretna i aktuelna zadatka za ovaj period. 
        Za svaki zadatak obavezno navedi:
        1. Šta se radi (npr. suzbijanje štetočine ili folijarna prihrana).
        2. Tačan naziv preparata koji je dostupan u Srbiji (npr. Signum, Tonus, Wuxal...).
        3. Dozu ili koncentraciju primene.
        
        Odgovori kratko i isključivo u obliku liste od 3 stavke.
        """
        
        with st.spinner("AI analizira bazu preparata..."):
            try:
                odgovor = model.generate_content(prompt).text
                # Pretvaramo odgovor u listu za interaktivne dugmiće
                st.session_state.lista_zadataka = [z.strip() for z in odgovor.split('\n') if len(z) > 10][:3]
            except:
                st.error("AI servis je trenutno preopterećen. Pokušajte ponovo za par sekundi.")

    # Prikaz interaktivne ček-liste
    if 'lista_zadataka' in st.session_state:
        st.write("---")
        st.markdown("##### ✍️ Evidentiraj obavljene radove:")
        for zadatak in st.session_state.lista_zadataka:
            if st.button(f"✅ Završio sam: {zadatak}", use_container_width=True):
                if korisnik != "Gost":
                    if posalji_u_tabelu(korisnik, zadatak):
                        st.success(f"Bravo! Podatak je uspešno upisan u dnevnik za: {korisnik}")
                    else:
                        st.error("Došlo je do greške pri komunikaciji sa Google tabelom.")
                else:
                    st.warning("Molimo unesite vaše ime u levom meniju (sidebar) kako biste sačuvali rad u tabelu.")

with col_info:
    st.info("""
    **Kako koristiti aplikaciju:**
    1. Unesi svoje ime levo u meniju.
    2. Klikni na mapu gde ti se nalazi voćnjak/bašta.
    3. Unesi kulturu i klikni na 'Generiši plan'.
    4. Kada poprskaš ili đubriš, klikni na dugme zadatka i on će se sam upisati u tvoju Google tabelu.
    """)
    st.warning("⚠️ **Napomena:** Saveti su generisani veštačkom inteligencijom. Pre upotrebe preparata uvek pročitajte zvanično uputstvo proizvođača.")
