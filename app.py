import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import requests

# 1. KONFIGURACIJA I POVEZIVANJE
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

# Povezivanje sa tvojom Google tabelom
conn = st.connection("gsheets", type=GSheetsConnection)

# Funkcija za upis u tvoju tabelu (Kolone: Временска ознака, Korisnik, Akcija, Status)
def trajno_zapisi(akcija, status):
    try:
        # Čitanje trenutnih podataka
        df = conn.read(worksheet="Лист1", ttl=0)
        # Pravljenje novog reda
        novi_red = pd.DataFrame([{
            "Временска ознака": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Korisnik": "Agronom",
            "Akcija": akcija,
            "Status": status
        }])
        # Spajanje i slanje nazad na Google Drive
        osvezeno = pd.concat([df, novi_red], ignore_index=True)
        conn.update(worksheet="Лист1", data=osvezeno)
        st.toast("✅ Podatak trajno sačuvan u Google Tabeli!")
    except Exception as e:
        st.error(f"Greška pri čuvanju: {e}")

st.title("🌾 AgroAsistent: Trajni Digitalni Dnevnik")

# 2. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("OpenWeather API Ključ:", type="password")
    datum_sadnje = st.date_input("Datum zadnje sadnje:", datetime.now())

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Radar i Savet", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Radovi u voćnjaku")
    v_mesec = st.selectbox("Izaberi mesec:", ["Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"])
    v_radovi = st.multiselect("Šta si danas radio?", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba"])
    
    if st.button("Trajno zapiši u dnevnik voća"):
        if v_radovi:
            trajno_zapisi(f"Voće ({v_mesec})", ", ".join(v_radovi))

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Radovi u povrtnjaku")
    povrce = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica"])
    p_radovi = st.multiselect("Šta je urađeno?", ["Sadnja", "Zaštita", "Prihrana", "Zalivanje"])
    
    if st.button("Trajno zapiši u dnevnik povrća"):
        if p_radovi:
            trajno_zapisi(f"Povrće ({povrce})", ", ".join(p_radovi))

# --- TAB 3: RADAR I PAMETNI SAVET (Kruševac) ---
with tab3:
    st.header("🛰️ Vremenski radar uživo")
    radar_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(radar_html, height=620)
    
    st.markdown("---")
    st.subheader("🗺️ Obeleži parcelu za savet")
    m = folium.Map(location=[43.5616, 21.3694], zoom_start=15)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=400, key="mapa_final")
    
    # Ručni unos vlage (dok se ne poveže API)
    st.markdown("### 📢 Brzi savet za trenutno stanje")
    vlaga = st.slider("Trenutna vlažnost vazduha (%):", 0, 100, 90)
    if vlaga > 85:
        st.warning("⚠️ SPARINA: Ne preteruj sa vodom i provetri plastenik!")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovi (Creva, Seme, Preparati)")
    stavka = st.text_input("Naziv investicije:")
    iznos = st.number_input("Iznos (RSD):", min_value=0.0)
    if st.button("Zapiši trošak"):
        if stavka:
            trajno_zapisi("TROŠAK", f"{stavka}: {iznos} RSD")

# --- PRIKAZ ISTORIJE IZ GOOGLE TABELE NA DNU ---
st.markdown("---")
st.subheader("📓 Istorija tvojih radova (Uživo iz Google Tabele)")
try:
    prikaz_df = conn.read(worksheet="Лист1", ttl=0)
    st.dataframe(prikaz_df.tail(10), use_container_width=True) # Pokazuje zadnjih 10 radova
except:
    st.info("Ovde će se pojaviti podaci čim uneseš prvi rad.")
