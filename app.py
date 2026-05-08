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
        # Čitamo tabelu (automatski nalazi list preko GID-a iz Secrets)
        df = conn.read(ttl=0)
        df = df.dropna(how='all')
        
        # Pravimo novi red
        novi_red = pd.DataFrame([{
            "Vremenska_oznaka": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Korisnik": "Ja",
            "Akcija": kultura,
            "Status": radnja
        }])
        
        # Spajamo i šaljemo
        final_df = pd.concat([df, novi_red], ignore_index=True)
        conn.update(data=final_df)
        st.success(f"✅ Sačuvano u Google tabelu!")
    except Exception as e:
        st.error(f"Greška: {e}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

tab1, tab2 = st.tabs(["🚜 Unos radova", "🛰️ Radar"])

with tab1:
    c1, c2 = st.columns(2)
    izabrana_kultura = c1.selectbox("Biljka:", ["Paradajz", "Paprika", "Voće", "Krastavac", "Krompir", "TROŠAK"])
    opis_rada = c2.text_input("Šta si radio/kupio?")
    
    if st.button("SAČUVAJ TRAJNO"):
        if opis_rada:
            zapisi_u_tabelu(izabrana_kultura, opis_rada)
        else:
            st.warning("Upiši opis rada pre čuvanja.")

with tab2:
    st.subheader("Radar Kruševac")
    radar_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(radar_html, height=620)

# Prikaz istorije
st.markdown("---")
st.subheader("📓 Tvoj dnevnik uživo")
try:
    prikaz = conn.read(ttl=0)
    st.dataframe(prikaz.dropna(how='all').tail(10), use_container_width=True)
except:
    st.info("Ovde će se pojaviti podaci čim klikneš na 'SAČUVAJ TRAJNO'.")
