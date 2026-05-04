import streamlit as st
import google.generativeai as genai

# Osnovna podešavanja aplikacije
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide", page_icon="🌾")

# Bočni meni za ključ
with st.sidebar:
    st.header("🔑 Pristup")
    api_key = st.text_input("Unesi svoj Gemini API Ključ:", type="password")
    st.info("Ključ uzmi na Google AI Studio sajtu.")

st.title("🌾 Pametni Poljoprivredni Savetnik")

# Glavni tabovi
tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Lokacija i Mapa"])

def generisi_savet(prompt):
    try:
        genai.configure(api_key=api_key.strip())
        # Menjamo način pozivanja i dodajemo konfiguraciju
        model = genai.GenerativeModel(
            model_name="gemini-1.0-pro",
            generation_config={
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Ako ni ovo ne proradi, ispisujemo precizniju grešku
        return f"Sistemska blokada: {str(e)}. Pokušajte da kreirate potpuno NOV ključ na AI Studio-u."


with tab1:
    st.header("Saveti za voćare (0-5 god)")
    voca = ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik", "Orah", "Trešnja"]
    izabrano_voce = st.selectbox("Izaberi voće:", voca)
    godina = st.slider("Starost sadnice (u godinama):", 0, 5, 1)
    
    if st.button(f"Prikaži plan za {izabrano_voce}"):
        if api_key:
            with st.spinner("AI stručnjak piše plan..."):
                plan = generisi_savet(f"Kao agronom, daj plan zaštite i ishrane za {izabrano_voce} u {godina}. godini u Srbiji.")
                st.markdown(plan)
        else:
            st.error("Prvo unesi API ključ sa leve strane!")

with tab2:
    st.header("Saveti za povrtare")
    povrce = ["Paradajz", "Paprika", "Krastavac", "Kupus", "Zelena salata", "Luk"]
    izabrano_povrce = st.selectbox("Izaberi povrće:", povrce)
    tip = st.radio("Način uzgoja:", ["Plastenik", "Otvoreno polje"])
    
    if st.button(f"Generiši savet za {izabrano_povrce}"):
        if api_key:
            with st.spinner("AI piše savete..."):
                plan = generisi_savet(f"Plan zaštite i ishrane za {izabrano_povrce} ({tip}) u Srbiji.")
                st.markdown(plan)
        else:
            st.error("Unesi API ključ!")

with tab3:
    st.info("Kada potvrdimo da AI radi, ovde dodajemo mapu i prognozu.")
