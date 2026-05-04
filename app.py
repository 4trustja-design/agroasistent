import streamlit as st
import requests

# Podešavanje stranice
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide", page_icon="🌾")

# Bočni meni
with st.sidebar:
    st.header("⚙️ Podešavanja")
    api_key = st.text_input("Unesi svoj Gemini API Ključ:", type="password")
    st.info("Ključ dobijaš na Google AI Studio.")

st.title("🌾 Pametni Poljoprivredni Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Mapa i Prognoza"])

def pitaj_ai(pitanje):
    # KORAK 1: Koristimo v1beta verziju koja je najfleksibilnija
    cist_kljuc = api_key.strip()
    url = f"https://googleapis.com{cist_kljuc}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": pitanje}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            res = response.json()
            return res['candidates'][0]['content']['parts'][0]['text']
        else:
            # Ako dobijemo grešku, ispisaće nam tačno koji deo URL-a mu smeta
            return f"Greška (Kod {response.status_code}): {response.text}"
    except Exception as e:
        return f"Došlo je do greške: {str(e)}"

with tab1:
    voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik", "Trešnja"])
    godina = st.slider("Starost (god):", 0, 5, 1)
    if st.button(f"Prikaži plan za {voce}"):
        if api_key:
            with st.spinner("AI piše savete..."):
                odgovor = pitaj_ai(f"Kao agronom, daj plan zaštite i ishrane za {voce} u {godina}. godini u Srbiji.")
                st.markdown(odgovor)
        else:
            st.error("Unesi API ključ levo!")

with tab2:
    povrce = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika", "Krastavac", "Luk"])
    tip = st.radio("Uzgoj:", ["Plastenik", "Otvoreno polje"])
    if st.button(f"Prikaži plan za {povrce}"):
        if api_key:
            with st.spinner("AI piše..."):
                odgovor = pitaj_ai(f"Plan zaštite i ishrane za {povrce} ({tip}) u Srbiji.")
                st.markdown(odgovor)
        else:
            st.error("Unesi ključ!")

with tab3:
    st.header("📍 Lokacija i Vremenska Prognoza")
    st.info("Čim proradi AI, ovde dodajemo mapu.")
