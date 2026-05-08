import streamlit as st
import streamlit.components.v1 as components  # OVA LINIJA IDE OVDE
import folium
from streamlit_folium import st_folium
import pandas as pd
# ... ostatak koda ...


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

# --- TAB 3: MOJA PARCELA I RADAR (BEZ KLJUČA) ---
# --- TAB 3: RADAR I MAPA (POPRAVLJENO) ---
with tab3:
    st.header("🛰️ Vremenski radar uživo (Srbija)")
    
    # Koristimo direktan link koji je stabilniji
    vreme_html = """
    <iframe src="https://vremeradar.rs" 
            width="100%" height="600" style="border:none;"></iframe>
    """
    components.html(vreme_html, height=620)
    
    st.markdown("---")
    st.subheader("🗺️ Obeleži parcelu")
    # ... ostatak koda za folium mapu ostaje isti ...

    
    # 2. PASUS: Tvoja interaktivna mapa za koordinate
    st.subheader("🗺️ Obeleži parcelu")
    m = folium.Map(location=[43.5615, 21.3696], zoom_start=12) # Centrirano na Kruševac
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=400, key="mapa_krusevac")
    
    if izlaz_mape and izlaz_mape.get('last_clicked'):
        st.success(f"Koordinate tvoje njive: {izlaz_mape['last_clicked']['lat']:.4f}, {izlaz_mape['last_clicked']['lng']:.4f}")


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
