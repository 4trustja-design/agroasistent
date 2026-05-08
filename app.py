import streamlit as st
from streamlit_folium import st_folium
import folium
import requests

# 1. Podešavanje stranice
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide", page_icon="🌾")

st.title("🌾 Pametni Poljoprivredni Savetnik")

# Bočni meni za API ključ
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    st.info("Ključ je potreban za prognozu uživo u Tabu 3.")

# Kreiranje tabova
tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("Saveti za voćare (0-5 god)")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik"])
    with v_col2:
        godina = st.slider("Starost sadnice (god):", 0, 5, 1)
    
    st.info(f"📍 Kalendar za: {voce} | Godina: {godina}")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🛡️ Zaštita")
        st.write("- Plavo prskanje (faza mirovanja)")
        # Ključ (key) se menja čim promeniš voće ili godinu, što resetuje checkbox
        zastita_uradjena = st.checkbox("Urađeno tretiranje", key=f"v_zast_{voce}_{godina}")
    with c2:
        st.subheader("🧪 Prehrana")
        st.write("- Osnovno đubrenje (NPK)")
        ishrana_uradjena = st.checkbox("Urađeno đubrenje", key=f"v_ishr_{voce}_{godina}")

    if st.button("Sačuvaj dnevnik za voće"):
        if zastita_uradjena or ishrana_uradjena:
            st.success(f"Zapisano u dnevnik: Radovi na {voce} ({godina}. god) su evidentirani!")
        else:
            st.warning("Niste označili nijedan završen rad.")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("Saveti za povrtare")
    tip = st.radio("Uzgoj:", ["Plastenik", "Otvoreno polje"], horizontal=True)
    povrce = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika", "Krastavac", "Kupus"])
    
    st.success(f"📑 Preporuke za: {povrce} ({tip})")
    
    # Resetuje se čim promeniš vrstu povrća ili način uzgoja
    rasad = st.checkbox("Rasad spreman za sadnju", key=f"p_rasad_{povrce}_{tip}")
    navodnjavanje = st.checkbox("Postavljen sistem kap po kap", key=f"p_navod_{povrce}_{tip}")
    zastita_p = st.checkbox("Urađena preventivna zaštita", key=f"p_zast_{povrce}_{tip}")

    if st.button("Potvrdi završene radove u povrtnjaku"):
        st.write(f"Sistemska beleška: {povrce} ({tip}) - Provereno.")

# --- TAB 3: MOJA PARCELA ---
with tab3:
    st.header("📍 Lokacija i Vremenska Prognoza")
    st.write("Kliknite na mapu gde se nalazi vaša parcela:")

    # Mapa centrirana na Srbiju
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    
    # Prikaz mape
    izlaz_mape = st_folium(m, width=800, height=450, key="agro_mapa_srbija")

    # Ako je korisnik kliknuo na mapu
    if izlaz_mape and izlaz_mape.get('last_clicked'):
        lat = izlaz_mape['last_clicked']['lat']
        lon = izlaz_mape['last_clicked']['lng']
        
        st.success(f"Koordinate vaše parcele: {lat:.4f}, {lon:.4f}")
        
        if meteo_key:
            try:
                url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key}&units=metric&lang=sr"
                res = requests.get(url)
                data = res.json()
                
                if res.status_code == 200:
                    temp = data["main"]["temp"]
                    vlaznost = data["main"]["humidity"]
                    vetar = data["wind"]["speed"]
                    opis = data["weather"][0]["description"]
                    
                    st.markdown("### 🌤️ Trenutna prognoza za lokaciju")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Temperatura", f"{temp} °C")
                    c2.metric("Vlažnost", f"{vlaznost} %")
                    c3.metric("Vetar", f"{vetar} m/s")
                    st.write(f"**Vreme:** {opis.capitalize()}")
                    
                    # Agro upozorenja
                    if temp < 2: st.error("⚠️ PAŽNJA: Opasnost od mraza!")
                    if vetar > 5: st.warning("💨 Prejak vetar za prskanje.")
                else:
                    st.error("Problem sa API ključem. Proverite da li je aktiviran na sajtu.")
            except:
                st.error("Greška pri povezivanju sa meteo servisom.")
        else:
            st.warning("Unesite OpenWeather API ključ u levom meniju da biste videli prognozu.")
