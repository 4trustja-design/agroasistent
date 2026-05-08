import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import requests
import io

# 1. OSNOVNA PODEŠAVANJA (Mora biti prvi red)
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

# 2. USPOSTAVLJANJE VEZE (Sada je na vrhu da bi 'conn' uvek postojao)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. FUNKCIJA ZA UPIS
def trajno_zapisi(akcija, status):
    try:
        # Čitamo trenutno stanje iz taba "Baza"
        df = conn.read(worksheet="Baza", ttl=0)
        
        # Novi red podataka
        novi_red = pd.DataFrame([{
            "Vremenska_oznaka": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Korisnik": "Agronom",
            "Akcija": akcija,
            "Status": status
        }])
        
        # Spajanje i slanje
        ažurirano = pd.concat([df, novi_red], ignore_index=True)
        conn.update(worksheet="Baza", data=ažurirano)
        st.toast(f"✅ Uspešno zabeleženo!")
    except Exception as e:
        st.error(f"Greška! Proveri da li se tab u Google tabeli zove 'Baza'. Detalji: {e}")

st.title("🌾 AgroAsistent: Digitalna Knjiga Polja")

# 4. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("OpenWeather API Ključ:", type="password")
    datum_sadnje = st.date_input("Datum zadnje sadnje:", datetime.now())

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Radar i Savet", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Radovi u voćnjaku")
    v_mesec = st.selectbox("Mesec:", ["Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"])
    v_rad = st.multiselect("Šta je urađeno?", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba"], key="v_m")
    if st.button("Sačuvaj u dnevnik voća"):
        if v_rad:
            trajno_zapisi(f"Voće ({v_mesec})", ", ".join(v_rad))

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Radovi u povrtnjaku")
    p_kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica"])
    p_rad = st.multiselect("Šta je urađeno?", ["Sadnja", "Zaštita", "Prihrana", "Zalivanje"], key="p_m")
    if st.button("Sačuvaj u dnevnik povrća"):
        if p_rad:
            trajno_zapisi(f"Povrće ({p_kultura})", ", ".join(p_rad))

# --- TAB 3: RADAR I PAMETNI SAVET ---
with tab3:
    st.header("🛰️ Radar i Savet (Kruševac)")
    radar_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(radar_html, height=620)
    
    st.markdown("---")
    vlaga = st.slider("Trenutna vlažnost (%):", 0, 100, 90)
    if vlaga > 85:
        st.warning("⚠️ SPARINA: Ne preteruj sa vodom i provetri plastenik sutra ujutru!")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovi")
    stavka = st.text_input("Naziv investicije:")
    cena = st.number_input("Iznos (RSD):", min_value=0.0)
    if st.button("Zapiši trošak"):
        if stavka:
            trajno_zapisi("TROŠAK", f"{stavka}: {cena} RSD")

# --- PRIKAZ ISTORIJE IZ TABELE ---
st.markdown("---")
st.subheader("📓 Istorija (Uživo iz Google Tabele)")
try:
    prikaz_df = conn.read(worksheet="Baza", ttl=0)
    st.dataframe(prikaz_df.dropna(how='all').tail(10), use_container_width=True)
except:
    st.info("Podaci će se pojaviti kada povežete tabelu i nazovete tab 'Baza'.")
