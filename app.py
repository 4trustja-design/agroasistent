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

# Povezivanje sa Google tabelom
def trajno_zapisi(akcija, status):
    try:
        # Čitamo tab koji se sada zove "Baza"
        df = conn.read(worksheet="Baza", ttl=0)
        
        novi_red = pd.DataFrame([{
            "Vremenska_oznaka": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Korisnik": "Agronom",
            "Akcija": akcija,
            "Status": status
        }])
        
        ažurirano = pd.concat([df, novi_red], ignore_index=True)
        
        # Šaljemo nazad u tab "Baza"
        conn.update(worksheet="Baza", data=ažurirano)
        st.toast(f"✅ Sačuvano u bazu!")
    except Exception as e:
        st.error(f"Greška: Promeni ime taba u Google tabeli iz 'Лист1' u 'Baza'. Detalji: {e}")

# --- Na dnu koda gde je prikaz istorije, promeni i tu ime taba ---
st.markdown("---")
st.subheader("📓 Istorija (Uživo iz Google Tabele)")
try:
    prikaz_df = conn.read(worksheet="Baza", ttl=0) # PROMENJENO U Baza
    prikaz_df = prikaz_df.dropna(how='all')
    st.dataframe(prikaz_df.tail(15), use_container_width=True)
except:
    st.info("Podaci će se pojaviti kada tab u Google tabeli nazoveš 'Baza'.")


# 2. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("OpenWeather API Ključ:", type="password")
    datum_sadnje = st.date_input("Datum zadnje sadnje:", datetime.now())

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Radar i Savet", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Radovi u voćnjaku (3. god)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"])
    v_radovi = st.multiselect("Šta si radio?", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba"], key="v_multi")
    if st.button("Trajno zapiši rad u voćnjaku"):
        if v_radovi:
            trajno_zapisi(f"Voće ({v_mesec})", ", ".join(v_radovi))

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Radovi u povrtnjaku")
    povrce = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica"])
    p_radovi = st.multiselect("Šta je urađeno?", ["Sadnja", "Zaštita", "Prihrana", "Zalivanje"], key="p_multi")
    if st.button("Trajno zapiši rad u povrtnjaku"):
        if p_radovi:
            trajno_zapisi(f"Povrće ({povrce})", ", ".join(p_radovi))

# --- TAB 3: RADAR I MAPA ---
with tab3:
    st.header("🛰️ Vremenski radar uživo (Kruševac)")
    radar_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(radar_html, height=620)
    
    st.markdown("---")
    st.subheader("🗺️ Obeleži parcelu")
    m = folium.Map(location=[43.5616, 21.3694], zoom_start=15)
    folium.LatLngPopup().add_to(m)
    st_folium(m, width=700, height=400, key="mapa_final")
    
    st.markdown("### 📢 Brzi savet")
    vlaga = st.slider("Trenutna vlažnost vazduha (%):", 0, 100, 90)
    if vlaga > 85:
        st.warning("⚠️ SPARINA: Ne preteruj sa vodom i provetri plastenik!")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovi i Investicije")
    stavka = st.text_input("Naziv investicije (npr. Creva):")
    iznos = st.number_input("Iznos (RSD):", min_value=0.0)
    if st.button("Zapiši trošak"):
        if stavka:
            trajno_zapisi("TROŠAK", f"{stavka}: {iznos} RSD")

# --- PRIKAZ ISTORIJE ---
st.markdown("---")
st.subheader("📓 Istorija (Uživo iz Google Tabele)")
try:
    prikaz_df = conn.read(worksheet="Лист1", ttl=0)
    # Čistimo prazne redove radi lepšeg prikaza
    prikaz_df = prikaz_df.dropna(how='all')
    st.dataframe(prikaz_df.tail(15), use_container_width=True)
except:
    st.info("Ovde će se pojaviti podaci čim uneseš prvi rad.")
