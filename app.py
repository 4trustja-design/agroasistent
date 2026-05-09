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
        # Čitamo list "Dnevnik" koristeći link iz Secrets
        df = conn.read(ttl=0)
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
        conn.update(data=finalni_df)
        st.success(f"✅ Uspešno sačuvano u Google tabelu!")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Greška: Proveri da li se list zove 'Dnevnik' i da li je link ispravan. Detalji: {e}")

st.title("🌾 AgroAsistent: Digitalni Dnevnik i Savetnik")

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "🛰️ Radar i Savet", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Radovi u voćnjaku (3. godina)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"])
    v_saveti = {
        "Maj": "🛡️ **Zaštita:** Captan (35g/16L). 🧪 **Ishrana:** Bor folijarno.",
        "Jun": "🐛 **Smotavac:** Coragen (3ml/16L). 🧪 **Ishrana:** Kalcijum (40ml/16L)."
    }
    st.info(v_saveti.get(v_mesec, "Pratite redovno stanje vlage."))
    v_rad = st.multiselect("Šta si radio?", ["Prskanje", "Đubrenje", "Navodnjavanje", "Kosidba"], key="v_multi")
    if st.button("Zapiši rad u voćnjaku"):
        if v_rad: zapisi_u_bazu(f"Voće ({v_mesec})", ", ".join(v_rad))

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Radovi u povrtnjaku")
    p_kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak"])
    p_saveti = {
        "Paradajz": "🌿 Zakidaj zaperke. 🛡️ Organski: Mleko/Voda. 🚑 Hitna: Quadris.",
        "Paprika": "🧪 Ishrana: Kalcijum (30ml/10L). 🐜 Prati tripsa.",
        "Krompir": "🚜 Nagrtanje zemlje. 🐞 Zlatica: Ručno skupljanje ili Lepinox."
    }
    st.warning(p_saveti.get(p_kultura, "Pratite vlagu i provetravajte plastenik."))
    p_rad = st.multiselect("Šta je urađeno?", ["Sadnja", "Zalivanje", "Zaštita", "Berba"], key="p_multi")
    if st.button("Zapiši rad u povrtnjaku"):
        if p_rad: zapisi_u_bazu(f"Povrće ({p_kultura})", ", ".join(p_rad))

# --- TAB 3: RADAR I PAMETNI SAVET ---
with tab3:
    st.subheader("🛰️ Vremenski radar za Kruševac")
    components.html('<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>', height=620)
    st.markdown("---")
    vlaga = st.slider("Trenutna vlažnost (%):", 0, 100, 90)
    if vlaga > 85:
        st.error("🚨 VELIKA SPARINA: Provetri plastenik i ne preteruj sa vodom!")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovi i Investicije")
    stavka = st.text_input("Naziv investicije (npr. Creva):")
    iznos = st.number_input("Iznos (RSD):", min_value=0.0)
    if st.button("Zapiši trošak"):
        if stavka: zapisi_u_bazu("TROŠAK", f"{stavka}: {iznos} RSD")

# --- PRIKAZ ISTORIJE IZ GOOGLE TABELE ---
st.markdown("---")
st.subheader("📓 Tvoj dnevnik (Uživo iz Google Sheeta)")
try:
    prikaz_df = conn.read(ttl=0)
    st.dataframe(prikaz_df.dropna(how='all').tail(15), use_container_width=True)
except:
    st.info("Ovde će se pojaviti podaci čim uradiš prvi uspešan upis.")
