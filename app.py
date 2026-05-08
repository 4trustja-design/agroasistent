import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime
import pandas as pd
import requests
import io

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

# Inicijalizacija memorije
if 'dnevnik' not in st.session_state: st.session_state.dnevnik = []
if 'troskovi' not in st.session_state: st.session_state.troskovi = []

st.title("🌿 AgroAsistent: Lični Savetnik i Digitalni Dnevnik")

# --- BOČNI MENI ---
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("Unesi OpenWeather Ključ:", type="password")
    st.info("Ključ je potreban za pametna upozorenja o plamenjači u Tabu 3.")
    if st.button("❌ Obriši sve podatke"):
        st.session_state.dnevnik = []
        st.session_state.troskovi = []
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Mapa i Alarm", "💰 Troškovnik"])

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita voćnjaka (3. godina)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust"], key="v_m")
    
    baza_v = {
        "Maj": {
            "Organski": "🌿 **Neem ulje** (50ml/16L) za vaši + **Soda bikarbona** (50g/10L) za krastavost.",
            "Hitna": "🚑 **Captan 80 WG** (35g/16L) - Karenca: 21 dan. (Ako se krastavost već pojavila)."
        },
        "Jun": {
            "Organski": "🌿 **Lepinox Plus** (15g/16L) - prirodno protiv crva. 🧪 **Ishrana:** Tečna kopriva.",
            "Hitna": "🚑 **Coragen 20 SC** (3ml/16L) - Karenca: 14 dana. (Zaustavlja smotavca)."
        }
    }
    info_v = baza_v.get(v_mesec, {"Organski": "Bakar u mirovanju (Mart).", "Hitna": "Pratiti opšte stanje."})
    st.success(info_v["Organski"])
    st.error(info_v["Hitna"])
    
    v_rad = st.multiselect("Šta je urađeno:", ["Organska zaštita", "Hemijska zaštita", "Đubrenje", "Navodnjavanje"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši u dnevnik", key="v_btn"):
        if v_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m."), "Kultura": f"Voćnjak ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zabeleženo!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Zaštita i plan za povrće")
    tip = st.radio("Sistem:", ["Plastenik (16x5m)", "Otvoreno polje"], horizontal=True)
    kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak"])
    
    baza_p = {
        "Paradajz": {"Org": "🌿 **Polyversum** ili Mleko/Voda (1:9). Karenca: 0 dana.", "Hitna": "🚑 **Quadris** (15ml/16L). Karenca: 3 dana."},
        "Krompir": {"Org": "🌿 **Lepinox** (zlatica) + **Fitobakter** (plamenjača).", "Hitna": "🚑 **Ridomil Gold** (40g/16L). Karenca: 21 dan."},
        "Krastavac": {"Org": "🌿 **Soda bikarbona** (50g/10L) + tečni sapun.", "Hitna": "🚑 **Equation Pro** (10g/16L). Karenca: 3 dana."},
        "Paprika": {"Org": "🌿 **Neem ulje** (trips/vaši) + žute ploče.", "Hitna": "🚑 **Exirel** (10ml/16L). Karenca: 1 dan."}
    }
    info_p = baza_p.get(kultura, {"Org": "Preventiva sodom ili mlekom.", "Hitna": "Kontaktni fungicid po potrebi."})
    st.success(f"📌 **Organski savet:** {info_p['Org']}")
    st.error(f"🚑 **Hitna hemija:** {info_p['Hitna']}")
    
    p_rad = st.multiselect("Urađeno:", ["Prirodna zaštita", "Hemijska zaštita", "Zalivanje", "Berba"], key=f"p_r_{kultura}_{tip}")
    if st.button("Zapiši rad", key="p_btn"):
        if p_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m."), "Kultura": f"{kultura} ({tip})", "Radovi": ", ".join(p_rad)})
            st.success("Dodato u digitalnu knjigu!")

# --- TAB 3: MAPA I METEO ALARM (FINALNA POPRAVKA) ---
with tab3:
    st.header("📍 Pametni Alarm za prskanje")
    st.write("Kliknite na mapu da vidite prognozu za vašu tačku:")
    
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=400, key="agro_mapa_v8")

    if izlaz_mape and izlaz_mape.get('last_clicked'):
        lat = izlaz_mape['last_clicked']['lat']
        lon = izlaz_mape['last_clicked']['lng']
        
        if not meteo_key:
            st.warning("⚠️ Unesite ključ u levi meni.")
        else:
            try:
                # Koristimo timeout i strip() da očistimo ključ
                cist_kljuc = meteo_key.strip()
                url = f"https://openweathermap.org"
                parametri = {
                    'lat': lat,
                    'lon': lon,
                    'appid': cist_kljuc,
                    'units': 'metric',
                    'lang': 'sr'
                }
                
                odgovor = requests.get(url, params=parametri, timeout=10)
                podaci = odgovor.json()
                
                if odgovor.status_code == 200:
                    vlaga = podaci['main']['humidity']
                    temp = podaci['main']['temp']
                    st.success(f"Lokacija potvrđena: {lat:.4f}, {lon:.4f}")
                    col1, col2 = st.columns(2)
                    col1.metric("Vlažnost", f"{vlaga}%")
                    col2.metric("Temperatura", f"{temp}°C")
                    
                    if vlaga > 80 and temp > 15:
                        st.error("🚨 **ALARM:** Uslovi za plamenjaču! Poprskaj čim se list osuši!")
                    else:
                        st.success("✅ Uslovi su stabilni.")
                else:
                    st.error(f"Greška {odgovor.status_code}: {podaci.get('message', 'Nepoznat problem')}")
            except Exception as e:
                st.error(f"Sistemska greška: {e}")

# --- TAB 4: TROŠKOVNIK (POPRAVLJENO) ---
with tab4:
    st.header("💰 Troškovi (Creva, Seme, Preparati)")
    c1, c2, c3 = st.columns(3)
    with c1: stavka = st.text_input("Naziv stavke (npr. Creva 16mm):")
    with c2: kol = st.number_input("Količina:", min_value=1.0, value=1.0)
    with c3: cena = st.number_input("Cena (RSD):", min_value=0.0, value=0.0)
    
    if st.button("Dodaj trošak"):
        if stavka:
            st.session_state.troskovi.append({"Stavka": stavka, "Iznos (RSD)": kol * cena})
            st.success(f"Dodato: {stavka}")
        else:
            st.warning("Unesite naziv stavke!")

    if st.session_state.troskovi:
        df_t = pd.DataFrame(st.session_state.troskovi)
        st.table(df_t)
        ukupno = df_t['Iznos (RSD)'].sum()
        st.subheader(f"Ukupna investicija: {ukupno:,.2f} RSD")

# --- DNEVNIK I EXPORT NA DNU ---
st.markdown("---")
if st.session_state.dnevnik:
    st.subheader("📓 Digitalna knjiga polja")
    df_d = pd.DataFrame(st.session_state.dnevnik)
    st.dataframe(df_d, use_container_width=True)
    
    towrite = io.BytesIO()
    df_d.to_excel(towrite, index=False, engine='xlsxwriter')
    towrite.seek(0)
    st.download_button("📥 Preuzmi Dnevnik (Excel)", data=towrite, file_name="agro_dnevnik.xlsx")
