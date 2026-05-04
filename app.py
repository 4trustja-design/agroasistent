import streamlit as st
import requests
import json

# Podešavanje stranice
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide", page_icon="🌾")

# Bočni meni za podešavanja
with st.sidebar:
    st.header("⚙️ Podešavanja")
    api_key_input = st.text_input("Unesi svoj Gemini API Ključ:", type="password")
    st.info("Ključ dobijaš besplatno na Google AI Studio sajtu.")
    st.markdown("---")
    st.markdown("v1.0 | AgroAsistent")

# Glavni naslov
st.title("🌾 Pametni Poljoprivredni Savetnik")
st.markdown("Dobrodošli! Izaberite kategoriju ispod i dobićete stručne savete za vaš uzgoj.")

# Kreiranje tabova
tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Mapa i Prognoza"])

# Funkcija za komunikaciju sa AI (Gemini)
def pitaj_ai(pitanje):
    if not api_key_input:
        return "Greska: Niste uneli API ključ u levom meniju!"
    
    # Čišćenje ključa od razmaka i kosa crta
    cist_kljuc = api_key_input.strip()
    
    # Najstabilnija adresa za v1 verziju API-ja
    url = f"https://googleapis.com{cist_kljuc}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": pitanje}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        # Ako je status kod 200, sve je u redu
        if response.status_code == 200:
            odgovor_json = response.json()
            if 'candidates' in odgovor_json and len(odgovor_json['candidates']) > 0:
                return odgovor_json['candidates'][0]['content']['parts'][0]['text']
            else:
                return "AI nije vratio odgovor. Proverite da li je vaš API ključ ispravan."
        else:
            # Ispisujemo tačnu grešku ako nije 200
            return f"Greška sa Google servera (Kod {response.status_code}): {response.text}"
            
    except Exception as e:
        return f"Došlo je do greške u povezivanju: {str(e)}"

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Saveti za voćare (0-5 god)")
    col1, col2 = st.columns(2)
    
    with col1:
        voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik", "Orah", "Trešnja"])
    with col2:
        godina = st.slider("Starost sadnice (u godinama):", 0, 5, 1)
    
    if st.button(f"Generiši plan za {voce}"):
        with st.spinner(f"AI kreira plan za {voce}..."):
            savet = pitaj_ai(f"Kao stručnjak agronom, napiši detaljan plan zaštite i ishrane za {voce} u {godina}. godini uzgoja u Srbiji. Navedi konkretne faze (proleće, leto, jesen) i preporuči preparate dostupne na našem tržištu.")
            st.markdown("### 📋 Plan rada")
            st.write(savet)

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Saveti za povrtare")
    col1, col2 = st.columns(2)
    
    with col1:
        povrce = st.selectbox("Izaberi povrće:", ["Paradajz", "Paprika", "Krastavac", "Kupus", "Zelena salata", "Luk"])
    with col2:
        tip_uzgoja = st.radio("Mesto uzgoja:", ["Plastenik", "Otvoreno polje"])
    
    if st.button(f"Generiši plan za {povrce}"):
        with st.spinner(f"AI kreira plan za {povrce}..."):
            savet = pitaj_ai(f"Kao stručnjak za povrtarstvo, napiši detaljan plan zaštite i ishrane za {povrce} (uzgoj: {tip_uzgoja}) u Srbiji, od sadnje rasada do berbe.")
            st.markdown("### 📋 Plan uzgoja")
            st.write(savet)

# --- TAB 3: LOKACIJA ---
with tab3:
    st.header("📍 Lokacija i Vremenska Prognoza")
    st.info("Ovaj deo ćemo aktivirati čim potvrdimo da AI veza radi ispravno. Ovde ćete moći da vidite prognozu za vašu parcelu.")
    st.warning("Napomena: Ček lista radova biće dodata u sledećoj verziji.")
