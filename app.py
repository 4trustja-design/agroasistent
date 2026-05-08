import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
import requests
import io

# 1. OSNOVNA PODEŠAVANJA
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

# Inicijalizacija dnevnika i troškova
if 'dnevnik' not in st.session_state: st.session_state.dnevnik = []
if 'troskovi' not in st.session_state: st.session_state.troskovi = []

st.title("🌾 AgroAsistent: Digitalni Savetnik i Dnevnik")

# 2. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    if st.button("❌ Obriši sve podatke"):
        st.session_state.dnevnik = []
        st.session_state.troskovi = []
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Radar i Mapa", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka (3. godina)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust"], key="v_m")
    baza_v = {
        "Maj": "🛡️ **Zaštita:** Captan (35g na 16L). 🧪 **Ishrana:** Bor preko lista.",
        "Jun": "🐛 **Smotavac:** Coragen (3ml na 16L). 🧪 **Ishrana:** Kalcijum (40ml/16L)."
    }
    st.info(baza_v.get(v_mesec, "Pratite redovno stanje."))
    v_rad = st.multiselect("Zapis rada:", ["Prskanje", "Đubrenje", "Navodnjavanje"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad u voćnjaku", key="v_btn"):
        if v_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m.%Y"), "Kultura": f"Voće ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Saveti za povrće")
    tip = st.radio("Sistem:", ["Plastenik (16x5m)", "Otvoreno polje"], horizontal=True)
    kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica"])
    p_rad = st.multiselect("Urađeno:", ["Sadnja", "Zaštita", "Prihrana", "Berba"], key=f"p_{kultura}_{tip}")
    if st.button("Zabeleži rad u povrtnjaku", key="p_btn"):
        if p_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m.%Y"), "Kultura": f"{kultura} ({tip})", "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: RADAR, MAPA I PAMETNI SAVET (OTPORAN NA GREŠKE) ---
with tab3:
    st.header("🛰️ Vremenski radar uživo (Kruševac)")
    vreme_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(vreme_html, height=620)
    
    st.markdown("---")
    st.subheader("🗺️ Obeleži parcelu i proveri uslove")
    
    m = folium.Map(location=[43.5616, 21.3694], zoom_start=15)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=450, key="mapa_v15")
    
    # --- PAMETNA LOGIKA ZA SAVET ---
    st.markdown("### 📢 Agronomski savet za navodnjavanje i zaštitu")
    
    # Inicijalizacija vrednosti
    vlaga_za_savet = None
    temp_za_savet = None

    # Pokušaj povezivanja na internet
    if izlaz_mape and izlaz_mape.get('last_clicked') and meteo_key:
        lat, lon = izlaz_mape['last_clicked']['lat'], izlaz_mape['last_clicked']['lng']
        try:
            cist_kljuc = meteo_key.strip().replace(".", "")
            url = f"https://openweathermap.org{lat}&lon={lon}&appid={cist_kljuc}&units=metric&lang=sr"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                d = res.json()
                vlaga_za_savet = d['main']['humidity']
                temp_za_savet = d['main']['temp']
                st.success(f"Automatski podaci: Vlaga {vlaga_za_savet}%, Temp {temp_za_savet}°C")
        except:
            st.warning("⚠️ Trenutni problem sa internet vezom. Koristite ručni unos ispod za savet.")

    # Ručni unos kao REZERVNI PLAN (uvek vidljiv ako internet zakaže)
    if not vlaga_za_savet:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            temp_za_savet = st.number_input("Unesi temperaturu (°C):", value=15)
        with col_r2:
            vlaga_za_savet = st.slider("Unesi vlažnost vazduha (%):", 0, 100, 90)

    # ISPIS SAVETA (Radi i za automatiku i za ručni unos)
    if vlaga_za_savet and temp_za_savet:
        if vlaga_za_savet > 85 and temp_za_savet < 20:
            st.warning(f"**SAVET:** Trenutno je velika sparina (Vlaga {vlaga_za_savet}%). Ako sutra planiraš zalivanje, zemlja će već biti prilično vlažna, pa nemoj preterivati sa količinom vode iz onog kontejnera!")
        elif temp_za_savet > 30:
            st.error(f"**VRELA ZEMLJA:** Na {temp_za_savet}°C ne zalivaj hladnom vodom iz bunara! Biljke će doživeti šok.")
        elif 18 <= temp_za_savet <= 25 and 40 <= vlaga_za_savet <= 65:
            st.success("✅ **IDEALNO:** Uslovi su savršeni za redovne radove.")
        else:
            st.info("Uslovi su umereni. Prati stanje u plasteniku zbog rose.")


# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovnik (Creva, Seme, Preparati)")
    c1, c2, c3 = st.columns(3)
    with c1: stavka = st.text_input("Naziv stavke:")
    with c2: kol = st.number_input("Količina:", min_value=1.0, value=1.0)
    with c3: cena = st.number_input("Cena (RSD):", min_value=0.0, value=0.0)
    if st.button("Dodaj trošak"):
        if stavka:
            st.session_state.troskovi.append({"Stavka": stavka, "Iznos (RSD)": kol * cena})
            st.success(f"Dodato: {stavka}")

    if st.session_state.troskovi:
        df_t = pd.DataFrame(st.session_state.troskovi)
        st.table(df_t)
        st.subheader(f"Ukupno uloženo: {df_t['Iznos (RSD)'].sum():,.2f} RSD")

# --- DNEVNIK NA DNU ---
st.markdown("---")
if st.session_state.dnevnik:
    st.subheader("📓 Digitalna knjiga polja")
    df_d = pd.DataFrame(st.session_state.dnevnik)
    st.table(df_d)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_d.to_excel(writer, index=False, sheet_name='Dnevnik')
    st.download_button(label="📥 Preuzmi dnevnik (Excel)", data=output.getvalue(), file_name="agro_dnevnik.xlsx")
