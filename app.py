import streamlit as st
from streamlit_folium import st_folium
import folium
import requests

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

st.title("🌾 Pametni Poljoprivredni Savetnik")

with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    st.info("Ključ dobijaš besplatno na OpenWeatherMap sajtu.")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("Saveti za voćare (0-5 god)")
    voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik"])
    godina = st.slider("Starost sadnice:", 0, 5, 1)
    
    st.info(f"Kalendar za {voce} u {godina}. godini")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛡️ Zaštita")
        st.write("- Plavo prskanje (faza mirovanja)")
        st.checkbox("Urađeno tretiranje", key="v_zastita")
    with col2:
        st.subheader("🧪 Prehrana")
        st.write("- Osnovno đubrenje (NPK)")
        st.checkbox("Urađeno đubrenje", key="v_ishrana")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("Saveti za povrtare")
    tip = st.radio("Uzgoj:", ["Plastenik", "Otvoreno polje"], key="tip_uzgoja")
    povrce = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika", "Krastavac", "Kupus"])
    
    st.success(f"Preporuke za {povrce} ({tip})")
    st.checkbox("Rasad spreman za sadnju", key="p_rasad")
    st.checkbox("Postavljen sistem kap po kap", key="p_navodnjavanje")

# --- TAB 3: MOJA PARCELA ---
with tab3:
    st.header("📍 Lokacija i Vremenska Prognoza")
    st.write("Kliknite na mapu da vidite prognozu za vašu parcelu:")

    # Kreiranje mape centrirane na Srbiju
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    
    # Prikaz mape
    izlaz_mape = st_folium(m, width=700, height=450, key="glavna_mapa")

    # Logika za vremensku prognozu nakon klika
    if izlaz_mape and izlaz_mape.get('last_clicked'):
        lat = izlaz_mape['last_clicked']['lat']
        lon = izlaz_mape['last_clicked']['lng']
        
        st.success(f"Koordinate parcele: {lat:.4f}, {lon:.4f}")
        
        if meteo_key:
            try:
                url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key}&units=metric&lang=sr"
                res = requests.get(url)
                data = res.json()
                
                if res.status_code == 200:
                    t = data["main"]["temp"]
                    vl = data["main"]["humidity"]
                    vtr = data["wind"]["speed"]
                    st.metric("Trenutna temperatura", f"{t} °C")
                    st.write(f"**Vlažnost:** {vl}% | **Vetar:** {vtr} m/s")
                    
                    if t < 2: st.error("⚠️ PAŽNJA: Rizik od mraza!")
                else:
                    st.error("Greška sa API ključem. Proverite da li je aktiviran.")
            except:
                st.error("Neuspešno povezivanje sa meteo servisom.")
        else:
            st.warning("Unesite API ključ levo za podatke o vremenu.")
