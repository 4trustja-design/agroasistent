import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components

# 1. Podešavanje
st.set_page_config(page_title="AgroAsistent Pro", layout="wide")

# 2. Veza sa tvojom tabelom
conn = st.connection("gsheets", type=GSheetsConnection)

def zapisi_u_tabelu(kultura, radnja):
    try:
        # Čitamo list "Dnevnik" - on MORA postojati u Google tabeli
        df = conn.read(worksheet="Dnevnik", ttl=0)
        df = df.dropna(how='all')
        
        novi_red = pd.DataFrame([{
            "Vremenska_oznaka": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Korisnik": "Ja",
            "Akcija": kultura,
            "Status": radnja
        }])
        
        finalni_df = pd.concat([df, novi_red], ignore_index=True)
        
        # Upisujemo nazad u list "Dnevnik"
        conn.update(worksheet="Dnevnik", data=finalni_df)
        st.success(f"✅ Sačuvano u Google tabelu!")
        st.rerun()
    except Exception as e:
        st.error(f"Sistemska greška: Proveri da li se list u Google tabeli zove tačno 'Dnevnik' (latinicom). Detalji: {e}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

tab1, tab2 = st.tabs(["🚜 Unos radova", "🛰️ Radar"])

with tab1:
    c1, c2 = st.columns(2)
    izabrana_kultura = c1.selectbox("Biljka:", ["Paradajz", "Paprika", "Voće", "Krastavac", "Krompir", "TROŠAK"])
    opis_rada = c2.text_input("Šta si radio/kupio?", placeholder="Npr. Zalivanje, Prskanje...")
    
    if st.button("SAČUVAJ TRAJNO"):
        if opis_rada:
            zapisi_u_tabelu(izabrana_kultura, opis_rada)
        else:
            st.warning("Upiši opis rada pre čuvanja.")

with tab2:
    radar_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(radar_html, height=620)

# Prikaz istorije
st.markdown("---")
st.subheader("📓 Tvoj dnevnik uživo (Poslednjih 10 unosa)")
try:
    prikaz = conn.read(worksheet="Dnevnik", ttl=0)
    st.dataframe(prikaz.dropna(how='all').tail(10), use_container_width=True)
except:
    st.info("Podaci će se pojaviti čim napraviš prvi uspešan upis.")
