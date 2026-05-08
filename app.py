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

# Inicijalizacija memorije
if 'dnevnik' not in st.session_state: st.session_state.dnevnik = []
if 'troskovi' not in st.session_state: st.session_state.troskovi = []

st.title("🌾 AgroAsistent: Digitalni Savetnik i Dnevnik")

# 2. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    st.markdown("---")
    datum_sadnje = st.date_input("Kada si posadio glavni rasad?", datetime.now())
    if st.button("❌ Obriši sve podatke"):
        st.session_state.dnevnik = []
        st.session_state.troskovi = []
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Radar i Mapa", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka (3. godina)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"], key="v_m")
    
    baza_v = {
        "Mart": "🛡️ Bakar (50g/16L) pre pupoljaka. 🧪 KAN 27% (250g po stablu).",
        "April": "🌸 Signum (10g/16L) u cvetu. 🛡️ Score (5ml/16L) za krastavost.",
        "Maj": "🛡️ Captan (35g/16L). 🧪 Bor (20ml/10L) folijarno.",
        "Jun": "🐛 Coragen (3ml/16L). 🧪 Kalcijum (40ml/16L) protiv pucanja.",
        "Jul": "💦 Navodnjavanje! 🛡️ Envidor (10ml/16L) protiv grinja.",
        "Avgust": "🧺 Berba ranih sorti. 🛡️ Teldor (15ml/16L) pred berbu.",
        "Septembar": "🧺 Berba kasnih sorti. 🧹 Higijena: Skupljanje mumificiranih plodova.",
        "Oktobar": "🧪 Jesenje đubrenje (Fosfor i Kalijum). 🚜 Plitka obrada zemlje."
    }
    st.info(baza_v.get(v_mesec))
    
    v_rad = st.multiselect("Zapis rada:", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad u voćnjaku", key="v_btn"):
        if v_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m.%Y"), "Kultura": f"Voće ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Saveti za povrće")
    
    dana_od_sadnje = (datetime.now().date() - datum_sadnje).days
    st.subheader(f"🌱 Status rasada: {dana_od_sadnje} dana od sadnje")
    
    if dana_od_sadnje < 4:
        st.error("❗ **UKORENJAVANJE:** Ne prskaj ničim! Samo umereno zalivanje ujutru.")
    elif 4 <= dana_od_sadnje <= 10:
        st.warning("⚠️ **STABILIZACIJA:** Može blagi rastvor mleka (1:10). Bez sode bikarbone.")
    else:
        st.success("✅ **STABILNA BILJKA:** Možeš početi sa redovnom zaštitom.")

    st.markdown("---")
    tip = st.radio("Sistem:", ["Plastenik (16x5m)", "Otvoreno polje"], horizontal=True)
    povrce = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak"])

    baza_p = {
        "Krompir": "🌱 **Maj:** Nagrtanje zemlje i kontrola zlatice (traži narandžasta jaja pod listom). 🛡️ **Jun:** Glavna zaštita od plamenjače nakon svake kiše.",
        "Paradajz": "🌿 **Maj:** Ukorenjavanje i prva folijarna prihrana. ✂️ **Jun:** Intenzivno zakidanje zaperaka.",
        "Luk": "🐜 **Maj:** Zaštita od lukove muve. ⚠️ **Sparina:** Ako je vlažno, rizik od plamenjače luka!"
    }

    st.info(baza_p.get(povrce, "Pratite redovno stanje vlažnosti."))

    p_rad = st.multiselect("Urađeno:", ["Sadnja", "Zaštita", "Prihrana", "Berba"], key=f"p_{povrce}_{tip}")
    if st.button("Zabeleži rad u povrtnjaku", key="p_btn"):
        if p_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m.%Y"), "Kultura": f"{povrce} ({tip})", "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: RADAR I MAPA ---
with tab3:
    st.header("🛰️ Radar i Pametni Saveti")
    v_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(v_html, height=620)
    
    st.markdown("---")
    st.subheader("🗺️ Obeleži parcelu")
    m = folium.Map(location=[43.5616, 21.3694], zoom_start=15)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=450, key="agro_mapa_final")
    
    if izlaz_mape and izlaz_mape.get('last_clicked') and meteo_key:
        lat, lon = izlaz_mape['last_clicked']['lat'], izlaz_mape['last_clicked']['lng']
        try:
            url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key.strip()}&units=metric&lang=sr"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                d = res.json()
                vlaga = d['main']['humidity']
                temp = d['main']['temp']
                st.success(f"Vlaga: {vlaga}% | Temp: {temp}°C")
                if vlaga > 85 and temp < 20:
                    st.warning("⚠️ Velika sparina! Ne preteruj sa vodom i provetri plastenik.")
        except:
            st.warning("⚠️ Internet veza prekinuta. Koristi ručne kontrole.")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovnik")
    c1, c2, c3 = st.columns(3)
    stavka = c1.text_input("Stavka:")
    kol = c2.number_input("Količina:", min_value=1.0, value=1.0)
    cena = c3.number_input("Cena (RSD):", min_value=0.0)
    if st.button("Dodaj"):
        if stavka: st.session_state.troskovi.append({"Stavka": stavka, "Iznos": kol * cena})
    if st.session_state.troskovi:
        st.table(pd.DataFrame(st.session_state.troskovi))

# --- DNEVNIK NA DNU ---
st.markdown("---")
if st.session_state.dnevnik:
    df_d = pd.DataFrame(st.session_state.dnevnik)
    st.table(df_d)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_d.to_excel(writer, index=False)
    st.download_button("📥 Preuzmi Excel", data=output.getvalue(), file_name="agro_dnevnik.xlsx")
