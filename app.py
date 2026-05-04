import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

with st.sidebar:
    api_key = st.text_input("Unesi svoj Gemini API Ključ:", type="password")
    st.info("Ključ uzmi na Google AI Studio.")

st.title("🌾 Pametni Poljoprivredni Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Mapa i Prognoza"])

with tab1:
    st.header("Saveti za voćare (0-5 god)")
    voca = ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik", "Orah", "Trešnja"]
    izabrano_voce = st.selectbox("Izaberi voće:", voca)
    godina = st.slider("Starost sadnice (u godinama):", 0, 5, 1)
    
    if st.button(f"Generiši plan za {izabrano_voce}"):
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Daj mi plan zaštite i ishrane za {izabrano_voce} u {godina}. godini uzgoja u Srbiji. Razdvoj zaštitu i ishranu."
            with st.spinner("AI piše..."):
                odgovor = model.generate_content(prompt)
                st.markdown(odgovor.text)
        else:
            st.error("Prvo unesi API ključ u meniju levo!")

with tab2:
    st.header("Saveti za povrtare")
    tip = st.radio("Mesto uzgoja:", ["Plastenik", "Otvoreno polje"])
    povrce = ["Paradajz", "Paprika", "Krastavac", "Kupus", "Zelena salata"]
    izabrano_povrce = st.selectbox("Izaberi povrće:", povrce)
    
    if st.button(f"Generiši plan za {izabrano_povrce}"):
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Daj mi plan zaštite i ishrane za {izabrano_povrce} ({tip}) od rasada do berbe u Srbiji."
            with st.spinner("AI piše..."):
                odgovor = model.generate_content(prompt)
                st.markdown(odgovor.text)
        else:
            st.error("Prvo unesi API ključ!")

with tab3:
    st.header("Lokacija i Vremenska Prognoza")
    st.write("Uskoro: Mapa i automatski podsetnici.")
