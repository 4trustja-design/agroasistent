import streamlit as st
import pandas as pd
from datetime import datetime

# --- PODEŠAVANJE ---
st.set_page_config(page_title="AI AgroAsistent", page_icon="🤖")

# Funkcija kojom AI generiše odgovor (Simulacija moćnog prompta)
def generisi_ai_savet(kategorija, vrsta, detalj):
    # Ovde aplikacija šalje "naredbu" AI-u
    prompt = f"Ti si stručni agronom iz Srbije. Daj precizne savete za {kategorija}: {vrsta}. "
    prompt += f"Specifičan fokus: {detalj}. "
    prompt += "Podeli odgovor na: 1. Radovi, 2. Zaštita, 3. Prehrana. Koristi kratke crte."
    
    # Za sada ćemo koristiti placeholder koji simulira AI, 
    # dok ne ubacimo tvoj OpenAI ili Gemini ključ u Streamlit Secrets.
    return f"### AI Savet za {vrsta} ({detalj})\n" + "Uskoro će se ovde pojaviti personalizovani plan generisan AI-om..."

# --- INTERFEJS ---
st.title("🤖 AI AgroAsistent Srbija")
st.markdown("Aplikacija koja koristi veštačku inteligenciju za planiranje vašeg imanja.")

glavni_meni = st.sidebar.selectbox("Izaberite sektor:", ["🍎 Voćarstvo", "🥦 Povrtarstvo"])

if glavni_meni == "🍎 Voćarstvo":
    vrsta = st.selectbox("Izaberite voće:", ["Šljiva", "Jabuka", "Malina", "Trešnja", "Lešnik", "Borovnica"])
    faza = st.select_slider("Starost/Faza:", options=["Sadnja", "1. godina", "2. godina", "3. godina", "Pun rod"])
    
    if st.button("Generiši AI plan radova"):
        with st.spinner('AI agronom analizira podatke...'):
            # Ovde pozivamo AI funkciju
            savet = generisi_ai_savet("voće", vrsta, faza)
            st.markdown(savet)

elif glavni_meni == "🥦 Povrtarstvo":
    vrsta = st.selectbox("Izaberite povrće:", ["Paradajz", "Paprika", "Krastavac", "Crni luk", "Krompir"])
    uzgoj = st.radio("Način uzgoja:", ["Plastenik", "Otvoreno polje"])
    
    if st.button("Prikaži plan proizvodnje"):
        with st.spinner('AI analizira uslove...'):
            savet = generisi_ai_savet("povrće", vrsta, uzgoj)
            st.markdown(savet)

# --- ČEK LISTA KOJA SE NE BRIŠE (Local Storage) ---
st.divider()
st.subheader("✅ Moja dnevna ček-lista")
aktivnost = st.text_input("Dodaj novu aktivnost (npr. Prskanje šljive):")
if st.button("Dodaj na listu"):
    if 'lista' not in st.session_state:
        st.session_state.lista = []
    st.session_state.lista.append(aktivnost)

if 'lista' in st.session_state:
    for stavka in st.session_state.lista:
        st.checkbox(stavka, key=stavka)
