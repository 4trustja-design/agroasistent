import streamlit as st
from streamlit_folium import st_folium
import folium

# Podešavanje stranice - uvek prvi red koda
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

st.title("🌾 Pametni Poljoprivredni Savetnik")

# Glavni meni u tabovima
tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Moja Parcela"])

with tab1:
    st.header("Saveti za voćare (0-5 god)")
    voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka"])
    godina = st.slider("Starost sadnice:", 0, 5, 1)
    
    st.info(f"Prikazujem kalendar zaštite za {voce} u {godina}. godini...")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛡️ Zaštita")
        st.write("- Zimsko prskanje (Bakar)")
        # Svaki checkbox mora imati svoj key da ne bi bilo greške
        st.checkbox("Urađeno", key="check_zastita_voce")
    with col2:
        st.subheader("🧪 Prehrana")
        st.write("- Unos azotnih đubriva")
        st.checkbox("Urađeno", key="check_ishrana_voce")

with tab2:
    st.header("Saveti za povrtare")
    tip = st.radio("Uzgoj:", ["Plastenik", "Otvoreno polje"])
    povrce = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika"])
    st.success(f"Saveti za {povrce} u statusu: {tip}")
    st.checkbox("Rasad spreman", key="check_rasad")

with tab3:
    st.header("📍 Lokacija tvoje parcele")
    st.write("Klikni na mapu da obeležiš svoje imanje:")
    
    # Centriramo mapu na Srbiju (Kruševac/centralna tačka)
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    # Dodaje opciju da se vidi koordinate kad se klikne
    m.add_child(folium.LatLngPopup())
    
    st_folium(m, width=700, height=500)
