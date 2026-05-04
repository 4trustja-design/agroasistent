import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium

# 1. Povezivanje sa AI modelom
try:
    # Izvlačimo ključ iz Streamlit Secrets
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # Pokušavamo da automatski nađemo najbolji dostupan model
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Ako nađe modele, uzima prvi (najčešće flash), ako ne, koristi fiksni naziv
        selected_model = models[0] if models else 'gemini-1.5-flash'
        model = genai.GenerativeModel(selected_model)
    except:
        # Rezervna varijanta ako lista modela ne može da se učita
        model = genai.GenerativeModel('gemini-1.5-flash')

except Exception as e:
    st.error(f"Kritična greška u konfiguraciji: {e}")

# 2. Funkcija za generisanje saveta
def dobij_ai_savet(kategorija, vrsta, detalj):
    prompt = f"Ti si agronom iz Srbije. Daj plan za {kategorija}, vrsta {vrsta}, faza {detalj}. Odgovori na srpskom jeziku sa emotikonima."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI trenutno nije dostupan: {str(e)}"

# --- INTERFEJS ---
st.set_page_config(page_title="AgroAI Srbija", layout="wide")
st.title("🚜 AgroAI Srbija")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Mapa"])

with tab1:
    voce = st.selectbox("Izaberite voće:", ["Šljiva", "Jabuka", "Malina", "Trešnja"])
    faza = st.select_slider("Faza:", options=["Sadnja", "1. godina", "2. godina", "Pun rod"])
    if st.button("Generiši plan"):
        with st.spinner("AI piše savet..."):
            st.markdown(dobij_ai_savet("Voćarstvo", voce, faza))

with tab2:
    povrce = st.selectbox("Izaberite povrće:", ["Paradajz", "Paprika", "Krastavac"])
    tip = st.radio("Tip:", ["Plastenik", "Otvoreno polje"])
    if st.button("Prikaži plan"):
        with st.spinner("AI analizira..."):
            st.markdown(dobij_ai_savet("Povrtarstvo", povrce, tip))

with tab3:
    st.write("Lokacija vašeg imanja:")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    st_folium(m, height=400, width=800)
