import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

if 'dnevnik' not in st.session_state:
    st.session_state.dnevnik = []

st.title("🌾 AgroAsistent: Lični Savetnik sa Doziranjem")

# --- SAVET ZA MEŠANJE I KARENCU (FIKSNI INFO) ---
with st.expander("ℹ️ Uputstvo za mešanje i Karenca (Pročitaj pre rada)"):
    st.markdown("""
    *   **Šta je KARENCA?** To je broj dana koji mora proći od prskanja do berbe. **Strogo se pridržavaj ovoga!**
    *   **Redosled mešanja u prskalici:** 
        1. Napuni prskalicu do pola vodom.
        2. Dodaj praškaste preparate (razmuti ih prvo u malo vode).
        3. Dodaj tečne preparate.
        4. Dodaj prihranu (đubrivo).
        5. Dopuni vodom do vrha i dobro promućkaj.
    *   **Tvoja oprema:** 
        *   Zaštita (16L baterijska): Doze su izračunate za punu prskalicu.
        *   Ishrana (10L kanta): Doze su izračunate za jednu kantu.
    """)

tab1, tab2, tab3 = st.tabs(["🍎 Voćnjak (3. god)", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# --- TAB 1: VOĆNJAK ---
with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust"], key="v_m")
    
    baza_v = {
        "Mart": "🛡️ **Zaštita:** Cuprozin (50g na 16L). **Karenca:** n/p. 🧪 **Ishrana:** KAN (200g po stablu).",
        "April": "🌸 **Cvet (Monilija):** Chorus (5g na 16L) ili Signum (10g na 16L). **Karenca:** 7-14 dana.",
        "Maj": "🛡️ **Zaštita:** Captan (35g na 16L). 🐜 **Vaši:** Teppeki (2g na 16L). **Karenca:** 21 dan.",
        "Jun": "🐛 **Smotavac:** Coragen (3ml na 16L). 🍄 **Pepelnica:** Luna Experience (10ml na 16L). **Karenca:** 14 dana.",
        "Jul": "💦 **Navodnjavanje!** 🛡️ **Grinje:** Envidor (10ml na 16L). **Karenca:** 14-21 dan.",
        "Avgust": "🛡️ **Pred berbu:** Teldor (15ml na 16L). **Karenca:** 1-3 dana (šljiva/breskva)."
    }
    st.info(baza_v[v_mesec])
    v_rad = st.multiselect("Završen rad:", ["Prskanje", "Đubrenje", "Navodnjavanje"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad", key="v_btn"):
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
                "Maj": "🧪 **Ishrana (10L kanta):** Fitofert Calcium (30ml). 🐜 **Vaši:** Laser (8ml na 16L). **Karenca:** 3 dana.",
                "Jun": "⚠️ **Plamenjača:** Ridomil Gold (40g na 16L). **Karenca:** 21 dan. 🌿 **Radovi:** Redovno pinciranje.",
                "Jul": "🛡️ **Trulež:** Switch (10g na 16L). **Karenca:** 3 dana. 🧪 **Ishrana:** Kristalon Crveni (20g na 10L).",
                "Avgust": "🧺 **Berba:** Voditi računa o karenti. ✂️ Skidanje donjih listova radi provetravanja."
            },
            "Paprika": {
                "Maj": "🌱 **Nakon sadnje:** Podsticanje ukorenjavanja (Fitofert Humisuper 30ml na 10L). 🐜 **Trips:** Vertical (10ml na 16L). **Karenca:** 7 dana.",
                "Jun": "🛡️ **Bakterioza:** Bakarni kreč (30g na 16L). **Karenca:** 14 dana. 🧪 **Ishrana:** Kristalon Zeleni (20g na 10L).",
                "Jul": "🧪 **Ishrana (10L):** Kristalon Crveni (25g). 🐜 **Vaši:** Afinex (5g na 16L). **Karenca:** 7 dana.",
                "Avgust": "🌶️ **Berba:** Zaštita od bele leptiraste vaši (Chess 6g na 16L). **Karenca:** 7 dana."
            },
            "Krastavac": {
                "Maj": "🌿 **Vođenje:** Formiranje vreže na kanap. 🛡️ **Pepelnica:** Nimrod (10ml na 16L). **Karenca:** 3 dana.",
                "Jun": "⚠️ **Plamenjača:** Equation Pro (10g na 16L). **Karenca:** 3 dana. 🐜 **Grinje:** Abastate (15ml na 16L).",
                "Jul": "🧺 **Intenzivna berba:** Svaki drugi dan. 🧪 **Ishrana (10L):** Wuxal Super (30ml).",
                "Avgust": "🛡️ **Podmlađivanje:** Uklanjanje starih listova. Zaštita od grinja (Envidor 10ml na 16L)."
            }
        }

    else:
        kultura = st.selectbox("Povrće:", ["Krompir", "Lubenica", "Beli luk", "Crni luk", "Bundeva", "Grašak", "Boranija"])
        baza_p = {
            "Krompir": {
                "Jun": "⚠️ **PLAMENJAČA:** Ridomil Gold (40g na 16L). **Karenca:** 21 dan. 🐞 **Zlatica:** Coragen (3ml na 16L). **Karenca:** 14 dana.",
                "Jul": "🛡️ **Plamenjača pred vađenje:** Revus (10ml na 16L). **Karenca:** 7 dana."
            },
            "Crni luk": {
                "Maj": "⚠️ **Plamenjača:** Ridomil Gold R (50g na 16L). **Karenca:** 14 dana. 🐜 **Muva:** Mospilan (4g na 16L). **Karenca:** 14 dana.",
                "Jun": "🛡️ **Zaštita:** Quadris (15ml na 16L). **Karenca:** 7 dana."
            }
        }

    # Prikaz specifičnog saveta
    rezultat = baza_p.get(kultura, {}).get(p_mesec, "Nema specifičnih podataka. Proverite opšte stanje.")
    st.warning(f"📌 **{kultura} ({p_mesec}):** {rezultat}")
    
    p_rad = st.multiselect("Urađeno:", ["Zalivanje sa prihranom", "Zaštita (Prskanje)", "Berba"], key=f"p_r_{kultura}_{p_mesec}")
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
