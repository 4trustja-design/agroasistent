import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import requests

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

# Resetovanje keša ako se javi greška
if st.button("🔄 Osveži vezu sa tabelom"):
    st.cache_data.clear()
    st.rerun()

# 2. USPOSTAVLJANJE VEZE
conn = st.connection("gsheets", type=GSheetsConnection)

def trajno_zapisi(akcija, status):
    try:
        # Čitamo list "Dnevnik" sa ttl=0 da ne koristi staru memoriju
        df = conn.read(worksheet="Dnevnik", ttl=0)
        
        novi_red = pd.DataFrame([{
            "Vremenska_oznaka": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Korisnik": "Agronom",
            "Akcija": akcija,
            "Status": status
        }])
        
        # Filtriramo prazne redove pre slanja
        df = df.dropna(how='all')
        ažurirano = pd.concat([df, novi_red], ignore_index=True)
        
        # Slanje u list "Dnevnik"
        conn.update(worksheet="Dnevnik", data=ažurirano)
        st.toast(f"✅ Sačuvano u Google Tabelu!")
    except Exception as e:
        st.error(f"Pokušaj ponovo. Ako ne radi, proveri da li se tab zove 'Dnevnik'. Detalji: {e}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

# --- TABOVI ---
tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Radar", "💰 Troškovnik"])

with tab1:
    v_mesec = st.selectbox("Izaberi mesec:", ["Maj", "Jun", "Jul", "Avgust"])
    v_rad = st.multiselect("Radovi:", ["Prskanje", "Đubrenje", "Navodnjavanje"])
    if st.button("Sačuvaj rad"):
        if v_rad: trajno_zapisi(f"Voće ({v_mesec})", ", ".join(v_rad))

with tab2:
    p_kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir"])
    p_rad = st.multiselect("Urađeno:", ["Sadnja", "Zaštita", "Zalivanje"])
    if st.button("Zabeleži rad"):
        if p_rad: trajno_zapisi(f"Povrće ({p_kultura})", ", ".join(p_rad))

with tab3:
    radar_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(radar_html, height=620)

with tab4:
    stavka = st.text_input("Investicija:")
    cena = st.number_input("Iznos (RSD):", min_value=0.0)
    if st.button("Zapiši trošak"):
        if stavka: trajno_zapisi("💰 TROŠAK", f"{stavka}: {cena} RSD")

# --- PRIKAZ ISTORIJE ---
st.markdown("---")
st.subheader("📓 Poslednjih 10 zapisa iz tabele")
try:
    prikaz_df = conn.read(worksheet="Dnevnik", ttl=0)
    st.dataframe(prikaz_df.dropna(how='all').tail(10), use_container_width=True)
except:
    st.info("Klikni na 'Osveži vezu' na vrhu ako se podaci ne vide.")
