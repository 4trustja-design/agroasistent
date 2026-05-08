import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
import requests
import io

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

if 'dnevnik' not in st.session_state: st.session_state.dnevnik = []
if 'troskovi' not in st.session_state: st.session_state.troskovi = []

st.title("🌿 AgroAsistent: Digitalni Savetnik i Dnevnik")

# 2. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    st.markdown("---")
    datum_sadnje = st.date_input("Kada si posadio glavni rasad?", datetime.now())

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Radar i Mapa", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka (3. godina)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"], key="v_m")
        saveti_v = {
        "Maj": "🛡️ **Zaštita:** Captan (35g na 16L). 🧪 **Ishrana:** Bor preko lista.",
        "Jun": "🐛 **Smotavac:** Coragen (3ml na 16L). 🧪 **Ishrana:** Kalcijum (40ml/16L).",
        "Jul": "💦 **Navodnjavanje:** Ključno za formiranje pupoljaka za dogodine.",
        "Avgust": "🍎 **Berba:** Rani sortiment. 🛡️ **Zaštita:** Paziti na karentu pred berbu.",
        "Septembar": "🧺 **Berba:** Glavna berba kasnih sorti. 🧹 **Higijena:** Skupljanje trulih plodova.",
        "Oktobar": "🧪 **Ishrana:** Jesenje đubrenje (Fosfor i Kalijum). 🚜 **Obrada:** Plitko oranje između redova."
    }

    st.info(saveti_v.get(v_mesec, "Pratite redovno stanje vlage."))
    v_rad = st.multiselect("Zapis rada:", ["Prskanje", "Đubrenje", "Navodnjavanje"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad u voćnjaku", key="v_btn"):
        if v_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m.%Y"), "Kultura": f"Voće ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano!")

# --- TAB 2: POVRTARSTVO (VRAĆENI SAVETI I NOVI KALENDAR) ---
with tab2:
    st.header("🥦 Saveti za povrće")
    
    # --- NOVO: KALENDAR UKORENJAVANJA ---
    dana_od_sadnje = (datetime.now().date() - datum_sadnje).days
    st.subheader(f"🌱 Status rasada: {dana_od_sadnje} dana od sadnje")
    
    if dana_od_sadnje < 4:
        st.error("❗ **FAZA UKORENJAVANJA:** Biljke su osetljive. **NE PRSKAJ** ničim (čak ni organski). Samo umereno zalivanje ujutru.")
    elif 4 <= dana_od_sadnje <= 10:
        st.warning("⚠️ **FAZA STABILIZACIJE:** Možeš početi sa blagim organskim sredstvima (Mleko/Voda 1:10). Izbegavaj jaku hemiju i sodu bikarbonu.")
    else:
        st.success("✅ **STABILNA BILJKA:** Biljka je razvila koren. Možeš primenjivati punu organsku i hemijsku zaštitu po potrebi.")

    st.markdown("---")
    tip = st.radio("Sistem:", ["Plastenik (16x5m)", "Otvoreno polje"], horizontal=True)
    kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak"])

    # Baza saveta za prikaz (Vraćena na tvoj zahtev)
    baza_p = {
        "Paradajz": "🌿 **Savet:** Zakidaj zaperke čim narastu 5cm. Ne kvasi list pri zalivanju. 🚑 **Hitna (3 dana karence):** Quadris.",
        "Paprika": "🐜 **Savet:** Prati pojavu tripsa. Voli visoku vlažnost u plasteniku. 🧪 **Ishrana:** Calcium (30ml/10L).",
        "Krastavac": "🥒 **Savet:** Traži vodu svaki dan. 🛡️ **Organski:** Soda bikarbona (50g/10L) protiv pepelnice.",
        "Krompir": "🐞 **Savet:** Prati zlaticu. 🛡️ **Jun:** Zaštita od plamenjače nakon kiše čim se list osuši.",
        "Lubenica": "🍉 **Savet:** Navodnjavanje u cvetanju je ključno. 🧪 **Ishrana:** Kalijum za šećer.",
        "Luk": "🐜 **Savet:** Zaštita od lukove muve. ⚠️ **Maj/Jun:** Rizik od plamenjače."
    }
    st.info(baza_p.get(kultura, "Pratite redovno stanje biljaka i vlažnost zemljišta."))

    p_rad = st.multiselect("Urađeno:", ["Sadnja", "Zaštita", "Prihrana", "Berba"], key=f"p_{kultura}_{tip}")
    if st.button("Zabeleži rad u povrtnjaku", key="p_btn"):
        if p_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m.%Y"), "Kultura": f"{kultura} ({tip})", "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: RADAR I MAPA ---
with tab3:
    st.header("🛰️ Vremenski radar uživo (Kruševac)")
    vreme_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(vreme_html, height=620)
    
    st.markdown("---")
    st.subheader("🗺️ Obeleži parcelu za precizan savet")
    m = folium.Map(location=[43.5616, 21.3694], zoom_start=15)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=450, key="agro_mapa_final_v16")
    
    # --- PAMETNI SAVET ZA NAVODNJAVANJE ---
    vlaga_za_savet = None
    temp_za_savet = None

    if izlaz_mape and izlaz_mape.get('last_clicked') and meteo_key:
        lat, lon = izlaz_mape['last_clicked']['lat'], izlaz_mape['last_clicked']['lng']
        try:
            url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key.strip()}&units=metric&lang=sr"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                d = res.json()
                vlaga_za_savet = d['main']['humidity']
                temp_za_savet = d['main']['temp']
                st.success(f"Automatski podaci: Vlaga {vlaga_za_savet}%, Temp {temp_za_savet}°C")
        except:
            st.warning("⚠️ Problem sa automatskim podacima. Koristite ručni unos.")

    if not vlaga_za_savet:
        c1, c2 = st.columns(2)
        temp_za_savet = c1.number_input("Unesi temp (°C):", value=15)
        vlaga_za_savet = c2.slider("Unesi vlažnost (%):", 0, 100, 90)

    if vlaga_za_savet and temp_za_savet:
        st.markdown("### 📢 Agronomski savet")
        if vlaga_za_savet > 85 and temp_za_savet < 20:
            st.warning(f"**Trenutno stanje u Kruševcu ({datetime.now().strftime('%H:%M')}h):** Sparina je velika ({vlaga_za_savet}%). Zemlja će biti vlažna, ne pretruj sa vodom iz kontejnera!")
        elif temp_za_savet > 30:
            st.error("Vrelo je! Ne zalivaj hladnom vodom iz bunara.")
        
        # --- RECEPT ZA PRSKALICU OD 16L ---
        if vlaga_za_savet > 80 and dana_od_sadnje > 4:
            st.markdown("---")
            st.subheader("🛡️ Organski recept za tvoju prskalicu (16L)")
            st.success("**Mleko (domaće):** 1.5L mleka + 14.5L vode. Bez karence, bezbedno za porodicu.")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovnik")
    c1, c2, c3 = st.columns(3)
    with c1: stavka = st.text_input("Stavka:")
    with c2: kol = st.number_input("Kol:", min_value=1.0, value=1.0)
    with c3: cena = st.number_input("Cena:", min_value=0.0, value=0.0)
    if st.button("Dodaj"):
        if stavka: st.session_state.troskovi.append({"Stavka": stavka, "Iznos": kol * cena})

    if st.session_state.troskovi:
        df_t = pd.DataFrame(st.session_state.troskovi)
        st.table(df_t)
        st.subheader(f"Ukupno: {df_t['Iznos'].sum():,.2f} RSD")

# --- DNEVNIK NA DNU ---
st.markdown("---")
if st.session_state.dnevnik:
    st.subheader("📓 Dnevnik")
    df_d = pd.DataFrame(st.session_state.dnevnik)
    st.table(df_d)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_d.to_excel(writer, index=False)
    st.download_button("Preuzmi Excel", data=output.getvalue(), file_name="agro_dnevnik.xlsx")
