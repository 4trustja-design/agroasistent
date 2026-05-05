import streamlit as st
from google import genai
import folium
from streamlit_folium import st_folium
import requests

# --- KONFIGURACIJA ---
st.set_page_config(page_title="AgroSmart", layout="wide")

if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ Ključ nije pronađen u Secrets!")
    st.stop()

# Inicijalizacija klijenta (Nova v1 metoda)
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("🚜 AgroAsistent")

# Jednostavna mapa
m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
folium.LatLngPopup().add_to(m)
map_data = st_folium(m, height=300, use_container_width=True)

# Unos podataka
kultura = st.selectbox("Izaberi kulturu:", ["Šljiva", "Jabuka", "Malina", "Paradajz", "Paprika"])

if st.button("Generiši savet", type="primary"):
    with st.spinner("AI agronom razmišlja..."):
        try:
            # Direktno pozivanje modela koji trenutno najbolje radi
            response = client.models.generate_content(
                model='gemini-1.5-flash', 
                contents=f"Ti si agronom. Daj 3 kratka saveta za kulturu {kultura} u maju u Srbiji. Lista."
            )
            
            if response.text:
                st.success("### Saveti agronoma:")
                st.write(response.text)
            else:
                st.warning("AI nije vratio tekst.")
        except Exception as e:
            st.error(f"Došlo je do greške: {e}")
