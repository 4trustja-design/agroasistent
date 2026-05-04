import streamlit as st
import requests
import json

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

with st.sidebar:
    api_key = st.text_input("Unesi svoj Gemini API Ključ:", type="password")

st.title("🌾 Pametni Poljoprivredni Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Lokacija"])

def pitaj_ai(pitanje):
    # Pažljivo razdvajamo bazu i ključ
    baza_url = "https://googleapis.com"
    kompletna_adresa = f"{baza_url}?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": pitanje}]
        }]
    }
    
    try:
        response = requests.post(kompletna_adresa, headers=headers, json=data)
        odgovor_json = response.json()
        
        # Provera da li nam je Google vratio tekst
        if 'candidates' in odgovor_json:
            return odgovor_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"AI nije poslao odgovor. Proveri ključ. Poruka: {odgovor_json}"
            
    except Exception as e:
        return f"Greška u konekciji: {str(e)}"


with tab1:
    voce = st.selectbox("Voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica"])
    godina = st.slider("Starost:", 0, 5, 1)
    if st.button("Prikaži plan zaštite"):
        if api_key:
            with st.spinner("AI piše..."):
                rezultat = pitaj_ai(f"Daj detaljan plan zaštite i ishrane za {voce} u {godina}. godini u Srbiji.")
                st.markdown(rezultat)
        else:
            st.error("Unesi API ključ levo!")

with tab2:
    povrce = st.selectbox("Povrće:", ["Paradajz", "Paprika", "Krastavac"])
    if st.button("Prikaži savete"):
        if api_key:
            with st.spinner("AI piše..."):
                rezultat = pitaj_ai(f"Plan uzgoja za {povrce} u Srbiji.")
                st.markdown(rezultat)
        else:
            st.error("Unesi ključ!")

with tab3:
    st.info("Kada AI proradi, ovde stavljamo mapu.")
