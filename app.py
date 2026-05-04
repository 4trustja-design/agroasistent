import streamlit as st
import google.generativeai as genai
import folium
from streamlit_folium import st_folium

# 1. Povezivanje sa tvojim API ključem
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # KORISTIMO NOVIJI MODEL KOJI JE DOSTUPAN
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error("Greška: Proveri 'Secrets' na Streamlit-u ili API ključ.")

# 2. Funkcija koja zove AI (dodata bolja kontrola grešaka)
def dobij_ai_savet(kategorija, vrsta, detalj):
    prompt = f"""
    Ti si stručni agronom iz Srbije. Korisnik gaji {vrsta} ({kategorija}) u fazi/uslovima: {detalj}.
    Daj mu konkretan plan radova, zaštite i prihrane za podneblje Srbije.
    Odgovori na srpskom, koristi emotikone i budi veoma precizan.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Došlo je do greške: {str(e)}"

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
