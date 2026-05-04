import streamlit as st
import requests

st.set_page_config(page_title="AgroAsistent", layout="wide")

# Koristimo polje koje se ne zove isto kao u starom kodu da izbegnemo memoriju brauzera
kljuc_za_ai = st.sidebar.text_input("UNESI API KLJUČ OVDE:", type="password")

st.title("🌾 AgroAsistent Srbija")

tab1, tab2 = st.tabs(["Saveti", "Mapa"])

def pozovi_gemini(pitanje):
    # OVDE SMO STAVILI RAZMAK I STROGO ODVOJILI KLJUČ
    link = "https://googleapis.com"
    parametri = {'key': kljuc_za_ai.strip()}
    zaglavlje = {'Content-Type': 'application/json'}
    podaci = {"contents": [{"parts": [{"text": pitanje}]}]}
    
    try:
        r = requests.post(link, headers=zaglavlje, params=parametri, json=podaci)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Greška sa servera: {r.text}"
    except Exception as e:
        return f"Greška u kodu: {str(e)}"

with tab1:
    kultura = st.selectbox("Izaberi:", ["Malina", "Paradajz", "Jabuka"])
    if st.button("Prikaži savet"):
        if kljuc_za_ai:
            with st.spinner("AI razmišlja..."):
                odgovor = pozovi_gemini(f"Daj kratak savet za uzgoj {kultura} u Srbiji.")
                st.write(odgovor)
        else:
            st.warning("Prvo unesi ključ levo!")
