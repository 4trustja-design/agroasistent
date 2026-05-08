import streamlit as st
from streamlit_folium import st_folium
import folium
import requests

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

st.title("🌾 Pametni Poljoprivredni Savetnik")

# Bočni meni za Meteo Ključ
with st.sidebar:
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    st.info("Ovaj ključ je potreban za prognozu uživo.")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# --- TAB 1 i 2 ostaju isti, fokusiramo se na TAB 3 ---

with tab3:
    st.header("📍 Lokacija i Vremenska Prognoza")
    st.write("Kliknite na svoju parcelu na mapi ispod:")

    # Kreiranje mape
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    m.add_child(folium.LatLngPopup())
    
    # Hvatanje klika na mapu
    izlaz_mape = st_folium(m, width=800, height=500)

    # Ako je korisnik kliknuo na mapu
    if izlaz_mape['last_clicked']:
        lat = izlaz_mape['last_clicked']['lat']
        lon = izlaz_mape['last_clicked']['lng']
        
        st.success(f"Izabrane koordinate: {lat:.4f}, {lon:.4f}")
        
        if meteo_key:
            # Pozivanje OpenWeather API-ja
            url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key}&units=metric&lang=sr"
            podaci = requests.get(url).json()
            
            if podaci.get("main"):
                temp = podaci["main"]["temp"]
                vlaznost = podaci["main"]["humidity"]
                opis = podaci["weather"][0]["description"]
                vetar = podaci["wind"]["speed"]
                
                # Prikaz prognoze u lepim karticama
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Temperatura", f"{temp}°C")
                col2.metric("Vlažnost", f"{vlaznost}%")
                col3.metric("Vetar", f"{vetar} m/s")
                col4.write(f"**Trenutno:** {opis.capitalize()}")
                
                # Agro savet na osnovu vremena
                if temp < 2:
                    st.warning("⚠️ OPREZ: Moguć mraz! Zaštitite mlade zasade.")
                if vetar > 5:
                    st.error("🚫 Nije preporučljivo prskanje zbog jačine vetra.")
                elif vlaznost > 80:
                    st.info("ℹ️ Visoka vlažnost: Povoljni uslovi za razvoj gljivičnih oboljenja.")
            else:
                st.error("Greška pri učitavanju prognoze. Proveri API ključ.")
        else:
            st.warning("Unesite API ključ u levom meniju da biste videli prognozu za ovu tačku.")
