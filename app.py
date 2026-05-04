import streamlit as st
import requests

# 1. Osnovna podešavanja - mora biti na samom vrhu
st.set_page_config(page_title="AgroAsistent", layout="wide")

# 2. Bočni meni
with st.sidebar:
    st.header("Podešavanja")
    moj_kljuc = st.text_input("Unesi API ključ:", type="password")

st.title("🌾 AgroAsistent Srbija")

# 3. Funkcija za AI
def pitaj_ai(pitanje):
    # Puna i tacna adresa
    url = "https://googleapis.com"
    parametri = {'key': moj_kljuc.strip()}
    zaglavlje = {'Content-Type': 'application/json'}
    podaci = {"contents": [{"parts": [{"text": pitanje}]}]}
    
    try:
        r = requests.post(url, headers=zaglavlje, params=parametri, json=podaci)
        if r.status_code == 200:
            return r.json()['candidates']['content']['parts']['text']
        else:
            return f"Greška (Kod {r.status_code}): {r.text}"
    except Exception as e:
        return f"Greška u konekciji: {str(e)}"

# 4. Interfejs
tab1, tab2 = st.tabs(["🍎 Saveti", "📍 Mapa"])

with tab1:
    kultura = st.selectbox("Izaberi biljku:", ["Malina", "Paradajz", "Jabuka"])
    if st.button("Prikaži savet"):
        if moj_kljuc:
            with st.spinner("AI piše..."):
                odgovor = pitaj_ai(f"Daj kratak savet za uzgoj {kultura} u Srbiji.")
                st.write(odgovor)
        else:
            st.error("Unesi ključ u meni levo!")

with tab2:
    st.write("Mapa će biti aktivna čim proradi AI.")
