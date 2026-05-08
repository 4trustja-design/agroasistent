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

# 2. USPOSTAVLJANJE VEZE SA GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def trajno_zapisi(akcija, status):
    try:
        # Čitamo list "Dnevnik" - mora postojati u Google tabeli!
        df = conn.read(worksheet="Dnevnik", ttl=0)
        
        novi_red = pd.DataFrame([{
            "Vremenska_oznaka": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Korisnik": "Agronom",
            "Akcija": akcija,
            "Status": status
        }])
        
        ažurirano = pd.concat([df, novi_red], ignore_index=True)
        
        # Šaljemo nazad u list "Dnevnik"
        conn.update(worksheet="Dnevnik", data=ažurirano)
        st.toast(f"✅ Uspešno zabeleženo: {akcija}")
    except Exception as e:
        st.error(f"Greška pri čuvanju! Proveri da li si napravio list 'Dnevnik' i postavio 'Editor' dozvolu. Detalji: {e}")

st.title("🌾 AgroAsistent: Digitalna Knjiga Polja")

# 3. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    datum_sadnje = st.date_input("Datum zadnje sadnje:", datetime.now())

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Radar i Savet", "💰 Troškovnik"])

with tab1:
    st.header("🍎 Radovi u voćnjaku")
    v_mesec = st.selectbox("Izaberi mesec:", ["Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"])
    v_rad = st.multiselect("Šta si danas radio?", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba"], key="v_m_multi")
    if st.button("Sačuvaj u dnevnik voća"):
        if v_rad: trajno_zapisi(f"Voće ({v_mesec})", ", ".join(v_rad))

with tab2:
    st.header("🥦 Radovi u povrtnjaku")
    p_kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica"])
    p_rad = st.multiselect("Šta je urađeno?", ["Sadnja", "Zaštita", "Prihrana", "Zalivanje"], key="p_m_multi")
    if st.button("Sačuvaj u dnevnik povrća"):
        if p_rad: trajno_zapisi(f"Povrće ({p_kultura})", ", ".join(p_rad))

with tab3:
    st.header("🛰️ Radar i Savet (Kruševac)")
    v_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(v_html, height=620)
    st.markdown("---")
    vlaga = st.slider("Trenutna vlažnost (%):", 0, 100, 90)
    if vlaga > 85: st.warning("⚠️ SPARINA: Provetri plastenik sutra ujutru!")

with tab4:
    st.header("💰 Troškovi")
    stavka = st.text_input("Naziv investicije:")
    iznos = st.number_input("Iznos (RSD):", min_value=0.0)
    if st.button("Zapiši trošak"):
        if stavka: trajno_zapisi("TROŠAK", f"{stavka}: {iznos} RSD")

# --- PRIKAZ ISTORIJE ---
st.markdown("---")
st.subheader("📓 Istorija tvojih radova (Uživo iz Google Tabele)")
try:
    prikaz_df = conn.read(worksheet="Dnevnik", ttl=0)
    st.dataframe(prikaz_df.dropna(how='all').tail(10), use_container_width=True)
except:
    st.info("Podaci će se pojaviti kada napraviš list 'Dnevnik'.")
