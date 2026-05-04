import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

with st.sidebar:
    st.header("Podešavanja")
    api_key = st.text_input("Unesite svoj Gemini API Ključ:", type="password")
    st.info("Ključ uzmite na Google AI Studio.")

st.title("🌾 Pametni Poljoprivredni Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Mapa i Prognoza"])

def generisi_savet(prompt):
    try:
        # Konfiguracija
        genai.configure(api_key=api_key)
        
        # OVO JE KLJUČNA PROMENA: 
        # Koristimo model 'gemini-1.5-flash-latest' koji je najdostupniji za nove ključeve
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Ako i ovo ne uspe, ispisaće nam tačno zašto
        return f"Došlo je do greške: {str(e)}"

with tab1:
    st.header("Saveti za voćare (0-5 god)")
    voca = ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik", "Orah", "Trešnja"]
    izabrano_voce = st.selectbox("Izaberite voće:", voca)
    godina = st.slider("Starost sadnice (u godinama):", 0, 5, 1)
    
    if st.button(f"Generišite plan za {izabrano_voce}"):
        if api_key:
            with st.spinner("AI piše savete..."):
                prompt = f"Kao stručnjak agronom, napišite detaljan plan zaštite i ishrane za {izabrano_voce} u {godina}. godini uzgoja u Srbiji. Koristite lokalne preparate."
                rezultat = generisi_savet(prompt)
                st.markdown(rezultat)
        else:
            st.error("Prvo unesite API ključ u levom meniju!")

with tab2:
    st.header("Saveti za povrtare")
    tip = st.radio("Mesto uzgoja:", ["Plastenik", "Otvoreno polje"])
    povrce = ["Paradajz", "Paprika", "Krastavac", "Kupus", "Zelena salata"]
    izabrano_povrce = st.selectbox("Izaberite povrće:", povrce)
    
    if st.button(f"Generišite plan za {izabrano_povrce}"):
        if api_key:
            with st.spinner("AI piše savete..."):
                prompt = f"Kao stručnjak za povrtarstvo, napišite plan zaštite i ishrane za {izabrano_povrce} (uzgoj: {tip}) u Srbiji."
                rezultat = generisi_savet(prompt)
                st.markdown(rezultat)
        else:
            st.error("Unesite API ključ!")

with tab3:
    st.header("Lokacija i Vremenska Prognoza")
    st.info("Kada stabilizujemo AI, ovde dodajemo mapu.")
