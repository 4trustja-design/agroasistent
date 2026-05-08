import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime

# 1. Osnovna podešavanja
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide", page_icon="🌾")

# Inicijalizacija dnevnika u memoriji
if 'dnevnik' not in st.session_state:
    st.session_state.dnevnik = []

st.title("🌾 AgroAsistent: Digitalni Dnevnik i Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# --- TAB 1: VOĆARSTVO (Baza znanja u kodu) ---
with tab1:
    st.header("🍎 Plan za voćnjak (0-5 god)")
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik"])
    with v_col2:
        godina = st.slider("Starost sadnice (god):", 0, 5, 1)
    
    st.markdown(f"### 📋 Preporuke za {voce} ({godina}. godina)")
    
    # Fiksni saveti umesto AI
    st.info("● **Mart:** Zimsko prskanje bakarnim preparatima. ● **April:** Prihrana azotnim đubrivima (KAN/Urea).")
    
    c1, c2 = st.columns(2)
    with c1:
        v_zast = st.checkbox("Urađena zaštita", key=f"v_z_{voce}_{godina}")
    with c2:
        v_ishr = st.checkbox("Urađena ishrana", key=f"v_i_{voce}_{godina}")

    if st.button("Zapiši u dnevnik", key="v_save"):
        vreme = datetime.now().strftime("%d.%m.%Y")
        radovi = []
        if v_zast: radovi.append("Zaštita")
        if v_ishr: radovi.append("Ishrana")
        if radovi:
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": voce, "Radovi": ", ".join(radovi)})
            st.success("Zapisano u dnevnik!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Plan za povrtnjak")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        povrce = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika", "Krastavac", "Kupus"])
    with p_col2:
        tip = st.radio("Uzgoj:", ["Plastenik", "Otvoreno polje"], horizontal=True)
    
    st.markdown(f"### 📋 Preporuke za {povrce}")
    st.success("● **Sadnja:** Voditi računa o temperaturi zemljišta. ● **Zaštita:** Preventiva protiv plamenjače nakon kiše.")
    
    p_zast = st.checkbox("Urađena zaštita", key=f"p_z_{povrce}_{tip}")
    p_ishr = st.checkbox("Urađena prihrana", key=f"p_i_{povrce}_{tip}")

    if st.button("Zapiši u dnevnik", key="p_save"):
        vreme = datetime.now().strftime("%d.%m.%Y")
        radovi = []
        if p_zast: radovi.append("Zaštita")
        if p_ishr: radovi.append("Ishrana")
        if radovi:
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": f"{povrce} ({tip})", "Radovi": ", ".join(radovi)})
            st.success("Zabeleženo!")

# --- TAB 3: MOJA PARCELA (Mapa bez ključa) ---
with tab3:
    st.header("📍 Moja Parcela")
    st.write("Klikni na mapu da obeležiš svoju parcelu i vidiš koordinate:")
    
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=800, height=500, key="agromapa_final")

    if izlaz_mape and izlaz_mape.get('last_clicked'):
        lat, lon = izlaz_mape['last_clicked']['lat'], izlaz_mape['last_clicked']['lng']
        st.success(f"Koordinate: {lat:.4f}, {lon:.4f}")

# --- PRIKAZ DNEVNIKA ---
st.markdown("---")
st.subheader("📓 Dnevnik polja (Istorija)")
if st.session_state.dnevnik:
    st.table(st.session_state.dnevnik)
    if st.button("Obriši istoriju"):
        st.session_state.dnevnik = []
        st.rerun()
else:
    st.write("Dnevnik je prazan. Izaberite radove iznad i kliknite na 'Zapiši'.")
