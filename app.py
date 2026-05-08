import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime

st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌾")

if 'dnevnik' not in st.session_state:
    st.session_state.dnevnik = []

st.title("🌾 AgroAsistent: Digitalni Dnevnik i Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Mešoviti Voćnjak", "🥦 Povrtarstvo", "📍 Moja Parcela"])

# --- TAB 1: MEŠOVITI VOĆNJAK (3. GODINA) ---
with tab1:
    st.header("🍎 Saveti za mešoviti voćnjak (3. godina)")
    st.subheader("Sastav: Šljiva, kruška, jabuka, dunja, višnja, trešnja, breskva, nektarina")
    
    mesec = st.selectbox("Izaberi trenutni mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust"])
    
    # Saveti za trogodišnja stabla
    saveti_voce = {
        "Mart": "● **Rezidba:** Završetak formiranja uzgojnog oblika. ● **Zaštita:** 'Plavo prskanje' (Bakar) pre kretanja vegetacije. ● **Đubrenje:** Unos azotnih đubriva (npr. KAN) za razvoj krošnje.",
        "April": "● **Zaštita:** Prskanje protiv monilije (u cvetu) i čađave krastavosti. ● **Prihrana:** Druga doza azota krajem meseca. ● **Održavanje:** Suzbijanje korova u redu.",
        "Maj": "● **Proređivanje:** Kod jabuke i breskve prorediti plodove ako su pregusti. ● **Zaštita:** Borba protiv lisnih vaši i rutave bube. ● **Navodnjavanje:** Početi ako je proleće sušno.",
        "Jun": "● **Letnja rezidba:** Uklanjanje 'vodopija' (uspravnih letorasta). ● **Zaštita:** Prskanje protiv smotavca jabuke i šljive. ● **Prihrana:** Preko lista (folijarno) sa kalcijumom."
    }
    
    st.info(saveti_voce.get(mesec, "Redovno pratite stanje vlage u zemljištu i pojavu štetočina."))
    
    c1, c2 = st.columns(2)
    with c1:
        v_rad = st.multiselect("Završen rad:", ["Rezidba", "Zaštita (Prskanje)", "Đubrenje", "Navodnjavanje"])
    
    if st.button("Zapiši rad u voćnjaku"):
        if v_rad:
            vreme = datetime.now().strftime("%d.%m.%Y")
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": "Mešoviti Voćnjak (3.g)", "Radovi": ", ".join(v_rad)})
            st.success("Zapisano!")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Saveti za povrtare")
    tip = st.radio("Mesto uzgoja:", ["Plastenik", "Otvoreno polje"], horizontal=True)
    
    if tip == "Plastenik":
        p_kultura = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika", "Krastavac (salatar)"])
        saveti_p = {
            "Paradajz": "● Zakidanje zaperaka (pinciranje) obavezno svake nedelje. ● Prihrana kalcijumom protiv truljenja vrha ploda. ● Provetravanje plastenika iznad 28°C.",
            "Paprika": "● Održavati visoku vlažnost vazduha. ● Zaštita od kalifornijskog tripsa. ● Redovno navodnjavanje manjim normama vode.",
            "Krastavac (salatar)": "● Vođenje na jedan ili dva kanapa. ● Zaštita od pepelnice i plamenjače. ● Prihrana kalijumom u fazi plodonošenja."
        }
    else:
        p_kultura = st.selectbox("Izaberi povrće:", ["Krompir", "Lubenica", "Beli luk", "Crni luk", "Bundeva", "Grašak", "Boranija"])
        saveti_p = {
            "Krompir": "● Suzbijanje krompirove zlatice. ● Nagrtanje zemljišta kada biljka dostigne 20cm.",
            "Lubenica": "● Zaštita od lisnih vaši. ● Navodnjavanje u fazi cvetanja i formiranja plodova.",
            "Beli luk": "● Suzbijanje lukove muve. ● Prehrana azotnim đubrivom rano u proleće.",
            "Crni luk": "● Zaštita od plamenjače (posebno posle kiše). ● Prestanak navodnjavanja 15 dana pre vađenja.",
            "Bundeva": "● Veliki razmak sadnje. ● Zaštita od pepelnice u julu.",
            "Grašak": "● Sejati što ranije. ● Navodnjavanje u fazi cvetanja i nalivanja zrna.",
            "Boranija": "● Sukcesivna setva na svakih 15 dana za berbu tokom celog leta."
        }
    
    st.success(f"📌 Savet za {p_kultura}: {saveti_p.get(p_kultura)}")
    
    p_rad = st.multiselect("Urađeno:", ["Setva/Sadnja", "Zaštita", "Prihrana", "Berba"], key="p_rad_multi")
    if st.button("Zapiši rad u povrtnjaku"):
        if p_rad:
            vreme = datetime.now().strftime("%d.%m.%Y")
            st.session_state.dnevnik.append({"Datum": vreme, "Kultura": f"{p_kultura} ({tip})", "Radovi": ", ".join(p_rad)})
            st.success("Zapisano!")

# --- TAB 3: MOJA PARCELA ---
with tab3:
    st.header("📍 Moja Parcela")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=800, height=450, key="agromapa_final")
    if izlaz_mape and izlaz_mape.get('last_clicked'):
        lat, lon = izlaz_mape['last_clicked']['lat'], izlaz_mape['last_clicked']['lng']
        st.success(f"Koordinate: {lat:.4f}, {lon:.4f}")

# --- PRIKAZ DNEVNIKA ---
st.markdown("---")
st.subheader("📓 Dnevnik polja (Istorija radova)")
if st.session_state.dnevnik:
    st.table(st.session_state.dnevnik)
    if st.button("Obriši istoriju"):
        st.session_state.dnevnik = []
        st.rerun()
else:
    st.write("Dnevnik je prazan. Zabeležite radove iznad.")
