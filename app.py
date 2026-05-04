import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

with st.sidebar:
    st.header("Podešavanja")
    api_key = st.text_input("Unesi svoj Gemini API Ključ:", type="password")
    st.info("Ključ uzmi na Google AI Studio.")

st.title("🌾 Pametni Poljoprivredni Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Mapa i Prognoza"])

def generisi_savet(prompt):
    try:
        # Konfiguracija sa eksplicitnim modelom 1.5-flash koji je najstabilniji
        genai.configure(api_key=api_key)
        
        # Forsiramo model koji sigurno radi na v1 verziji API-ja
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sistemska greška: {str(e)}"

with tab1:
    st.header("Saveti za voćare (0-5 god)")
    voca = ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik", "Orah", "Trešnja"]
    izabrano_voce = st.selectbox("Izaberi voće:", voca)
    godina = st.slider("Starost sadnice (u godinama):", 0, 5, 1)
    
    if st.button(f"Generiši plan za {izabrano_voce}"):
        if api_key:
            with st.spinner("AI piše savete..."):
                prompt = f"Kao agronom, daj plan zaštite i ishrane za {izabrano_voce} u {godina}. godini uzgoja u Srbiji."
                rezultat = generisi_savet(prompt)
                st.markdown(rezultat)
        else:
            st.error("Unesi API ključ levo!")

with tab2:
    st.header("Saveti za povrtare")
    tip = st.radio("Mesto uzgoja:", ["Plastenik", "Otvoreno polje"])
    povrce = ["Paradajz", "Paprika", "Krastavac", "Kupus", "Zelena salata"]
    izabrano_povrce = st.selectbox("Izaberi povrće:", povrce)
    
    if st.button(f"Generiši plan za {izabrano_povrce}"):
        if api_key:
            with st.spinner("AI piše savete..."):
                prompt = f"Plan zaštite i ishrane za {izabrano_povrce} ({tip}) u Srbiji."
                rezultat = generisi_savet(prompt)
                st.markdown(rezultat)
        else:
            st.error("Unesi API ključ!")

with tab3:
    st.header("Lokacija i Vremenska Prognoza")
    st.info("Ovaj deo aktiviramo čim se AI poveže.")
