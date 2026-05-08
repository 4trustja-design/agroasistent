import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
from datetime import datetime

# 1. Podešavanje stranice
st.set_page_config(page_title="AgroSavetnik Pro", layout="wide", page_icon="🌾")

# Inicijalizacija dnevnika u memoriji
if 'dnevnik' not in st.session_state:
    st.session_state.dnevnik = []

# 2. Bočni meni
with st.sidebar:
    st.header("🔑 Ključevi")
    ai_key = st.text_input("Gemini AI Ključ:", type="password")
    meteo_key = st.text_input("OpenWeather Ključ:", type="password")
    st.markdown("---")
    if st.button("Obriši dnevnik"):
        st.session_state.dnevnik = []
        st.rerun()

st.title("🌾 AgroAsistent: Lični Agronom")

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "🤖 Pitaj Agronoma", "📍 Mapa i Prognoza"])

# FUNKCIJA ZA AI - SADA POTPUNO SIGURNA
def pozovi_ai(pitanje):
    # Razdvajamo adresu i ključ da se više nikada ne spoje u grešci
    url_baza = "https://googleapis.com"
    parametri = {'key': ai_key.strip()}
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": pitanje}]}]}
    
    try:
        r = requests.post(url_baza, headers=headers, params=parametri, json=data)
        if r.status_code == 200:
            return r.json()['candidates']['content']['parts']['text']
        else:
            return f"Greška sa servera (Kod {r.status_code}): {r.text}"
    except Exception as e:
        return f"Greška u povezivanju: {str(e)}"

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Plan za voćnjak")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik"])
    with v_col2:
        godina = st.slider("Godina zasada:", 0, 5, 1)
    
    c1, c2 = st.columns(2)
    with c1:
        zastita = st.checkbox("Urađeno prskanje (Bakar/Plavo ulje)", key=f"v_z_{voce}_{godina}")
    with c2:
        ishrana = st.checkbox("Urađeno đubrenje", key=f"v_i_{voce}_{godina}")

    if st.button("Zapiši radove u voćnjaku", key="v_save"):
        vreme = datetime.now().strftime("%d.%m.%Y %H:%M")
        radovi = []
        if zastita: radovi.append("Zaštita")
        if ishrana: radovi.append("Ishrana")
        if radovi:
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": voce, "Radovi": ", ".join(radovi)})
            st.success("Zabeleženo u dnevnik!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Plan za povrtnjak")
    povrce = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika", "Krastavac", "Kupus"])
    tip = st.radio("Način uzgoja:", ["Plastenik", "Otvoreno polje"], horizontal=True)
    
    p_zastita = st.checkbox("Urađena zaštita", key=f"p_z_{povrce}_{tip}")
    p_ishrana = st.checkbox("Urađena prihrana", key=f"p_i_{povrce}_{tip}")

    if st.button("Zapiši radove u povrtnjaku", key="p_save"):
        vreme = datetime.now().strftime("%d.%m.%Y %H:%M")
        radovi = []
        if p_zastita: radovi.append("Zaštita")
        if p_ishrana: radovi.append("Prihrana")
        if radovi:
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": f"{povrce} ({tip})", "Radovi": ", ".join(radovi)})
            st.success("Zabeleženo u dnevnik!")

# --- TAB 3: PITANJA ZA AI ---
with tab3:
    st.header("🤖 Konsultacije sa AI Agronomom")
    pitanje = st.text_area("Vaše pitanje o bolestima ili preparatima:")
    if st.button("Pitaj"):
        if ai_key:
            with st.spinner("AI razmišlja..."):
                odgovor = pozovi_ai(f"Kao agronom iz Srbije, odgovori na: {pitanje}")
                st.markdown(odgovor)
        else:
            st.error("Prvo unesite AI ključ u meni levo!")

# --- TAB 4: MAPA I PROGNOZA ---
with tab4:
    st.header("📍 Moja Parcela")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=450, key="agromapa_pro")

    if izlaz_mape and izlaz_mape.get('last_clicked'):
        lat, lon = izlaz_mape['last_clicked']['lat'], izlaz_mape['last_clicked']['lng']
        st.success(f"Lokacija: {lat:.4f}, {lon:.4f}")
        
        if meteo_key:
            url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key}&units=metric&lang=sr"
            data = requests.get(url).json()
            if "main" in data:
                st.metric("Temperatura", f"{data['main']['temp']} °C")
                st.write(f"**Vreme:** {data['weather'][0]['description']}")
            else: st.error("Meteo ključ neispravan.")

# --- PRIKAZ DNEVNIKA ---
st.markdown("---")
st.subheader("📓 Istorija radova (Dnevnik)")
if st.session_state.dnevnik:
    st.table(st.session_state.dnevnik)
else:
    st.write("Dnevnik je trenutno prazan.")
