import streamlit as st
import requests

st.set_page_config(page_title="AgroAsistent", layout="wide")

# Menjamo naslov polja da nateramo brauzer da ne koristi staru memoriju
kljuc = st.sidebar.text_input("UNESI NOVI API KLJUČ:", type="password")

st.title("🌾 AgroAsistent Srbija")

def pozovi_ai(pitanje):
    # Proverena i najnovija putanja koju Google preporučuje za 2024. godinu
    cist_kljuc = kljuc.strip()
    adresa = f"https://googleapis.com{cist_kljuc}"
    
    zaglavlje = {'Content-Type': 'application/json'}
    podaci = {
        "contents": [{
            "parts": [{"text": pitanje}]
        }]
    }
    
    try:
        response = requests.post(adresa, headers=zaglavlje, json=podaci)
        odgovor_json = response.json()
        
        if response.status_code == 200:
            # Ako je sve u redu, uzmi tekst
            return odgovor_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # Ako opet prijavi 404, ispisaće nam tačno ŠTA Google vidi
            return f"Google javlja problem (Kod {response.status_code}): {odgovor_json.get('error', {}).get('message', 'Nepoznata greška')}"
            
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
