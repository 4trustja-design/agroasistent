import streamlit as st
import requests
import json

# Podešavanje stranice
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide", page_icon="🌾")

# Bočni meni
with st.sidebar:
    st.header("⚙️ Podešavanja")
    api_key = st.text_input("Unesi svoj Gemini API Ključ:", type="password")
    st.info("Ključ dobijaš na Google AI Studio.")
    st.markdown("---")
    st.write("Verzija: 1.2 (Stabilna)")

st.title("🌾 Pametni Poljoprivredni Savetnik")

tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Mapa i Prognoza"])

def pitaj_ai(pitanje):
    if not api_key:
        return "Greška: Niste uneli API ključ!"
    
    # Čistimo ključ od razmaka
    cist_kljuc = api_key.strip()
    
    # DIREKTNA PUTANJA (v1beta je trenutno najpouzdanija za nove ključeve)
    url = f"https://googleapis.com{cist_kljuc}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": pitanje}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        
        # Provera da li je Google vratio tekst
        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in res_json:
            return f"Greška od Google-a: {res_json['error']['message']}"
        else:
            return f"Neobičan odgovor od AI: {json.dumps(res_json)}"
            
    except Exception as e:
        return f"Došlo je do greške u povezivanju: {str(e)}"

# --- VOĆARSTVO ---
with tab1:
    st.header("Saveti za voćare (0-5 god)")
    voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik", "Orah", "Trešnja"])
    godina = st.slider("Starost sadnice (godina):", 0, 5, 1)
    
    if st.button(f"Prikaži plan za: {voce}"):
        with st.spinner("AI piše savete..."):
            rezultat = pitaj_ai(f"Kao agronom, daj detaljan plan zaštite i ishrane za {voce} u {godina}. godini uzgoja u Srbiji. Navedi faze i preparate.")
            st.markdown(rezultat)

# --- POVRTARSTVO ---
with tab2:
    st.header("Saveti za povrtare")
    povrce = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika", "Krastavac", "Kupus", "Luk"])
    tip = st.radio("Način uzgoja:", ["Plastenik", "Otvoreno polje"])
    
    if st.button(f"Prikaži plan za: {povrce}"):
        with st.spinner("AI piše savete..."):
            rezultat = pitaj_ai(f"Kao stručnjak za povrtarstvo, napiši plan zaštite i ishrane za {povrce} ({tip}) u Srbiji.")
            st.markdown(rezultat)

# --- LOKACIJA ---
with tab3:
    st.info("Kada potvrdimo da AI veza radi, ovde ubacujemo mapu za tvoju lokaciju.")
