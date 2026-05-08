import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
import requests
import io
from PIL import Image
import base64

# 1. OSNOVNA PODEŠAVANJA
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

if 'dnevnik' not in st.session_state: st.session_state.dnevnik = []
if 'troskovi' not in st.session_state: st.session_state.troskovi = []

st.title("🌿 AgroAsistent: Digitalni Savetnik i AI Dijagnoza")

# 2. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    ai_key = st.text_input("Unesi Google Gemini API Ključ:", type="password", help="Za prepoznavanje bolesti sa slike.")
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    st.markdown("---")
    datum_sadnje = st.date_input("Kada si posadio glavni rasad?", datetime.now())
    if st.button("❌ Obriši sve podatke"):
        st.session_state.dnevnik = []
        st.session_state.troskovi = []
        st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🍎 Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Radar i Savet", "💰 Troškovnik", "📸 Foto Dijagnoza"])

# --- FUNKCIJA ZA AI PREPOZNAVANJE SLIKE ---
def analiziraj_list(image_file, api_key):
    img = Image.open(image_file)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    url = f"https://googleapis.com{api_key.strip()}"
    headers = {'Content-Type': 'application/json'}
    prompt = "Kao stručni agronom iz Srbije, analiziraj sliku lista. Reci mi: 1. Šta je problem? 2. Koji su organski lekovi (0 dana karence)? 3. Koja je hitna hemija ako mora?"
    payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": img_str}}]}]}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Problem u komunikaciji sa AI serverom. Proveri ključ."

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka (3. godina)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"], key="v_m")
    baza_v = {
        "Maj": "🛡️ Captan (35g na 16L). 🧪 Bor (20ml/10L) folijarno.",
        "Jun": "🐛 Coragen (3ml na 16L). 🧪 Kalcijum (40ml/16L).",
        "Jul": "💦 Navodnjavanje! 🛡️ Envidor (10ml/16L) protiv grinja.",
        "Avgust": "🧺 Berba ranih sorti. 🛡️ Teldor (15ml/16L) pred berbu."
    }
    st.info(baza_v.get(v_mesec, "Pratite redovno stanje i vlagu."))
    v_rad = st.multiselect("Zapis rada:", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad u voćnjaku"):
        if v_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m."), "Kultura": f"Voće ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Saveti i Mešovita sadnja")
    razlika = (datetime.now().date() - datum_sadnje).days
    st.subheader(f"🌱 Status rasada: {razlika} dana")
    if razlika < 4: st.error("❗ UKORENJAVANJE: Ne prskaj ničim! Samo umereno zalivanje ujutru.")
    elif 4 <= razlika <= 10: st.warning("⚠️ STABILIZACIJA: Može mleko (1:10). Bez sode bikarbone.")
    else: st.success("✅ STABILNA BILJKA: Možeš početi sa redovnom zaštitom.")

    with st.expander("🤝 Vodič: Šta saditi pored čega"):
        st.write("Luk + Šargarepa (najbolji prijatelji). Paradajz + Bosiljak. Krompir + Pasulj.")

    st.markdown("---")
    tip = st.radio("Sistem:", ["Plastenik (16x5m)", "Otvoreno polje"], horizontal=True)
    povrce = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak"])
    baza_p = {
        "Paradajz": "🌿 Zakidaj zaperke. 🚑 Hitna (3 dana karence): Quadris.",
        "Paprika": "🐜 Prati tripsa. 🧪 Ishrana: Kalcijum (30ml/10L).",
        "Krastavac": "🥒 Zalivaj svaki dan. 🛡️ Organski: Soda (50g/10L).",
        "Krompir": "🐞 Prati zlaticu. 🛡️ Jun: Zaštita od plamenjače."
    }
    st.info(baza_p.get(povrce, "Pratite vlažnost."))
    p_rad = st.multiselect("Urađeno:", ["Sadnja", "Zaštita", "Prihrana"], key=f"p_{povrce}_{tip}")
    if st.button("Zapiši rad u povrtnjaku"):
        if p_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m."), "Kultura": f"{povrce} ({tip})", "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: RADAR I SAVET ---
with tab3:
    st.header("🛰️ Radar i Pametni Saveti")
    v_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(v_html, height=620)
    st.markdown("---")
    m = folium.Map(location=[43.5616, 21.3694], zoom_start=15)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=450, key="mapa_final")
    
    st.markdown("### 📢 Agronomski savet")
    c1, c2 = st.columns(2)
    temp_s = c1.number_input("Temp (°C):", value=15)
    vlaga_s = c2.slider("Vlaga (%):", 0, 100, 90)
    if vlaga_s > 85 and temp_s < 20:
        st.warning(f"**PAŽNJA:** Velika sparina ({vlaga_s}%). Ne preteruj sa vodom i provetri plastenik!")
    if vlaga_s > 80 and razlika > 4:
        st.info("🛡️ **RECEPT ZA 16L:** 1.5L mleka + 14.5L vode. Prskaj čim se list prosuši.")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovnik")
    c1, c2, c3 = st.columns(3)
    stavka = c1.text_input("Stavka:")
    kol = c2.number_input("Količina:", min_value=1.0, value=1.0)
    cena = c3.number_input("Cena (RSD):", min_value=0.0)
    if st.button("Dodaj"):
        if stavka: st.session_state.troskovi.append({"Stavka": stavka, "Iznos": kol * cena})
    if st.session_state.troskovi:
        st.table(pd.DataFrame(st.session_state.troskovi))

# --- TAB 5: FOTO DIJAGNOZA ---
with tab5:
    st.header("📸 AI Prepoznavanje bolesti")
    if not ai_key: st.warning("⚠️ Unesi Gemini API ključ u Sidebar levo!")
    izvor = st.radio("Izvor:", ["Kamera", "Galerija"])
    slika = st.camera_input("Uslikaj list") if izvor == "Kamera" else st.file_uploader("Postavi sliku", type=['jpg','png'])
    if slika and ai_key and st.button("🔍 Analiziraj"):
        with st.spinner("AI analizira..."):
            st.write(analiziraj_list(slika, ai_key))

# --- EKSPORT NA DNU ---
st.markdown("---")
if st.session_state.dnevnik or st.session_state.troskovi:
    st.subheader("📓 Kompletna dokumentacija")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if st.session_state.dnevnik: pd.DataFrame(st.session_state.dnevnik).to_excel(writer, index=False, sheet_name='Dnevnik')
        if st.session_state.troskovi: pd.DataFrame(st.session_state.troskovi).to_excel(writer, index=False, sheet_name='Troskovi')
    st.download_button("📥 Preuzmi Excel izveštaj", data=output.getvalue(), file_name="agro_izvestaj.xlsx")
