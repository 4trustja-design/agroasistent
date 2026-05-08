import streamlit as st
from streamlit_folium import st_folium
import folium
import requests

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

st.title("🌾 Pametni Poljoprivredni Savetnik")

with st.sidebar:
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    st.info("Ključ dobijaš besplatno na OpenWeatherMap sajtu.")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# ... (Tab 1 i 2 ostaju isti) ...

with tab3:
    st.header("📍 Lokacija i Vremenska Prognoza")
    st.write("Kliknite na svoju parcelu na mapi:")

    # 1. Kreiranje mape
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    m.add_child(folium.LatLngPopup())
    
    # 2. Prikaz mape i hvatanje izlaza
    izlaz_mape = st_folium(m, width=800, height=500, key="agromapa")

    # 3. PROVERA: Radi samo ako je korisnik KLIKNUO
    if izlaz_mape.get('last_clicked'):
        lat = izlaz_mape['last_clicked']['lat']
        lon = izlaz_mape['last_clicked']['lng']
        
        st.success(f"Izabrana lokacija: {lat:.4f}, {lon:.4f}")
        
        # Tek sada, ako imamo ključ, tražimo vreme
        if meteo_key:
            try:
                url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key}&units=metric&lang=sr"
                response = requests.get(url)
                podaci = response.json()
                
                if response.status_code == 200:
                    temp = podaci["main"]["temp"]
                    vlaznost = podaci["main"]["humidity"]
                    vetar = podaci["wind"]["speed"]
                    opis = podaci["weather"][0]["description"]
                    
                    # Prikaz u karticama
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Temperatura", f"{temp}°C")
                    c2.metric("Vlažnost", f"{vlaznost}%")
                    c3.metric("Vetar", f"{vetar} m/s")
                    st.write(f"**Trenutno stanje:** {opis.capitalize()}")
                    
                    # Agro preporuke
                    if temp < 2: st.error("❄️ Opasnost od mraza!")
                    if vetar > 5: st.warning("💨 Vetar je prejak za prskanje.")
                else:
                    st.error(f"Problem sa API ključem: {podaci.get('message', 'Greška')}")
            except Exception as e:
                st.error(f"Greška u povezivanju: {e}")
        else:
            st.warning("Unesite API ključ u levom meniju za detaljnu prognozu.")
