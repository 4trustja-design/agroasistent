import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Kruševac", layout="wide", page_icon="🌾")

# Učitavanje poverljivih podataka
try:
    TOKEN = st.secrets["GITHUB_TOKEN"].strip()
    USER = "4trustja-design"
    REPO = "requirements.txt"
except Exception as e:
    st.error("⚠️ Greška: Niste ispravno popunili Secrets u Streamlit podešavanjima!")
    st.stop()

FILE_PATH = "dnevnik.csv"

# --- FUNKCIJA ZA PISANJE NA GITHUB (TVOJA ISPRAVLJENA) ---
def snimi_na_github(kultura, radnja):
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        sha = None
        stari_sadrzaj = ""
        if res.status_code == 200:
            podaci = res.json()
            sha = podaci.get('sha')
            stari_sadrzaj = base64.b64decode(podaci['content']).decode('utf-8')
        
        vreme = datetime.now().strftime('%d.%m.%Y %H:%M')
        novi_red = f"{vreme},{kultura},{radnja.replace(',', ' ')}\n"
        
        if not stari_sadrzaj:
            finalni_sadrzaj = "Datum,Kultura,Rad\n" + novi_red
        else:
            finalni_sadrzaj = stari_sadrzaj + ('' if stari_sadrzaj.endswith('\n') else '\n') + novi_red
            
        payload = {
            "message": f"Unos: {kultura}",
            "content": base64.b64encode(finalni_sadrzaj.encode('utf-8')).decode('utf-8'),
            "sha": sha
        }
        r = requests.put(url, headers=headers, json=payload, timeout=10)
        if r.status_code in [200, 201]:
            st.success("✅ Podaci su trajno sačuvani na GitHub!")
            st.balloons()
            st.rerun()
        else:
            st.error(f"Greška {r.status_code}: {r.text}")
    except Exception as e:
        st.error(f"Kritična greška: {e}")

# --- GLAVNI INTERFEJS ---
st.title("🌾 AgroAsistent: Digitalni Savetnik i Dnevnik")

# Bočni meni za podešavanja
with st.sidebar:
    st.header("⚙️ Podešavanja")
    datum_sadnje = st.date_input("Kada ste posadili poslednji rasad?", datetime.now())
    st.markdown("---")
    st.info("Podaci se čuvaju u `dnevnik.csv` na vašem GitHub-u.")

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Radar i Savet", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka (3. godina)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"], key="v_m")
    baza_v = {
        "Maj": "🛡️ **Zaštita:** Captan (35g na 16L). 🧪 **Ishrana:** Bor preko lista za bolju oplodnju.",
        "Jun": "🐛 **Smotavac:** Coragen (3ml na 16L). 🧪 **Ishrana:** Kalcijum (Wuxal Calcium) - 40ml/16L.",
        "Jul": "💦 **Navodnjavanje:** Kritično za formiranje pupoljaka.",
        "Avgust": "🍎 **Berba:** Rani sortiment. 🛡️ **Teldor** (15ml na 16L) - kratka karenca.",
        "Septembar": "🧺 **Berba:** Glavna berba. 🧹 **Higijena:** Skupljanje trulih plodova.",
        "Oktobar": "🧪 **Ishrana:** Jesenje đubrenje (NPK 6:12:24)."
    }
    st.info(baza_v.get(v_mesec, "Pratite redovno stanje."))
    v_rad = st.multiselect("Šta ste radili?", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad u voćnjaku"):
        if v_rad: snimi_na_github(f"Voće ({v_mesec})", ", ".join(v_rad))

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Saveti i Mešovita sadnja")
    # Kalendar ukorenjavanja
    razlika = (datetime.now().date() - datum_sadnje).days
    st.subheader(f"🌱 Status rasada: {razlika} dana")
    if razlika < 4: st.error("❗ UKORENJAVANJE: Ne prskaj ničim! Samo umereno zalivanje ujutru.")
    elif 4 <= razlika <= 10: st.warning("⚠️ STABILIZACIJA: Može mleko (1:10). Bez sode bikarbone.")
    else: st.success("✅ STABILNA BILJKA: Možeš početi sa redovnom zaštitom.")

    with st.expander("🤝 Vodič: Šta saditi pored čega"):
        st.write("Luk + Šargarepa (teraju muve). Paradajz + Bosiljak (ukus i vaši). Krompir + Pasulj (azot).")

    st.markdown("---")
    kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak"])
    baza_p = {
        "Paradajz": "🌿 Maj: Ukorenjavanje i pinciranje. 🛡️ Ne kvasi list!",
        "Paprika": "🧪 Maj: Prihrana kalcijumom. 🐜 Prati tripsa.",
        "Krastavac": "🥒 Maj: Vođenje na kanap. 🛡️ Soda bikarbona protiv pepelnice.",
        "Krompir": "🚜 Maj: Nagrtanje. 🐞 Zlatica: Ručno skupljanje jaja.",
        "Lubenica": "🍉 Maj: Ukorenjavanje. 💦 Ne preteruj sa vodom.",
        "Grašak": "🌸 Maj: CVETANJE! Obavezno navodnjavanje.",
        "Boranija": "🌱 Maj: Setva ili okopavanje tek ponikle."
    }
    st.info(baza_p.get(kultura, "Pratite vlažnost."))
    p_rad = st.multiselect("Šta je urađeno?", ["Sadnja", "Zalivanje", "Zaštita", "Berba"], key=f"p_{kultura}")
    if st.button("Zapiši rad u povrtnjaku"):
        if p_rad: snimi_na_github(f"{kultura}", ", ".join(p_rad))

# --- TAB 3: RADAR I SAVET ---
with tab3:
    st.header("🛰️ Radar i Pametni Savet")
    components.html('<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>', height=620)
    st.markdown("---")
    st.subheader("📢 Agronomski savet za Kruševac")
    vlaga_s = st.slider("Trenutna vlažnost (%):", 0, 100, 90)
    if vlaga_s > 85:
        st.warning(f"**PAŽNJA:** Velika sparina ({vlaga_s}%). Ne preteruj sa vodom sutra ujutru i obavezno provetri plastenik!")
    if vlaga_s > 80 and razlika > 4:
        st.info("🛡️ **RECEPT (16L):** 1.5L mleka + 14.5L vode. Prskaj čim se list prosuši.")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovnik")
    stavka = st.text_input("Naziv investicije:")
    iznos = st.number_input("Iznos (RSD):", min_value=0.0)
    if st.button("Zapiši trošak"):
        if stavka: snimi_na_github("TROŠAK", f"{stavka}: {iznos} RSD")

# --- ČITANJE DNEVNIKA (TVOJ ISPRAVLJEN KOD) ---
st.write("---")
st.subheader("📓 Tvoj digitalni dnevnik (Uživo)")
try:
    url_raw = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{FILE_PATH}"
    df = pd.read_csv(f"{url_raw}?v={datetime.now().timestamp()}")
    st.dataframe(df.tail(20), use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Preuzmi tabelu kao CSV",
        data=csv,
        file_name="dnevnik.csv",
        mime="text/csv",
    )
except:
    st.info("Tabela će se pojaviti ovde nakon prvog uspešnog upisa.")
