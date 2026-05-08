import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
import requests
import io

# 1. OSNOVNA PODEŠAVANJA
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

if 'dnevnik' not in st.session_state: st.session_state.dnevnik = []
if 'troskovi' not in st.session_state: st.session_state.troskovi = []

st.title("🌾 AgroAsistent: Digitalni Savetnik i Dnevnik")

# 2. BOČNI MENI
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    st.markdown("---")
    datum_sadnje = st.date_input("Kada si posadio glavni rasad?", datetime.now())
    if st.button("❌ Obriši sve podatke"):
        st.session_state.dnevnik = []
        st.session_state.troskovi = []
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Radar i Mapa", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka (3. godina)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"], key="v_m")
    
    baza_v = {
        "Mart": "🛡️ Bakar (50g/16L) pre pupoljaka. 🧪 KAN 27% (250g po stablu).",
        "April": "🌸 Signum (10g/16L) u cvetu. 🛡️ Score (5ml/16L) za krastavost.",
        "Maj": "🛡️ Captan (35g/16L). 🧪 Bor (20ml/10L) folijarno za bolju oplodnju.",
        "Jun": "🐛 Coragen (3ml/16L). 🧪 Kalcijum (40ml/16L) protiv pucanja plodova.",
        "Jul": "💦 Navodnjavanje! 🛡️ Envidor (10ml/16L) protiv grinja i crvenog pauka.",
        "Avgust": "🧺 Berba ranih sorti. 🛡️ Teldor (15ml/16L) pred berbu (kratka karenca).",
        "Septembar": "🧺 Berba kasnih sorti. 🧹 Higijena: Skupljanje mumificiranih plodova.",
        "Oktobar": "🧪 Jesenje đubrenje (Fosfor i Kalijum - NPK 6:12:24). 🚜 Plitka obrada."
    }
    st.info(baza_v.get(v_mesec))
    v_rad = st.multiselect("Zapis rada:", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad u voćnjaku", key="v_btn"):
        if v_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m.%Y"), "Kultura": f"Voće ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Saveti za povrće i Mešovita sadnja")
    
    # --- KALENDAR UKORENJAVANJA ---
    dana_od_sadnje = (datetime.now().date() - datum_sadnje).days
    st.subheader(f"🌱 Status rasada: {dana_od_sadnje} dana od sadnje")
    if dana_od_sadnje < 4:
        st.error("❗ **UKORENJAVANJE:** Ne prskaj ničim! Samo umereno zalivanje ujutru.")
    elif 4 <= dana_od_sadnje <= 10:
        st.warning("⚠️ **STABILIZACIJA:** Može blagi rastvor mleka (1:10). Bez sode bikarbone.")
    else:
        st.success("✅ **STABILNA BILJKA:** Možeš početi sa redovnom zaštitom.")

    # --- VODIČ ZA MEŠOVITU SADNJU ---
    with st.expander("🤝 Vodič: Šta saditi pored čega (Prirodna zaštita)"):
        st.markdown("""
        *   **Paradajz voli:** Bosiljak (tera muve), Šargarepu, Crni luk.
        *   **Krompir voli:** Ren (poboljšava ukus), Pasulj (obogaćuje zemlju azotom).
        *   **Luk i Šargarepa:** Najbolji prijatelji! Teraju jedno drugom muve.
        *   **Lubenica voli:** Neven (uništava nematode u zemlji).
        *   **Krastavac voli:** Pasulj i Grašak, ali NE VOLI krompir.
        *   **Bela Rada i Kadifa:** Sadi ih svuda između povrća, teraju većinu štetočina!
        """)

    st.markdown("---")
    tip = st.radio("Sistem:", ["Plastenik (16x5m)", "Otvoreno polje"], horizontal=True)
    povrce = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak", "Bundeva"])

    baza_p = {
        "Paradajz": "🌿 **Maj:** Ukorenjavanje i pinciranje (zaperci). 🛡️ Ne kvasi list!",
        "Paprika": "🧪 **Maj:** Prihrana kalcijumom. 🐜 Prati pojavu tripsa u plasteniku.",
        "Krastavac": "🥒 **Maj:** Vođenje na kanap. 🛡️ Soda bikarbona protiv pepelnice.",
        "Krompir": "🚜 **Maj:** Nagrtanje i zlatica (uništavaj jaja). 🛡️ Jun: Zaštita od plamenjače.",
        "Lubenica": "🍉 **Maj:** Ukorenjavanje. 💦 Ne preteruj sa vodom dok ne krene vreža.",
        "Luk": "⚠️ **Maj:** Kritično za plamenjaču luka! 🐜 Zaštita od lukove muve.",
        "Grašak": "🌸 **Maj:** CVETANJE! Obavezno navodnjavanje ako nema kiše.",
        "Boranija": "🌱 **Maj:** Setva ili okopavanje tek ponikle boranije.",
        "Bundeva": "🎃 **Maj:** Direktna setva ili iznošenje rasada u toplu zemlju."
    }
    st.info(baza_p.get(povrce))

    p_rad = st.multiselect("Urađeno:", ["Sadnja", "Zaštita", "Prihrana", "Okopavanje"], key=f"p_{povrce}_{tip}")
    if st.button("Zabeleži rad u povrtnjaku", key="p_btn"):
        if p_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m.%Y"), "Kultura": f"{povrce} ({tip})", "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: RADAR I MAPA ---
with tab3:
    st.header("🛰️ Radar i Pametni Saveti")
    v_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(v_html, height=620)
    
    st.markdown("---")
    st.subheader("🗺️ Obeleži parcelu")
    m = folium.Map(location=[43.5616, 21.3694], zoom_start=15)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=450, key="agro_mapa_final_v20")
    
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
                st.success(f"Vlaga: {vlaga_za_savet}% | Temp: {temp_za_savet}°C")
        except:
            st.warning("⚠️ Internet veza prekinuta. Koristi ručne kontrole ispod.")

    if not vlaga_za_savet:
        c1, c2 = st.columns(2)
        temp_za_savet = c1.number_input("Temp (°C):", value=15)
        vlaga_za_savet = c2.slider("Vlaga (%):", 0, 100, 90)

    if vlaga_za_savet and temp_za_savet:
        st.markdown("### 📢 Agronomski savet za Kruševac")
        if vlaga_za_savet > 85 and temp_za_savet < 20:
            st.warning(f"**PAŽNJA:** Velika sparina ({vlaga_za_savet}%). Zemlja je vlažna, ne preteruj sa vodom sutra ujutru! Obavezno provetri plastenik.")
        elif temp_za_savet > 30:
            st.error("🚨 **VRELO:** Ne zalivaj hladnom vodom iz bunara! Biljke će doživeti šok.")
        
        if vlaga_za_savet > 80 and dana_od_sadnje > 4:
            st.info("**RECEPT (16L):** 1.5L mleka + 14.5L vode. Prskaj čim se list prosuši.")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovnik")
    c1, c2, c3 = st.columns(3)
    stavka = c1.text_input("Stavka (npr. Creva kap po kap):")
    kol = c2.number_input("Količina:", min_value=1.0, value=1.0)
    cena = c3.number_input("Cena (RSD):", min_value=0.0)
    if st.button("Dodaj stavku"):
        if stavka: st.session_state.troskovi.append({"Stavka": stavka, "Iznos": kol * cena})
    if st.session_state.troskovi:
        st.table(pd.DataFrame(st.session_state.troskovi))
        st.subheader(f"Ukupno: {pd.DataFrame(st.session_state.troskovi)['Iznos'].sum():,.2f} RSD")

