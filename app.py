import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime
import requests
import pandas as pd
import io

# 1. OSNOVNA PODEŠAVANJA
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

# Inicijalizacija dnevnika u memoriji
if 'dnevnik' not in st.session_state:
    st.session_state.dnevnik = []

st.title("🌾 AgroAsistent: Digitalni Dnevnik i Savetnik")

# --- INFO PANEL ---
with st.expander("ℹ️ UPUTSTVO ZA RAD (Karenca i Doziranje)"):
    st.markdown("""
    *   **Tvoja oprema:** Zaštita = **16L** (baterijska prskalica) | Ishrana = **10L** (kanta).
    *   **KARENCA:** Obavezan broj dana od prskanja do berbe!
    *   **Mešanje:** Prvo praškasti (razmućeni u malo vode), pa tečni, pa prihrana.
    """)

# 2. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("OpenWeather API Ključ:", type="password")

tab1, tab2, tab3 = st.tabs(["🍎 Mešoviti Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka (3. godina)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar"], key="v_m")
    
    baza_v = {
        "Mart": "🛡️ **Zaštita:** Cuprozin (50g na 16L). 🧪 **Ishrana:** KAN 27% (200g po stablu).",
        "April": "🌸 **Cvet:** Signum (10g na 16L). 🛡️ **Krastavost:** Score (5ml na 16L). **Karenca:** 14 dana.",
        "Maj": "🛡️ **Zaštita:** Captan (35g na 16L). 🐜 **Vaši:** Teppeki (2g na 16L). **Karenca:** 21 dan.",
        "Jun": "🐛 **Smotavac:** Coragen (3ml na 16L). 🧪 **Ishrana:** Kristalon Kalcijum (30g na 16L).",
        "Jul": "💦 **Navodnjavanje!** 🛡️ **Grinje:** Envidor (10ml na 16L). **Karenca:** 14-21 dan.",
        "Avgust": "🛡️ **Pred berbu:** Teldor (15ml na 16L). **Karenca:** 3 dana.",
        "Septembar": "🧺 **Berba.** 🧪 **Ishrana:** Jesenje đubrenje NPK 6:12:24 (300g po stablu)."
    }
    st.info(baza_v.get(v_mesec))
    v_rad = st.multiselect("Završen rad:", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad u voćnjaku", key="v_btn"):
        if v_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m.%Y"), "Kultura": f"Voćnjak ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Povrtarstvo: Detaljni Saveti")
    tip = st.radio("Mesto uzgoja:", ["Plastenik", "Otvoreno polje"], horizontal=True)
    p_mesec = st.selectbox("Izaberi mesec:", ["Maj", "Jun", "Jul", "Avgust"], key="p_m")
    
    if tip == "Plastenik":
        kultura = st.selectbox("Povrće:", ["Paradajz", "Paprika", "Krastavac"])
        baza_p = {
            "Paradajz": {
                "Maj": "🧪 **Ishrana (10L):** Fitofert Calcium (30ml). 🐜 **Vaši:** Laser (8ml na 16L). Karenca: 3 dana.",
                "Jun": "⚠️ **Plamenjača:** Ridomil Gold (40g na 16L). Karenca: 21 dan. 🌿 **Radovi:** Pinciranje.",
                "Jul": "🛡️ **Trulež:** Switch (10g na 16L). Karenca: 3 dana. 🧪 **Ishrana:** Kristalon Crveni (20g na 10L).",
                "Avgust": "🧺 **Berba.** ✂️ Skidanje donjih listova radi provetravanja."
            },
            "Paprika": {
                "Maj": "🌱 **Koren:** Fitofert Humisuper (30ml na 10L). 🐜 **Trips:** Vertical (10ml na 16L). Karenca: 7 dana.",
                "Jun": "🛡️ **Bakterioza:** Bakarni kreč (30g na 16L). Karenca: 14 dana. 🧪 **Ishrana:** Kristalon Zeleni (20g na 10L).",
                "Jul": "🧪 **Ishrana (10L):** Kristalon Crveni (25g). 🐜 **Vaši:** Afinex (5g na 16L). Karenca: 7 dana.",
                "Avgust": "🌶️ **Berba.** 🐜 **Bela vaši:** Chess (6g na 16L). Karenca: 7 dana."
            },
            "Krastavac": {
                "Maj": "🌿 **Vođenje na kanap.** 🛡️ **Pepelnica:** Nimrod (10ml na 16L). Karenca: 3 dana.",
                "Jun": "⚠️ **Plamenjača:** Equation Pro (10g na 16L). Karenca: 3 dana. 🐜 **Grinje:** Abastate (15ml na 16L).",
                "Jul": "🧺 **Berba.** 🧪 **Ishrana (10L):** Wuxal Super (30ml) - folijarno.",
                "Avgust": "✂️ Uklanjanje starih listova. 🛡️ **Grinje:** Envidor (10ml na 16L)."
            }
        }
    else:
        kultura = st.selectbox("Povrće:", ["Krompir", "Lubenica", "Beli luk", "Crni luk", "Bundeva", "Grašak", "Boranija"])
        baza_p = {
            "Krompir": {
                "Maj": "🐞 **Zlatica:** Coragen (3ml na 16L). 🚜 **Nagrtanje.**",
                "Jun": "⚠️ **PLAMENJAČA (posle kiše):** Ridomil Gold (40g na 16L). Karenca: 21 dan.",
                "Jul": "🛡️ **Plamenjača:** Revus (10ml na 16L). Karenca: 7 dana. 💦 **Zalivanje!**",
                "Avgust": "🧺 **Vađenje.**"
            },
            "Lubenica": {
                "Maj": "🌱 **Ukorenjavanje:** Humisuper (30ml na 10L). 🛡️ **Bakterioza:** Bakarni kreč (30g na 16L).",
                "Jun": "🛡️ **Plamenjača:** Quadris (15ml na 16L). Karenca: 3 dana. 🐜 **Vaši:** Confidor (5ml na 16L).",
                "Jul": "🧪 **Ishrana:** Kristalon Crveni (25g na 10L). 💦 **Zalivanje ujutru.**",
                "Avgust": "🍉 Smanjiti zalivanje radi šećera."
            },
            "Beli luk": {
                "Maj": "🛡️ **Plamenjača:** Ridomil Gold R (50g na 16L). 🧪 **Ishrana:** KAN (15g po m2).",
                "Jun": "🧺 **Vađenje:** Kada listovi požute 2/3. Sušenje na promaji."
            },
            "Crni luk": {
                "Maj": "⚠️ **Plamenjača:** Ridomil Gold MZ (40g na 16L). 🐜 **Muva:** Mospilan (4g na 16L).",
                "Jun": "🛡️ **Zaštita:** Quadris (15ml na 16L). Karenca: 7 dana.",
                "Jul": "🧺 **Vađenje luka.**"
            },
            "Bundeva": {
                "Jun": "🌿 **Radovi:** Okopavanje. 🧪 **Ishrana:** NPK 20:20:20 (20g na 10L).",
                "Jul": "🛡️ **Pepelnica:** Topas (5ml na 16L). Karenca: 7 dana. 💦 **Navodnjavanje!**"
            },
            "Grašak": {
                "Maj": "🌸 **Cvetanje:** Obavezno zalivanje! 🐜 **Žižak:** Fastac (3ml na 16L). Karenca: 14 dana."
            },
            "Boranija": {
                "Jun": "🌱 **Setva (drugi rok).** 🛡️ **Rđa:** Mancogal (30g na 16L). Karenca: 14 dana.",
                "Jul": "🧺 **Berba svaka 2 dana.** 💦 **Zalivanje** u cvetu."
            }
        }

    info = baza_p.get(kultura, {}).get(p_mesec, "Pratite opšte stanje biljke.")
    st.warning(f"📌 **{kultura} ({p_mesec}):** {info}")
    
    p_rad = st.multiselect("Urađeno:", ["Zalivanje/Prihrana", "Zaštita (Prskanje)", "Berba", "Okopavanje"], key=f"p_r_{kultura}_{p_mesec}_{tip}")
    if st.button("Zapiši rad u povrtnjaku", key="p_btn"):
        if p_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m.%Y"), "Kultura": f"{kultura} ({p_mesec})", "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: MAPA ---
with tab3:
    st.header("📍 Moja Parcela")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=450, key="agro_mapa_final")
    if izlaz_mape and izlaz_mape.get('last_clicked'):
        lat, lon = izlaz_mape['last_clicked']['lat'], izlaz_mape['last_clicked']['lng']
        st.success(f"Koordinate: {lat:.4f}, {lon:.4f}")
        if meteo_key:
            url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key}&units=metric&lang=sr"
            d = requests.get(url).json()
            if "main" in d:
                st.metric("Temperatura", f"{d['main']['temp']} °C")
                st.write(f"**Vreme:** {d['weather']['description']}")

# --- DNEVNIK I PREUZIMANJE ---
st.markdown("---")
st.subheader("📓 Digitalna knjiga polja")

if st.session_state.dnevnik:
    df = pd.DataFrame(st.session_state.dnevnik)
    st.dataframe(df, use_container_width=True)
    
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='xlsxwriter')
    towrite.seek(0)
    
    col_dl, col_del = st.columns(2)
    with col_dl:
        st.download_button(
            label="📥 Preuzmi dnevnik (Excel)",
            data=towrite,
            file_name=f"agro_dnevnik_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col_del:
        if st.button("❌ Obriši sve zapise"):
            st.session_state.dnevnik = []
            st.rerun()
else:
    st.info("Dnevnik je prazan. Zabeležite radove iznad.")
