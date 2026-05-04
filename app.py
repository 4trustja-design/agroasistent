import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium

# 1. Povezivanje
try:
    # Proveri da li je u Streamlit Secrets ključ nazvan tačno GEMINI_API_KEY
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # Koristimo najnoviji stabilni model
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Greška pri konfiguraciji: {e}")

# 2. Funkcija koja zove AI
def dobij_ai_savet(kategorija, vrsta, detalj):
    prompt = f"Ti si agronom iz Srbije. Daj plan za {kategorija}, vrsta {vrsta}, faza {detalj}. Odgovori na srpskom."
    try:
        # Dodajemo generisanje sadržaja
        response = model.generate_content(prompt)
        if response.text:
            return response.text
        else:
            return "AI nije vratio odgovor. Pokušajte ponovo."
    except Exception as e:
        # Ako i dalje prijavljuje 404, ispisujemo tačnu grešku radi dijagnostike
        return f"Greška u modelu: {str(e)}"

# 3. Izgled aplikacije
st.set_page_config(page_title="AI AgroAsistent Srbija", page_icon="🚜")
st.title("🚜 AI AgroAsistent Srbija")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Mapa i Vreme"])

with tab1:
    voce = st.selectbox("Izaberite voće:", ["Šljiva", "Jabuka", "Malina", "Trešnja", "Lešnik", "Borovnica"])
    faza = st.select_slider("Starost/Faza:", options=["Sadnja", "1. godina", "2. godina", "3. godina", "4. godina", "Pun rod"])
    
    if st.button("Generiši AI plan za voće"):
        with st.spinner('AI agronom piše plan...'):
            savet = dobij_ai_savet("Voćarstvo", voce, faza)
            st.markdown(savet)

with tab2:
    povrce = st.selectbox("Izaberite povrće:", ["Paradajz", "Paprika", "Krastavac", "Crni luk", "Kupus"])
    uzgoj = st.radio("Način uzgoja:", ["Plastenik", "Otvoreno polje"])
    
    if st.button("Generiši AI plan za povrće"):
        with st.spinner('AI analizira uslove...'):
            savet = dobij_ai_savet("Povrtarstvo", povrce, uzgoj)
            st.markdown(savet)

with tab3:
    st.info("Kliknite na mapu da označite lokaciju vašeg zasada.")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    st_folium(m, height=300, width=800)

st.divider()
st.subheader("✅ Moja dnevna ček-lista")
aktivnost = st.text_input("Dodaj novu obavezu:")
if st.button("Dodaj"):
    if 'tasks' not in st.session_state: st.session_state.tasks = []
    st.session_state.tasks.append(aktivnost)

if 'tasks' in st.session_state:
    for t in st.session_state.tasks:
        st.checkbox(t)
