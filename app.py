import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
import requests
import io

# 1. KONFIGURACIJA STRANICE
st.set_page_config(page_title="AgroAsistent Kruševac", layout="wide", page_icon="🌾")

# Inicijalizacija memorije (da se podaci ne brišu pri promeni taba)
if 'dnevnik' not in st.session_state: st.session_state.dnevnik = []
if 'troskovi' not in st.session_state: st.session_state.troskovi = []

st.title("🌾 AgroAsistent: Digitalni Savetnik i Dnevnik")

# 2. BOČNI MENI (SIDEBAR)
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("Unesi OpenWeather API Ključ:", type="password")
    st.markdown("---")
    datum_sadnje = st.date_input("Kada si posadio glavni rasad?", datetime.now())
    st.markdown("---")
    if st.button("❌ Obriši sve podatke sezone"):
        st.session_state.dnevnik = []
        st.session_state.troskovi = []
        st.rerun()

# 3. GLAVNI TABOVI
tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Radar i Savet", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka (3. godina)")
    st.write("Sastav: Šljiva, kruška, jabuka, dunja, višnja, trešnja, breskva i nektarina")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"], key="v_m")
    
    baza_v = {
        "Maj": "🛡️ **Zaštita:** Captan (35g na 16L). 🧪 **Ishrana:** Bor preko lista za bolju oplodnju.",
        "Jun": "🐛 **Smotavac:** Coragen (3ml na 16L). 🧪 **Ishrana:** Kalcijum (Wuxal Calcium) - 40ml/16L.",
        "Jul": "💦 **Navodnjavanje:** Kritično za formiranje pupoljaka. 🛡️ **Grinje:** Envidor (10ml na 16L).",
        "Avgust": "🍎 **Berba:** Rani sortiment. 🛡️ **Teldor** (15ml na 16L) - karenca samo 3 dana.",
        "Septembar": "🧺 **Berba:** Glavna berba. 🧹 **Higijena:** Skupljanje mumificiranih plodova.",
        "Oktobar": "🧪 **Ishrana:** Jesenje đubrenje (NPK 6:12:24) - 300g po stablu."
    }
    st.info(baza_v.get(v_mesec, "Pratite redovno stanje vlage i higijenu voćnjaka."))
    
    v_rad = st.multiselect("Zapis rada:", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba", "Kosidba"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad u voćnjaku", key="v_btn"):
        if v_rad:
            vreme = datetime.now().strftime("%d.%m.%Y")
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": f"Voće ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano u dnevnik!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Povrtarstvo i Mešovita sadnja")
    
    # Izračunavanje starosti rasada
    razlika = (datetime.now().date() - datum_sadnje).days
    st.subheader(f"🌱 Status rasada: {razlika} dana od sadnje")
    
    if razlika < 4:
        st.error("❗ **FAZA UKORENJAVANJA:** Ne prskaj ničim! Samo umereno zalivanje ujutru.")
    elif 4 <= razlika <= 10:
        st.warning("⚠️ **FAZA STABILIZACIJE:** Može blagi rastvor mleka (1:10). Izbegavaj sodu bikarbonu još malo.")
    else:
        st.success("✅ **STABILNA BILJKA:** Možeš primenjivati punu organsku ili hitnu hemijsku zaštitu.")

    with st.expander("🤝 Vodič za prirodnu zaštitu (Šta saditi pored čega)"):
        st.markdown("* **Luk + Šargarepa:** Teraju muve. * **Paradajz + Bosiljak:** Bolji ukus i manje vaši. * **Krompir + Pasulj:** Pasulj daje azot krompiru.")

    st.markdown("---")
    tip = st.radio("Sistem uzgoja:", ["Plastenik (16x5m)", "Otvoreno polje"], horizontal=True)
    kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak", "Bundeva"])
    
    baza_p = {
        "Paradajz": "🌿 **Savet:** Zakidaj zaperke. 🛡️ **Organski:** Mleko/Voda. 🚑 **Hitna:** Quadris (K: 3 dana).",
        "Paprika": "🐜 **Savet:** Prati tripsa. 🧪 **Ishrana:** Kalcijum u koren (30ml/10L).",
        "Krastavac": "🥒 **Savet:** Zalivaj svaki dan ujutru. 🛡️ **Organski:** Soda bikarbona.",
        "Krompir": "🐞 **Savet:** Prati zlaticu. 🚜 **Maj:** Nagrtanje zemlje oko stabljike.",
        "Luk": "⚠️ **Savet:** Pazite na plamenjaču luka posle svake kiše!",
        "Lubenica": "🍉 **Savet:** Navodnjavanje u fazi cvetanja je presudno za prinos."
    }
    st.warning(f"📌 **{kultura}:** {baza_p.get(kultura, 'Pratite vlagu i opšte stanje.')}")
    
    p_rad = st.multiselect("Urađeno:", ["Sadnja", "Zaštita", "Prihrana", "Zalivanje", "Berba"], key=f"p_{kultura}_{tip}")
    if st.button("Zapiši rad u povrtnjaku", key="p_btn"):
        if p_rad:
            vreme = datetime.now().strftime("%d.%m.%Y")
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": f"{kultura} ({tip})", "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: RADAR I PAMETNI SAVET ---
with tab3:
    st.header("🛰️ Radar i Pametni Saveti (Kruševac)")
    v_html = """<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>"""
    components.html(v_html, height=620)
    
    st.markdown("---")
    st.subheader("🗺️ Lokacija i Meteo Alarm")
    m = folium.Map(location=[43.5616, 21.3694], zoom_start=15)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=400, key="agro_mapa_final")
    
    vlaga_s = 50
    temp_s = 20

    if izlaz_mape and izlaz_mape.get('last_clicked') and meteo_key:
        lat, lon = izlaz_mape['last_clicked']['lat'], izlaz_mape['last_clicked']['lng']
        try:
            url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key.strip()}&units=metric&lang=sr"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                d = res.json()
                vlaga_s = d['main']['humidity']
                temp_s = d['main']['temp']
                st.success(f"Automatski podaci: Vlaga {vlaga_s}%, Temp {temp_s}°C")
        except:
            st.warning("⚠️ Internet veza prekinuta. Koristi ručni unos ispod.")

    if 'd' not in locals(): # Ako automatika nije proradila
        c1, c2 = st.columns(2)
        temp_s = c1.number_input("Trenutna Temp (°C):", value=15)
        vlaga_s = c2.slider("Trenutna Vlažnost (%):", 0, 100, 90)

    st.markdown("### 📢 Agronomski savet za trenutno stanje")
    if vlaga_s > 85 and temp_s < 20:
        st.warning(f"**SPARINA:** Vlažnost je {vlaga_s}%. Ne preteruj sa vodom sutra ujutru i obavezno provetri plastenik!")
    elif temp_s > 30:
        st.error("🚨 **VRELO:** Ne zalivaj hladnom vodom iz bunara! Biljke će doživeti šok.")
    
    if vlaga_s > 80 and razlika > 4:
        st.success("🛡️ **PREPORUKA ZA 16L:** 1.5L mleka + 14.5L vode. Prskaj čim se list prosuši.")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    st.header("💰 Troškovnik (Creva, Seme, Preparati)")
    col1, col2, col3 = st.columns(3)
    stavka = col1.text_input("Naziv stavke:")
    kolicina = col2.number_input("Količina:", min_value=1.0, value=1.0)
    cena = col3.number_input("Cena (RSD):", min_value=0.0)
    
    if st.button("Dodaj trošak"):
        if stavka:
            st.session_state.troskovi.append({"Stavka": stavka, "Iznos": kolicina * cena})
            st.success("Dodato!")

    if st.session_state.troskovi:
        df_t = pd.DataFrame(st.session_state.troskovi)
        st.table(df_t)
        st.subheader(f"Ukupno uloženo: {df_t['Iznos'].sum():,.2f} RSD")

# --- DNEVNIK I EXPORT ---
st.markdown("---")
if st.session_state.dnevnik or st.session_state.troskovi:
    st.subheader("📓 Kompletna evidencija sezone")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if st.session_state.dnevnik:
            df_d = pd.DataFrame(st.session_state.dnevnik)
            st.write("**Radovi:**")
            st.table(df_d)
            df_d.to_excel(writer, index=False, sheet_name='Dnevnik_Radova')
        if st.session_state.troskovi:
            df_t = pd.DataFrame(st.session_state.troskovi)
            df_t.to_excel(writer, index=False, sheet_name='Troskovi')
    
    st.download_button("📥 Preuzmi Excel izveštaj", data=output.getvalue(), file_name="agro_izvestaj.xlsx")
