import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

# 2. VEZA SA TABELOM
conn = st.connection("gsheets", type=GSheetsConnection)

def trajno_zapisi(akcija, status):
    try:
        # Čitamo list "Dnevnik" - mora postojati!
        df = conn.read(worksheet="Dnevnik", ttl=0)
        
        # Pravimo novi red - kolone MORAJU biti identične kao u tabeli
        novi_podaci = {
            "Vremenska_oznaka": [datetime.now().strftime("%d.%m.%Y %H:%M")],
            "Korisnik": ["Agronom"],
            "Akcija": [akcija],
            "Status": [status]
        }
        novi_df = pd.DataFrame(novi_podaci)
        
        # Čistimo staru tabelu od praznih redova da ne bi došlo do Error 400
        df_cist = df.dropna(how='all')
        
        # Spajamo staro i novo
        finalni_df = pd.concat([df_cist, novi_df], ignore_index=True)
        
        # Šaljemo nazad
        conn.update(worksheet="Dnevnik", data=finalni_df)
        st.toast(f"✅ Uspešno sačuvano: {akcija}")
        st.rerun() # Osvežava tabelu na ekranu
    except Exception as e:
        st.error(f"Greška pri upisu. Proveri da li su naslovi u A1, B1, C1, D1 ispravni. Detalji: {e}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

# --- MENI ---
tab1, tab2, tab3 = st.tabs(["🚜 Radovi", "🛰️ Radar", "💰 Troškovi"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        kultura = st.selectbox("Izaberi kulturu:", ["Voće", "Paradajz", "Paprika", "Krastavac", "Krompir", "Luk"])
    with col2:
        radnja = st.multiselect("Šta si uradio?", ["Prskanje", "Đubrenje", "Zalivanje", "Sadnja", "Okopavanje"])
    
    if st.button("Sačuvaj rad trajno"):
        if radnja:
            trajno_zapisi(kultura, ", ".join(radnja))

with tab2:
    st.subheader("Radar za Kruševac")
    radar_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(radar_html, height=620)

with tab3:
    col_t1, col_t2 = st.columns(2)
    stavka = col_t1.text_input("Šta si kupio?")
    cena = col_t2.number_input("Iznos (RSD):", min_value=0.0)
    if st.button("Zapiši trošak trajno"):
        if stavka:
            trajno_zapisi("TROŠAK", f"{stavka}: {cena} RSD")

# --- PRIKAZ ISTORIJE ---
st.markdown("---")
st.subheader("📓 Tvoj dnevnik uživo")
try:
    prikaz = conn.read(worksheet="Dnevnik", ttl=0)
    st.dataframe(prikaz.dropna(how='all').tail(10), use_container_width=True)
except:
    st.info("Podaci će se pojaviti ovde nakon prvog uspešnog upisa.")
