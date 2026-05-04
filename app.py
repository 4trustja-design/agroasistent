import streamlit as st
import requests
import json

st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

with st.sidebar:
    api_key = st.text_input("Unesi svoj Gemini API Ključ:", type="password")

st.title("🌾 Pametni Poljoprivredni Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Lokacija"])

def pitaj_ai(pitanje):
    # Čista adresa bez ključa u linku
    url = "https://googleapis.com"
    
    # Ključ šaljemo kao parametar, ali na čistiji način
    params = {'key': api_key}
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": pitanje}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, params=params, json=data)
        
        # Ako je Google vratio grešku (npr. pogrešan ključ), ispisaće je ovde
        if response.status_code != 200:
            return f"Greška sa Google servera (Kod {response.status_code}): {response.text}"
            
        odgovor_json = response.json()
        
        # Izvlačenje teksta
        if 'candidates' in odgovor_json:
            return odgovor_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return "AI je vratio prazan odgovor. Proveri da li je API ključ ispravan."
            
    except Exception as e:
        return f"Došlo je do greške: {str(e)}"



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
