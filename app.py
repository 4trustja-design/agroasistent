import streamlit as st
import requests

# 1. OSNOVNA PODEŠAVANJA STRANICE
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide", page_icon="🌾")

# 2. BOČNI MENI ZA KLJUČ I PODEŠAVANJA
with st.sidebar:
    st.header("⚙️ Podešavanja")
    api_key_input = st.text_input("Unesi svoj Gemini API Ključ:", type="password")
    st.info("Ključ dobijaš besplatno na Google AI Studio.")
    st.markdown("---")
    st.write("Verzija: 1.5 (Stabilna)")

st.title("🌾 Pametni Poljoprivredni Savetnik")

# 3. GLAVNI TABOVI APLIKACIJE
tab1, tab2, tab3 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Mapa i Prognoza"])

# 4. FUNKCIJA ZA POVEZIVANJE SA AI
def pozovi_ai(pitanje):
    if not api_key_input:
        return "Greška: Niste uneli API ključ u levom meniju!"
    
    # Čistimo ključ od razmaka
    cist_kljuc = api_key_input.strip()
    
    # PUNA ADRESA KA GOOGLE SERVERU
    url = f"https://googleapis.com{cist_kljuc}"
    
    zaglavlje = {'Content-Type': 'application/json'}
    podaci = {"contents": [{"parts": [{"text": pitanje}]}]}
    
    try:
        response = requests.post(url, headers=zaglavlje, json=podaci)
        
        if response.status_code == 200:
            odgovor_json = response.json()
            return odgovor_json['candidates']['content']['parts']['text']
        else:
            return f"Greška sa servera (Kod {response.status_code}): {response.text}"
            
    except Exception as e:
        return f"Greška u konekciji: {str(e)}"

# --- TAB 1: VOĆARSTVO (0-5 GODINA) ---
with tab1:
    st.header("🍎 Saveti za voćare (mladi zasadi)")
    col1, col2 = st.columns(2)
    
    with col1:
        voce = st.selectbox("Izaberi voće:", ["Malina", "Šljiva", "Jabuka", "Borovnica", "Lešnik", "Orah", "Trešnja"])
    with col2:
        godina = st.slider("Starost sadnice (u godinama):", 0, 5, 1)
    
    if st.button(f"Prikaži plan za: {voce}"):
        with st.spinner(f"Stručnjak piše plan za {voce}..."):
            savet = pozovi_ai(f"Kao agronom, daj detaljan plan zaštite i ishrane za {voce} u {godina}. godini u Srbiji. Razdvoj zaštitu i ishranu po mesecima.")
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
    
    if st.button(f"Prikaži plan za: {povrce}"):
        with st.spinner(f"Generisanje plana za {povrce}..."):
            savet = pozovi_ai(f"Kao stručnjak za povrtarstvo, napiši plan zaštite i ishrane za {povrce} (uzgoj: {tip_uzgoja}) u Srbiji od sadnje do berbe.")
            st.markdown("### 📋 Plan uzgoja")
            st.write(savet)

# --- TAB 3: LOKACIJA I PODSETNICI ---
with tab3:
    st.header("📍 Lokacija i Vremenska Prognoza")
    st.info("Kada potvrdimo da AI veza radi, ovde dodajemo mapu i automatske podsetnike za navodnjavanje.")
    
    # Mala ček lista za poljoprivrednike (privremena verzija)
    st.subheader("✅ Ček lista radova")
    st.checkbox("Zimsko prskanje")
    st.checkbox("Đubrenje u toku")
    st.checkbox("Postavljanje sistema za navodnjavanje")
