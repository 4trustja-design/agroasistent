import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

if 'dnevnik' not in st.session_state:
    st.session_state.dnevnik = []

st.title("🌾 AgroAsistent: Lični Savetnik sa Preparatima")

tab1, tab2, tab3 = st.tabs(["🍎 Voćnjak (3. god)", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# --- TAB 1: MEŠOVITI VOĆNJAK ---
with tab1:
    st.header("🍎 Saveti i Preparati za Voćnjak")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust"], key="v_m")
    
    baza_v = {
        "Mart": "🛡️ **Zaštita:** Plavo prskanje (Bakar). Preparati: **Cuprozin, Bakarni kreč ili Everest**. 🧪 **Ishrana:** KAN 27% (oko 200g po stablu).",
        "April": "🌸 **Cvetanje (Monilija):** **Chorus, Signum ili Switch**. 🛡️ **Čađava krastavost:** **Score ili Chorus**. 🐜 **Vaši:** **Teppeki ili Perfectthion**.",
        "Maj": "🛡️ **Zaštita:** **Mancogal ili Captan**. 🐜 **Rutava buba:** Postavljanje plavih posuda sa vodom (bez hemije u cvetu). 🧪 **Prihrana:** **Wuxal Ascofol** (preko lista).",
        "Jun": "🛡️ **Smotavac:** **Coragen ili Affirm**. 🍄 **Pepelnica:** **Luna Experience ili Topas**. 🧪 **Prihrana:** **Kristalon (Kalcijum)** za čvrstinu ploda.",
        "Jul": "💦 **Navodnjavanje:** Obavezno! 🛡️ **Grinje:** **Envidor ili Ortus**. 🍎 **Trulež:** **Switch ili Geox** (voditi računa o karenti).",
        "Avgust": "🛡️ **Pred berbu:** **Teldor ili Bellis** (kratka karenca). 🧺 **Higijena:** Skupljanje opalih plodova."
    }
    st.info(baza_v[v_mesec])
    v_rad = st.multiselect("Zapis rada:", ["Prskanje", "Đubrenje", "Navodnjavanje"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad", key="v_btn"):
        if v_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m."), "Kultura": f"Voćnjak ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Saveti i Preparati za Povrće")
    tip = st.radio("Mesto uzgoja:", ["Plastenik", "Otvoreno polje"], horizontal=True)
    p_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust"], key="p_m")
    
    if tip == "Plastenik":
        kultura = st.selectbox("Povrće:", ["Paradajz", "Paprika", "Krastavac"])
        baza_p = {
            "Paradajz": {
                "April": "🌿 **Pinciranje:** Zakidanje zaperaka. 🛡️ **Plesan:** **Signum ili Quadris**.",
                "Maj": "🧪 **Ishrana:** **Fitofert Calcium Organo** (protiv crne pege na vrhu ploda). 🐜 **Trips:** **Exirel ili Laser**.",
                "Jun": "⚠️ **Plamenjača:** **Ridomil Gold ili Infinito**. 🛡️ **Pepelnica:** **Topas**.",
                "Jul": "🧺 **Berba:** Voditi računa o karenti! 💦 **Zalivanje:** Svaki drugi dan."
            },
            "Paprika": {
                "Maj": "🐜 **Vaši i Trips:** **Actara ili Vertical**. 🧪 **Prihrana:** **Kristalon Zeleni** (NPK 20:20:20).",
                "Jun": "🛡️ **Bakterioze:** **Funguran ili Cuprablau** (manje doze bakra). 💦 **Vlažnost:** Orošavanje staza.",
                "Jul": "🌶️ **Berba:** Prihrana kalijumom (**Kristalon Crveni**) za boju i težinu."
            },
            "Krastavac": {
                "Maj": "🛡️ **Plamenjača:** **Equation Pro ili Aliette**. 🛡️ **Pepelnica:** **Nimrod**.",
                "Jun": "🐜 **Grinje (Crveni pauk):** **Abastate ili Envidor**. 🧺 **Berba:** Svakodnevno.",
                "Jul": "🧪 **Prihrana:** **Wuxal Super** folijarno za kondiciju vreže."
            }
        }
    else:
        kultura = st.selectbox("Povrće:", ["Krompir", "Lubenica", "Beli luk", "Crni luk", "Bundeva", "Grašak", "Boranija"])
        baza_p = {
            "Krompir": {
                "Maj": "🐞 **Zlatica:** **Coragen, Alverde ili Mospilan**. 🚜 **Nagrtanje:** Obavezno.",
                "Jun": "⚠️ **PLAMENJAČA (posle kiše):** **Ridomil Gold, Consento ili Revus**. 🛡️ **Crna pegavost:** **Antracol**.",
                "Jul": "💦 **Navodnjavanje:** Presudno za prinos. 🐜 **Moljac:** **Decis**."
            },
            "Lubenica": {
                "Jun": "🛡️ **Plamenjača:** **Bravo ili Quadris**. 🐜 **Vaši:** **Confidor**. 🐝 **Pčele:** Ne prskati u toku dana!",
                "Jul": "🧪 **Prihrana:** **Fitofert Kristal Kalijum**. 💦 **Zalivanje:** Intenzivno ujutru."
            },
            "Crni luk": {
                "Maj": "⚠️ **Plamenjača:** **Ridomil Gold MZ ili Ridomil Gold R**. 🐜 **Muva:** **Mospilan**.",
                "Jun": "🛡️ **Rđa:** **Zato ili Score**. 🚜 **Korov:** Ručno čišćenje u ovoj fazi."
            },
            "Boranija": {
                "Jun": "🛡️ **Rđa:** **Mancogal**. 🐜 **Vaši:** **Afinex**. 🧺 **Berba:** Česta berba stimuliše cvetanje.",
                "Jul": "💦 **Navodnjavanje:** Obavezno u fazi cvetanja. 🛡️ **Grinje:** **Akaristop**."
            }
        }

    # Prikaz saveta (dodata provera da li postoji podatak za taj mesec)
    mesecni_savet = baza_p.get(kultura, {}).get(p_mesec, "Nema specifičnih preporuka za ovaj mesec, pratite opšte stanje biljke.")
    st.warning(f"📌 **{kultura} ({p_mesec}):** {mesecni_savet}")
    
    p_rad = st.multiselect("Urađeno:", ["Sadnja", "Zaštita", "Prihrana", "Berba"], key=f"p_r_{kultura}_{p_mesec}")
    if st.button("Zapiši rad", key="p_btn"):
        if p_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m."), "Kultura": f"{kultura} ({p_mesec})", "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: MAPA ---
with tab3:
    st.header("📍 Moja Parcela")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    st_folium(m, width=800, height=450, key="agro_mapa")

# --- DNEVNIK ---
st.markdown("---")
st.subheader("📓 Dnevnik radova")
if st.session_state.dnevnik:
    st.table(st.session_state.dnevnik)
    if st.button("Obriši istoriju"):
        st.session_state.dnevnik = []
        st.rerun()
