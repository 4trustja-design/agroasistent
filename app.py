import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime

# 1. Osnovna podešavanja aplikacije
st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

# Inicijalizacija dnevnika u memoriji
if 'dnevnik' not in st.session_state:
    st.session_state.dnevnik = []

st.title("🌾 AgroAsistent: Digitalni Dnevnik i Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Mešoviti Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# --- TAB 1: MEŠOVITI VOĆNJAK (3. GODINA) ---
with tab1:
    st.header("🍎 Saveti za mešoviti voćnjak (3. godina)")
    st.write("**Sastav:** Šljiva, kruška, jabuka, dunja, višnja, trešnja, breskva, nektarina")
    
    mesec = st.selectbox("Izaberi trenutni mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust", "Septembar"])
    
    # Baza saveta po mesecima za 3. godinu
    saveti_mesecno = {
        "Mart": "● **Rezidba:** Završetak formiranja uzgojnog oblika. ● **Zaštita:** 'Plavo prskanje' (Bakar) pre vegetacije. ● **Đubrenje:** Unos azota (KAN) za razvoj krošnje.",
        "April": "● **Zaštita:** Prskanje protiv monilije i čađave krastavosti. ● **Prihrana:** Druga doza azota krajem meseca.",
        "Maj": "● **Proređivanje:** Prorediti plodove kod breskve i jabuke. ● **Zaštita:** Lisne vaši i rutava buba. ● **Navodnjavanje:** Početi ako je sušno.",
        "Jun": "● **Letnja rezidba:** Uklanjanje 'vodopija'. ● **Zaštita:** Smotavac jabuke i šljive. ● **Prihrana:** Kalcijum preko lista.",
        "Jul": "● **Navodnjavanje:** Ključno za nalivanje plodova. ● **Zaštita:** Drugo pokolenje smotavca i grinje.",
        "Avgust": "● **Berba:** Rane sorte jabuka i šljiva. ● **Higijena:** Uklanjanje trulih plodova sa stabla.",
        "Septembar": "● **Berba:** Glavna sezona jabuka i krušaka. ● **Priprema:** Planiranje jesenjeg đubrenja (P i K)."
    }
    
    st.info(saveti_mesecno.get(mesec))
    
    # Resetuje se čim promeniš mesec jer je mesec deo 'key' parametra
    v_rad = st.multiselect("Završen rad u ovom mesecu:", 
                           ["Rezidba", "Zaštita (Prskanje)", "Đubrenje", "Navodnjavanje", "Kosidba trave"],
                           key=f"v_rad_{mesec}")
    
    if st.button("Zapiši u dnevnik", key="v_btn"):
        if v_rad:
            vreme = datetime.now().strftime("%d.%m.%Y")
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": f"Voćnjak ({mesec})", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano u dnevnik!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Saveti za povrtare")
    tip = st.radio("Mesto uzgoja:", ["Plastenik", "Otvoreno polje"], horizontal=True)
    
    if tip == "Plastenik":
        p_kultura = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika", "Krastavac (salatar)"])
        saveti_p = {
            "Paradajz": "● Zakidanje zaperaka svake nedelje. ● Prihrana kalcijumom protiv truljenja vrha ploda. ● Provetravanje iznad 28°C.",
            "Paprika": "● Održavati vlažnost vazduha. ● Zaštita od tripsa. ● Često navodnjavanje manjim normama.",
            "Krastavac (salatar)": "● Vođenje na kanap. ● Zaštita od pepelnice i plamenjače. ● Prihrana kalijumom tokom berbe."
        }
    else:
        p_kultura = st.selectbox("Izaberi povrće:", ["Krompir", "Lubenica", "Beli luk", "Crni luk", "Bundeva", "Grašak", "Boranija"])
        saveti_p = {
            "Krompir": "● Suzbijanje zlatice. ● Nagrtanje kada dostigne 20cm. ● Zaštita od plamenjače.",
            "Lubenica": "● Navodnjavanje tokom cvetanja. ● Zaštita od lisnih vaši i grinja.",
            "Beli luk": "● Suzbijanje lukove muve. ● Prehrana azotom rano u proleće.",
            "Crni luk": "● Zaštita od plamenjače posle kiše. ● Prestanak zalivanja 15 dana pre vađenja.",
            "Bundeva": "● Veliki razmak sadnje. ● Zaštita od pepelnice u julu.",
            "Grašak": "● Sejati što ranije (februar/mart). ● Navodnjavanje u fazi nalivanja zrna.",
            "Boranija": "● Sukcesivna setva na 15 dana. ● Zaštita od rđe i vaši."
        }
    
    st.success(saveti_p.get(p_kultura))
    
    # Resetuje se pri promeni kulture ili tipa uzgoja
    p_rad = st.multiselect("Urađeno:", ["Sadnja", "Zaštita", "Prihrana", "Okopavanje", "Berba"], 
                           key=f"p_rad_{p_kultura}_{tip}")
    
    if st.button("Zapiši rad u povrtnjaku", key="p_btn"):
        if p_rad:
            vreme = datetime.now().strftime("%d.%m.%Y")
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": f"{p_kultura} ({tip})", "Radovi": ", ".join(p_rad)})
            st.success("Zabeleženo!")

# --- TAB 3: MOJA PARCELA ---
with tab3:
    st.header("📍 Lokacija Parcele")
    st.write("Klikni na mapu da obeležiš svoje imanje:")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=800, height=450, key="agro_mapa")
    if izlaz_mape and izlaz_mape.get('last_clicked'):
        st.success(f"Koordinate: {izlaz_mape['last_clicked']['lat']:.4f}, {izlaz_mape['last_clicked']['lng']:.4f}")

# --- PRIKAZ DNEVNIKA ---
st.markdown("---")
st.subheader("📓 Dnevnik polja (Istorija)")
if st.session_state.dnevnik:
    st.table(st.session_state.dnevnik)
    if st.button("Obriši istoriju radova"):
        st.session_state.dnevnik = []
        st.rerun()
else:
    st.write("Dnevnik je prazan. Zabeležite radove iznad.")
