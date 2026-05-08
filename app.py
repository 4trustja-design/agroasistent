import streamlit as st
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

st.title("🌾 Pametni Poljoprivredni Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Moja Parcela"])

with tab1:
    st.header("Saveti za voćare (0-5 god)")
    voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka"])
    godina = st.slider("Starost sadnice:", 0, 5, 1)
    
    # Ovde ćemo ubaciti tvoje fiksne savete koji uvek rade
    st.info(f"Prikazujem kalendar zaštite za {voce} u {godina}. godini...")
    
        col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛡️ Zaštita")
        st.write("- Zimsko prskanje (Bakar)")
        # Dodat jedinstveni ključ 'zastita_check'
        st.checkbox("Urađeno", key="zastita_check")
    with col2:
        st.subheader("🧪 Prehrana")
        st.write("- Unos azotnih đubriva")
        # Dodat jedinstveni ključ 'prehrana_check'
        st.checkbox("Urađeno", key="prehrana_check")


with tab2:
    st.header("Saveti za povrtare")
    tip = st.radio("Uzgoj:", ["Plastenik", "Otvoreno polje"])
    povrce = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika"])
    st.success(f"Saveti za {povrce} u statusu: {tip}")

with tab3:
    st.header("📍 Lokacija tvoje parcele")
    st.write("Klikni na mapu da obeležiš svoje imanje:")
    
    # Centriramo mapu na Srbiju
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    m.add_child(folium.LatLngPopup()) # Omogućava klik na koordinate
    
    st_folium(m, width=700, height=500)