# --- DNEVNIK I EKSPORT NA DNU ---
st.markdown("---")
if st.session_state.dnevnik or st.session_state.troskovi:
    st.subheader("📓 Kompletna evidencija sezone")
    
    # Prikaz radova ako postoje
    if st.session_state.dnevnik:
        st.write("**Zabeleženi radovi:**")
        df_d = pd.DataFrame(st.session_state.dnevnik)
        st.table(df_d)
    
    # Dugme za preuzimanje SVEGA u jedan fajl
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Prvi list: Radovi
        if st.session_state.dnevnik:
            df_d = pd.DataFrame(st.session_state.dnevnik)
            df_d.to_excel(writer, index=False, sheet_name='Dnevnik_Radova')
        
        # Drugi list: Troskovi
        if st.session_state.troskovi:
            df_t = pd.DataFrame(st.session_state.troskovi)
            df_t.to_excel(writer, index=False, sheet_name='Troškovi_Investicije')
    
    st.download_button(
        label="📥 Preuzmi sve (Excel sa dva lista)",
        data=output.getvalue(),
        file_name=f"AgroAsistent_Izvestaj_{datetime.now().strftime('%d_%m')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Evidencija je prazna. Unesite radove ili troškove da biste aktivirali preuzimanje.")

    st.download_button("📥 Preuzmi Excel", data=output.getvalue(), file_name="agro_dnevnik.xlsx")
