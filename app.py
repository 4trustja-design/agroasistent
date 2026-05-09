import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="AgroAsistent Pro", layout="wide")

st.title("🌾 AgroAsistent: Digitalni Dnevnik")

# Povezivanje na tabelu (koristi link iz Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

def snimi_podatak(biljka, rad):
    try:
        # Čitamo bez imena taba (već je definisan GID u linku)
        df = conn.read(ttl=0)
        df = df.dropna(how='all')
        
        # Novi red podataka
        novi_red = pd.DataFrame([{
            "Vremenska_oznaka": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Korisnik": "Ja",
            "Akcija": biljka,
            "Status": rad
        }])
        
        # Spajanje
        finalni_df = pd.concat([df, novi_red], ignore_index=True)
        
        # Upisujemo direktno
        conn.update(data=finalni_df)
        st.success("✅ USPEŠNO SAČUVANO!")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Sistemska greška: {e}")

# INTERFEJS
c1, c2 = st.columns(2)
kultura = c1.selectbox("Kultura:", ["Paradajz", "Paprika", "Voće", "Krastavac", "Krompir", "TROŠAK"])
opis = c2.text_input("Šta si radio/kupio?")

if st.button("SAČUVAJ"):
    if opis:
        snimi_podatak(kultura, opis)
    else:
        st.warning("Upiši nešto pre čuvanja.")

# PRIKAZ TABELE
st.write("---")
st.subheader("📓 Tvoj dnevnik")
try:
    prikaz = conn.read(ttl=0)
    st.dataframe(prikaz.dropna(how='all').tail(10), use_container_width=True)
except:
    st.info("Podaci će se pojaviti ovde nakon prvog uspešnog upisa.")
