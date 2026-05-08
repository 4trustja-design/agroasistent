import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
from datetime import datetime

# 1. Konfiguracija
st.set_page_config(page_title="AgroSavetnik Pro", layout="wide", page_icon="🌾")

# Inicijalizacija dnevnika u memoriji aplikacije
if 'dnevnik' not in st.session_state:
    st.session_state.dnevnik = []

# 2. Bočni meni za ključeve
with st.sidebar:
    st.header("🔑 Pristupni Ključevi")
    ai_key = st.text_input("Gemini AI Ključ:", type="password")
    meteo_key = st.text_input("OpenWeather Ključ:", type="password")
    st.markdown("---")
    if st.button("Obriši dnevnik"):
        st.session_state.dnevnik = []
        st.rerun()

st.title("🌾 AgroAsistent: Lični Agronom")

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "🤖 Pitaj Agronoma", "📍 Mapa i Prognoza"])

# Pomoćna funkcija za AI
def pitaj_ai(pitanje):
    if not ai_key:
        return "Greska: Niste uneli AI ključ!"
    
    # Direktna i najstabilnija putanja koju smo ranije koristili
    url = f"https://googleapis.com{ai_key.strip()}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": pitanje}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            res_json = response.json()
            return res_json['candidates']['content']['parts']['text']
        else:
            return f"Greška sa servera (Kod {response.status_code}): {response.text}"
    except Exception as e:
        return f"Greška u povezivanju: {str(e)}"


# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Plan za voćnjak")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        voce = st.selectbox("Voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik"])
    with v_col2:
        godina = st.slider("Godina zasada:", 0, 5, 1)
    
    c1, c2 = st.columns(2)
    with c1:
        zastita = st.checkbox("Urađeno tretiranje (Bakar/Plavo ulje)", key=f"v_z_{voce}_{godina}")
    with c2:
        ishrana = st.checkbox("Urađeno prolećno đubrenje", key=f"v_i_{voce}_{godina}")

    if st.button("Zapiši u dnevnik", key="v_dugme"):
        vreme = datetime.now().strftime("%d.%m.%Y %H:%M")
        radovi = []
        if zastita: radovi.append("Zaštita")
        if ishrana: radovi.append("Ishrana")
        if radovi:
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": voce, "Radovi": ", ".join(radovi)})
            st.success("Zabeleženo!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Plan za povrtnjak")
    povrce = st.selectbox("Povrće:", ["Paradajz", "Paprika", "Krastavac", "Kupus"])
    tip = st.radio("Uzgoj:", ["Plastenik", "Otvoreno polje"], horizontal=True)
    
    p_zastita = st.checkbox("Urađena zaštita od plamenjače", key=f"p_z_{povrce}")
    p_ishrana = st.checkbox("Folijarna prihrana (Kalcijum/Aminokiseline)", key=f"p_i_{povrce}")

    if st.button("Zapiši u dnevnik", key="p_dugme"):
        vreme = datetime.now().strftime("%d.%m.%Y %H:%M")
        radovi = []
        if p_zastita: radovi.append("Zaštita")
        if p_ishrana: radovi.append("Prihrana")
        if radovi:
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": f"{povrce} ({tip})", "Radovi": ", ".join(radovi)})
            st.success("Zabeleženo!")

# --- TAB 3: PITANJA ZA AI ---
with tab3:
    st.header("🤖 Konsultacije sa AI Agronomom")
    st.write("Postavite pitanje o bolestima, štetočinama ili specifičnim preparatima.")
    pitanje = st.text_area("Vaše pitanje (npr. Zašto se list paradajza uvija?):")
    if st.button("Pitaj"):
        if ai_key:
            with st.spinner("Agronom razmišlja..."):
                odgovor = pitaj_ai(f"Kao stručni agronom iz Srbije, odgovori na pitanje: {pitanje}")
                st.markdown(odgovor)
        else:
            st.warning("Unesite Gemini AI ključ u meni sa strane.")

# --- TAB 4: MAPA I PROGNOZA ---
with tab3: # (Kod za mapu ostaje isti kao onaj koji nam je radio)
    pass # Ovde ide onaj prethodni kod za mapu koji si već testirao

# --- PRIKAZ DNEVNIKA NA DNU ---
st.markdown("---")
st.subheader("📓 Dnevnik polja (Istorija radova)")
if st.session_state.dnevnik:
    st.table(st.session_state.dnevnik)
else:
    st.write("Dnevnik je prazan. Označite radove iznad i kliknite na 'Zapiši'.")
