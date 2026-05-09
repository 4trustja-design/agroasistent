import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Pro", layout="wide")

# 2. VEZA SA TVOJOM TABELOM
conn = st.connection("gsheets", type=GSheetsConnection)

def zapisi_u_bazu(kultura, radnja):
    try:
        # Čitamo list "Dnevnik" - on MORA postojati u Google tabeli
        df = conn.read(worksheet="Dnevnik", ttl=0)
        df = df.dropna(how='all')
        
        # Novi red podataka
        novi_red = pd.DataFrame([{
            "Vremenska_oznaka": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Korisnik": "Ja",
            "Akcija": kultura,
            "Status": radnja
        }])
        
        # Spajanje i slanje nazad na Google Drive
        finalni_df = pd.concat([df, novi_red], ignore_index=True)
        conn.update(worksheet="Dnevnik", data=finalni_df)
        st.success(f"✅ Uspešno sačuvano u Google tabelu!")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Greška: Proveri da li se list zove 'Dnevnik'. Detalji: {e}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik i Savetnik")

tab1, tab2, tab3 = st.tabs(["🚜 Radovi i Troškovi", "🛰️ Radar", "📓 Istorija"])

with tab1:
    c1, c2 = st.columns(2)
    izbor = c1.selectbox("Kultura:", ["Paradajz", "Paprika", "Voće", "Krastavac", "Krompir", "TROŠAK"])
    tekst = c2.text_input("Opis rada / Iznos troška:")
    
    if st.button("SAČUVAJ"):
        if tekst:
            zapisi_u_bazu(izbor, tekst)
        else:
            st.warning("Prvo unesi opis.")

with tab2:
    st.subheader("Radar Kruševac")
    components.html('<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>', height=620)

with tab3:
    st.subheader("📓 Tvoj dnevnik uživo")
    try:
        prikaz_df = conn.read(worksheet="Dnevnik", ttl=0)
        st.dataframe(prikaz_df.dropna(how='all').tail(20), use_container_width=True)
    except:
        st.info("Podaci će se pojaviti nakon prvog upisa.")
