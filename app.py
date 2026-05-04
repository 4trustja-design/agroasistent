import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

# Podešavanje API-ja direktno
with st.sidebar:
    st.header("Podešavanja")
    api_key = st.text_input("Unesi svoj Gemini API Ključ:", type="password")

st.title("🌾 Pametni Poljoprivredni Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Mapa i Prognoza"])

def pokreni_ai(pitanje):
    try:
        genai.configure(api_key=api_key)
        # Koristimo najosnovnije ime modela bez ikakvih dodataka
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(pitanje)
        return response.text
    except Exception as e:
        # Ako 'gemini-pro' ne prođe, probali smo sve verzije naziva
        return f"Greška: {str(e)}"

with tab1:
    st.header("Saveti za voćare")
    voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica"])
    godina = st.slider("Starost (god):", 0, 5, 1)
    
    if st.button("Prikaži plan"):
        if api_key:
            with st.spinner("AI piše..."):
                tekst = pokreni_ai(f"Plan zaštite i ishrane za {voce} u {godina}. godini u Srbiji.")
                st.write(tekst)
        else:
            st.error("Unesi ključ levo!")

with tab2:
    st.header("Saveti za povrtare")
    povrce = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika", "Krastavac"])
    
    if st.button("Generiši savet"):
        if api_key:
            with st.spinner("AI piše..."):
                tekst = pokreni_ai(f"Plan uzgoja za {povrce} u Srbiji.")
                st.write(tekst)
        else:
            st.error("Unesi ključ!")

with tab3:
    st.info("Mapa će biti dodata čim proradi AI veza.")
