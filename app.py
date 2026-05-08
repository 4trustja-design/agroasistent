import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime
import pandas as pd
import io

# 1. KONFIGURACIJA
st.set_page_config(page_title="AgroAsistent ORGANIC", layout="wide", page_icon="🌿")

# Inicijalizacija memorije
if 'dnevnik' not in st.session_state: st.session_state.dnevnik = []
if 'troskovi' not in st.session_state: st.session_state.troskovi = []

st.title("🌿 AgroAsistent: Organska Proizvodnja & Kalkulator")

# --- INFO PANEL ZA ORGANSKU ZAŠTITU ---
with st.expander("🛡️ PRINCIPI ZDRAVE ZAŠTITE (0 dana karence)"):
    st.markdown("""
    *   **Soda bikarbona:** Odlična protiv pepelnice (50g na 10L vode + malo tečnog sapuna).
    *   **Neem ulje:** Prirodni insekticid za vaši i tripse (0 dana karence).
    *   **Bakar (Cu):** Dozvoljen u organskoj u mirovanju (za voće).
    *   **Bacillus thuringiensis (npr. Lepinox):** Prirodni neprijatelj gusenica i zlatice.
    *   **Kopriva i Gavez:** Najbolja tečna đubriva za prehranu preko lista.
    """)

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćnjak (Organic)", "🥦 Povrće (Organic)", "💰 Kalkulator Troškova", "📍 Mapa"])

# --- TAB 1: VOĆARSTVO (ORGANIC) ---
with tab1:
    st.header("🍎 Zaštita voćnjaka na prirodan način")
    v_mesec = st.selectbox("Izaberi mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust"], key="v_m")
    
    baza_v = {
        "Mart": "🛡️ **Bakar (npr. Cuproxat):** 50g/16L. Suzbija gljivice. 🧪 **Ishrana:** Stajski gnoj ili peletirano organsko đubrivo.",
        "April": "🌸 **Cvet:** Sumpor (npr. Kumulus) protiv pepelnice. 🍯 **Za pčele:** Ne prskati ništa u punom cvetu!",
        "Maj": "🐜 **Lisne vaši:** Neem ulje (50ml/16L) ili sapunica. 🛡️ **Krastavost:** Soda bikarbona (80g/16L).",
        "Jun": "🐛 **Smotavac:** Lepinox Plus (prirodna bakterija) 15g/16L. 🧪 **Ishrana:** Tečna kopriva (1L na 10L vode).",
        "Jul": "🛡️ **Grinje:** Ekstrakt belog luka ili mineralna ulja. 💦 **Voda:** Malčiranje oko stabala slamom.",
        "Avgust": "🧺 **Berba:** Samo fizičko uklanjanje oštećenih plodova."
    }
    st.info(baza_v.get(v_mesec))
    v_rad = st.multiselect("Zapiši rad:", ["Prskanje (Organic)", "Đubrenje", "Navodnjavanje", "Rezidba"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši u dnevnik", key="v_btn"):
        if v_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m."), "Kultura": f"Voćnjak ({v_mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano!")

# --- TAB 2: POVRTARSTVO (ORGANIC) ---
with tab2:
    st.header("🥦 Zdravo povrće iz plastenika i bašte")
    tip = st.radio("Sistem uzgoja:", ["Plastenik (16x5m)", "Otvoreno polje"], horizontal=True)
    p_kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija"])
    
    organic_saveti = {
        "Paradajz": "🛡️ **Plamenjača:** Mleko i voda (1:9) ili soda bikarbona. 🧪 **Ishrana:** Gavez (bogat kalijumom).",
        "Paprika": "🐜 **Trips/Vaši:** Neem ulje ili žute lepljive ploče. 💦 **Vlažnost:** Redovno provetravanje.",
        "Krastavac": "🍄 **Pepelnica:** Soda bikarbona + malo ulja. 🧺 **Berba:** Svaki dan.",
        "Krompir": "🐞 **Zlatica:** Ručno skupljanje ili Bacillus thuringiensis. 🚜 **Nagrtanje** slamom (mulching).",
        "Luk": "🐜 **Muva:** Sadnja šargarepe pored luka (mešovita sadnja). 🛡️ **Pepelnica:** Mleko u prahu.",
        "Lubenica": "🧪 **Ishrana:** Fermentisani stajnjak kroz sistem kap po kap (proceđen).",
        "Boranija": "🛡️ **Rđa:** Sumporni preparati (niže doze). 🐝 **Oprašivanje:** Saditi cveće u blizini."
    }
    st.warning(f"📌 **Savet za {p_kultura}:** {organic_saveti[p_kultura]}")
    
    p_rad = st.multiselect("Urađeno:", ["Prirodna zaštita", "Zalivanje", "Berba", "Plastenje"], key=f"p_r_{p_kultura}")
    if st.button("Zapiši rad u povrtnjaku", key="p_btn"):
        if p_rad:
            st.session_state.dnevnik.append({"Datum": datetime.now().strftime("%d.%m."), "Kultura": p_kultura, "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: KALKULATOR TROŠKOVA ---
with tab3:
    st.header("💰 Kalkulator troškova i investicija")
    col_t1, col_t2, col_t3 = st.columns(3)
    
    with col_t1:
        stavka = st.text_input("Naziv (npr. Creva kap po kap, Seme, Neem ulje):")
    with col_t2:
        kolicina = st.number_input("Količina / Dužina:", min_value=1.0, value=1.0)
    with col_t3:
        cena = st.number_input("Cena po jedinici (RSD):", min_value=0.0, value=0.0)
    
    if st.button("Dodaj u troškovnik"):
        ukupno = kolicina * cena
        st.session_state.troskovi.append({"Stavka": stavka, "Količina": kolicina, "Iznos (RSD)": ukupno})
        st.success(f"Dodato: {stavka}")

    if st.session_state.troskovi:
        df_t = pd.DataFrame(st.session_state.troskovi)
        st.table(df_t)
        st.metric("UKUPNA INVESTICIJA:", f"{df_t['Iznos (RSD)'].sum():,.2f} RSD")

# --- TAB 4: MAPA ---
with tab4:
    st.header("📍 Moja Parcela")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    st_folium(m, width=700, height=450, key="mapa_final")

# --- EXPORT DNEVNIKA ---
st.markdown("---")
if st.session_state.dnevnik:
    st.subheader("📓 Dnevnik radova")
    df_d = pd.DataFrame(st.session_state.dnevnik)
    st.dataframe(df_d, use_container_width=True)
    
    towrite = io.BytesIO()
    df_d.to_excel(towrite, index=False, engine='xlsxwriter')
    towrite.seek(0)
    st.download_button("📥 Preuzmi Dnevnik (Excel)", data=towrite, file_name="agro_dnevnik.xlsx")
