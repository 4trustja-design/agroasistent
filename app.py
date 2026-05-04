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
    # Pažljivo čišćenje ključa
    cist_kljuc = moj_kljuc.strip()
    
    # Direktna v1 putanja koja je najstabilnija
    url = f"https://googleapis.com{cist_kljuc}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": pitanje}]
        }]
    }
    
    try:
        # Povećavamo timeout da aplikacija ne pukne prebrzo
        r = requests.post(url, headers=headers, json=data, timeout=15)
        
        # Ako dobijemo odgovor od Gugla
        if r.status_code == 200:
            odgovor_json = r.json()
            return odgovor_json['candidates']['content']['parts']['text']
        else:
            # Ispisujemo tačnu poruku greške koju nam Gugl šalje
            return f"Gugl kaže (Kod {r.status_code}): {r.text}"
            
    except Exception as e:
        return f"Sistemska greška: {str(e)}"


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
