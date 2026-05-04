import streamlit as st
import requests

# Podešavanje stranice
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

# BOČNI MENI - Promenjeno ime da se izbriše stara memorija
with st.sidebar:
    moj_tajni_kljuc = st.text_input("NALEPITE KLJUČ OVDE:", type="password")
    st.warning("Pazite da nema razmaka ispred ključa!")

st.title("🌾 AgroAsistent Srbija")

tab1, tab2 = st.tabs(["🍎 Saveti za uzgoj", "📍 Lokacija"])

def pozovi_ai_direktno(pitanje):
    # OVDE JE STROGO DEFINISANA ADRESA I KLJUČ KAO POSEBAN PARAMETAR
    url_adresa = "https://googleapis.com"
    
    # Čišćenje ključa
    cist_kljuc = moj_tajni_kljuc.strip()
    
    # Parametri se šalju odvojeno, što sprečava spajanje reči
    parametri = {'key': cist_kljuc}
    zaglavlje = {'Content-Type': 'application/json'}
    podaci = {"contents": [{"parts": [{"text": pitanje}]}]}
    
    try:
        # Koristimo params=parametri što garantuje da će se dodati znak '?' na pravo mesto
        odgovor = requests.post(url_adresa, headers=zaglavlje, params=parametri, json=podaci)
        
        if odgovor.status_code == 200:
            return odgovor.json()['candidates']['content']['parts']['text']
        else:
            return f"Greška sa servera (Kod {odgovor.status_code}): {odgovor.text}"
    except Exception as e:
        return f"Greška u konekciji: {str(e)}"

with tab1:
    kultura = st.selectbox("Izaberi biljku:", ["Malina", "Paradajz", "Jabuka", "Jagoda"])
    if st.button("Prikaži stručni savet"):
        if moj_tajni_kljuc:
            with st.spinner("AI piše plan..."):
                rezultat = pozovi_ai_direktno(f"Daj kratak plan zaštite i ishrane za {kultura} u Srbiji.")
                st.write(rezultat)
        else:
            st.error("Unesite ključ u meni sa leve strane!")

with tab2:
    st.info("Mapa će biti ovde čim potvrdimo da AI radi.")
