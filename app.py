import streamlit as st
import requests

# Ova komanda MORA biti prva i jedina u svom redu
st.set_page_config(page_title="AgroAsistent")

st.title("🌾 AgroAsistent Srbija")

# Bočni meni
moj_kljuc = st.sidebar.text_input("Unesi API ključ:", type="password")

# Glavni deo
tab1, tab2 = st.tabs(["🍎 Saveti", "📍 Mapa"])

def pitaj_ai(pitanje):
    # Koristimo najprostiju verziju linka
    url = f"https://googleapis.com{moj_kljuc.strip()}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": pitanje}]}]}
    
    try:
        r = requests.post(url, headers=headers, json=data)
        if r.status_code == 200:
            return r.json()['candidates']['content']['parts']['text']
        else:
            return f"Greška (Kod {r.status_code})"
    except:
        return "Greška u povezivanju."

with tab1:
    kultura = st.selectbox("Biljka:", ["Malina", "Paradajz", "Jabuka"])
    if st.button("Prikaži savet"):
        if moj_kljuc:
            rezultat = pitaj_ai(f"Kratak savet za {kultura} u Srbiji.")
            st.write(rezultat)
        else:
            st.error("Unesi ključ levo!")

with tab2:
    st.write("Mapa će biti ovde.")
