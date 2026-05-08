import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime
import requests

# 1. Podešavanje stranice
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

# Inicijalizacija dnevnika
if 'dnevnik' not in st.session_state:
    st.session_state.dnevnik = []

st.title("🌾 AgroAsistent: Lični Savetnik sa Doziranjem")

# --- SAVETI O KARENCI I MEŠANJU ---
with st.expander("ℹ️ VAŽNO: Uputstvo za prskanje i Karenca"):
    st.markdown("""
    *   **Tvoja oprema:** Zaštita = **16L** (baterijska prskalica) | Ishrana = **10L** (kanta za polivanje).
    *   **Karenca:** Broj dana od prskanja do berbe. **Strogo se pridržavaj!**
    *   **Mešanje:** Prvo praškasti preparati (razmućeni u malo vode), pa tečni, pa prihrana.
    """)

# 2. Bočni meni
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("OpenWeather API Ključ:", type="password")
    if st.button("Obriši istoriju radova"):
        st.session_state.dnevnik = []
        st.rerun()

tab1, tab2, tab3 = st.tabs(["🍎 Voćnjak (3. god)", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust"], key="v_m")
    
    baza_v = {
        "Mart": "🛡️ **Zaštita:** Cuprozin (50g na 16L). 🧪 **Ishrana:** KAN (200g po stablu).",
        "April": "🌸 **Cvet:** Signum (10g na 16L). 🛡️ **Krastavost:** Score (5ml na 16L).",
        "Maj": "🛡️ **Zaštita:** Captan (35g na 16L). 🐜 **Vaši:** Teppeki (2g na 16L).",
        "Jun": "🐛 **Smotavac:** Coragen (3ml na 16L). 🧪 **Ishrana:** Kristalon (Kalcijum) 30g na 16L.",
        "Jul": "💦 **Navodnjavanje!** 🛡️ **Grinje:** Envidor (10ml na 16L).",
        "Avgust": "🛡️ **Pred berbu:** Teldor (15ml na 16L). Karenca: 3 dana."
    }
    st.info(baza_v.get(v_mesec))
    v_rad = st.multiselect("Zapis rada:", ["Prskanje", "Đubrenje", "Navodnjavanje"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad u voćnjaku", key="v_btn"):
        if v_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m."), "Kultura": f"Voćnjak ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Povrtarstvo: Doziranje i Karenca")
    tip = st.radio("Mesto uzgoja:", ["Plastenik", "Otvoreno polje"], horizontal=True)
    p_mesec = st.selectbox("Izaberi mesec:", ["Maj", "Jun", "Jul", "Avgust"], key="p_m")
    
    if tip == "Plastenik":
        kultura = st.selectbox("Povrće:", ["Paradajz", "Paprika", "Krastavac"])
        baza_p = {
            "Paradajz": {
                "Maj": "🧪 **Ishrana (10L):** Fitofert Calcium (30ml). 🐜 **Vaši:** Laser (8ml na 16L). Karenca: 3 dana.",
                "Jun": "⚠️ **Plamenjača:** Ridomil Gold (40g na 16L). Karenca: 21 dan. (Pred berbu Quadris - 3 dana).",
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
        kultura = st.selectbox("Povrće:", ["Krompir", "Lubenica", "Luk", "Grašak", "Boranija", "Bundeva"])
        baza_p = {
            "Krompir": {
                "Maj": "🐞 **Zlatica:** Coragen (3ml na 16L). 🚜 **Nagrtanje.**",
                "Jun": "⚠️ **PLAMENJAČA (posle kiše):** Ridomil Gold (40g na 16L). Karenca: 21 dan.",
                "Jul": "🛡️ **Plamenjača:** Revus (10ml na 16L). Karenca: 7 dana.",
                "Avgust": "🧺 **Vađenje krompira.**"
            },
            "Luk": {
                "Maj": "⚠️ **Plamenjača:** Ridomil Gold R (50g na 16L). 🐜 **Muva:** Mospilan (4g na 16L).",
                "Jun": "🛡️ **Zaštita:** Quadris (15ml na 16L). Karenca: 7 dana.",
                "Jul": "🧺 **Vađenje luka kada polegne list.**"
            },
            "Lubenica": {
                "Jun": "🛡️ **Plamenjača:** Quadris (15ml na 16L). 🐜 **Vaši:** Confidor (5ml na 16L).",
                "Jul": "🧪 **Ishrana:** Fitofert Kalijum (30g na 10L). 💦 **Zalivanje!**"
            }
        }

    # Prikaz saveta
    info = baza_p.get(kultura, {}).get(p_mesec, "Nema specifičnih podataka za ovaj mesec.")
    st.warning(f"📌 **{kultura} ({p_mesec}):** {info}")
    
    p_rad = st.multiselect("Urađeno:", ["Zalivanje sa prihranom", "Zaštita (Prskanje)", "Berba"], key=f"p_r_{kultura}_{p_mesec}")
    if st.button("Zapiši rad u povrtnjaku", key="p_btn"):
        if p_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m."), "Kultura": f"{kultura} ({p_mesec})", "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: MAPA ---
with tab3:
    st.header("📍 Moja Parcela")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=450, key="agro_mapa")
    if izlaz_mape and izlaz_mape.get('last_clicked'):
        lat, lon = izlaz_mape['last_clicked']['lat'], izlaz_mape['last_clicked']['lng']
        st.success(f"Koordinate: {lat:.4f}, {lon:.4f}")
        if meteo_key:
            url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key}&units=metric&lang=sr"
            d = requests.get(url).json()
            if "main" in d:
                st.metric("Temperatura", f"{d['main']['temp']} °C")
                st.write(f"**Vreme:** {d['weather'][0]['description']}")

# --- PRIKAZ DNEVNIKA ---
st.markdown("---")
st.subheader("📓 Dnevnik radova (Istorija)")
if st.session_state.dnevnik:
    st.table(st.session_state.dnevnik)
else:
    st.write("Dnevnik je prazan.")
