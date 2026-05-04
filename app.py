import streamlit as st
import requests

st.set_page_config(page_title="AgroAsistent", layout="wide")

# Menjamo naslov polja da nateramo brauzer da ne koristi staru memoriju
kljuc = st.sidebar.text_input("UNESI NOVI API KLJUČ:", type="password")

st.title("🌾 AgroAsistent Srbija")

def pozovi_ai(pitanje):
    # Proverena putanja sa v1beta verzijom i stabilnim modelom
    adresa = "https://googleapis.com"
    
    parametri = {'key': kljuc.strip()}
    zaglavlje = {'Content-Type': 'application/json'}
    podaci = {"contents": [{"parts": [{"text": pitanje}]}]}
    
    try:
        # Koristimo timeout da aplikacija ne bi "visila" ako Google ne odgovara
        r = requests.post(adresa, headers=zaglavlje, params=parametri, json=podaci, timeout=10)
        
        if r.status_code == 200:
            return r.json()['candidates']['content']['parts']['text']
        else:
            return f"Problem na Google serveru (Status: {r.status_code}). Proveri da li je ključ ispravan."
    except Exception as e:
        return f"Greška u konekciji: {str(e)}"

# Glavni deo aplikacije
tab1, tab2 = st.tabs(["Saveti za uzgoj", "Mapa lokacije"])

with tab1:
    voce = st.selectbox("Izaberi kulturu:", ["Malina", "Paradajz", "Jabuka", "Šljiva"])
    if st.button("Prikaži plan"):
        if kljuc:
            with st.spinner("AI generiše savete..."):
                odgovor = pozovi_ai(f"Daj kratke savete za zaštitu i ishranu za {voce} u Srbiji.")
                st.write(odgovor)
        else:
            st.error("Unesi API ključ u meni sa leve strane!")

with tab2:
    st.info("Mapa će biti aktivirana čim potvrdimo rad AI asistenta.")
