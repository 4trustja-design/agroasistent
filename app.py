import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="AgroAsistent Pro", layout="wide")

# Veza
conn = st.connection("gsheets", type=GSheetsConnection)

def zapisi_rad(kultura, radnja):
    try:
        # Čitamo list "Dnevnik"
        df = conn.read(worksheet="Dnevnik", ttl=0)
        df = df.dropna(how='all')
        
        novi_red = pd.DataFrame([{
            "Vremenska_oznaka": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Korisnik": "Ja",
            "Akcija": kultura,
            "Status": radnja
        }])
        
        finalni_df = pd.concat([df, novi_red], ignore_index=True)
        conn.update(worksheet="Dnevnik", data=finalni_df)
        st.success("✅ Podatak je uspešno upisan u tabelu!")
    except Exception as e:
        st.error(f"Sistemska greška: {e}")
        st.info("Proveri da li je u Google tabeli ime lista tačno 'Dnevnik' (bez razmaka).")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

c1, c2 = st.columns(2)
kultura = c1.selectbox("Kultura:", ["Paradajz", "Paprika", "Voće", "Krompir", "TROŠAK"])
opis = c2.text_input("Šta si radio/kupio?")

if st.button("SAČUVAJ"):
    if opis:
        zapisi_rad(kultura, opis)
    else:
        st.warning("Upiši opis pre čuvanja.")

st.write("---")
st.subheader("📓 Tvoj dnevnik")
try:
    prikaz = conn.read(worksheet="Dnevnik", ttl=0)
    st.dataframe(prikaz.dropna(how='all').tail(10), use_container_width=True)
except:
    st.info("Ovde će se pojaviti podaci čim prvi upis uspe.")
