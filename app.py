import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# --- 1. POSTAVKE ---
st.set_page_config(page_title="AgroAsistent Srbija", layout="wide")

# --- 2. TVOJA BAZA PODATAKA ---
vocarstvo_data = {
    "Šljiva": {
        "1. Godina": "Sadnja u jesen, skraćivanje sadnice na 80cm.",
        "Zaštita": "Plavo prskanje u fazi mirovanja.",
        "Prehrana": "Unos stajnjaka ili NPK 15:15:15 pre sadnje."
    },
    "Malina": {
        "1. Godina": "Postavljanje naslona, đubrenje azotnim đubrivima u proleće.",
        "Zaštita": "Tretman protiv didimele nakon kretanja vegetacije."
    }
}

povrtarstvo_data = {
    "Paradajz": {
        "Plastenik": "Sadnja rasada u aprilu, sistem kap po kap.",
        "Otvoreno": "Sadnja krajem maja, razmak 50cm.",
        "Zaštita": "Tretman protiv plamenjače nakon svake jače kiše.",
        "Prehrana": "Prihrana kalijumom u fazi formiranja plodova."
    }
}

# --- 3. GLAVNI INTERFEJS ---
st.title("🚜 AgroAsistent: Voćarstvo & Povrtarstvo")

# DODALI SMO ČETVRTI TAB: AI Savetnik
tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćarstvo", "🥦 Povrtarstvo", "📍 Lokacija", "🤖 AI Savetnik"])

with tab1:
    st.header("Saveti za voćare")
    voce = st.selectbox("Izaberite voćnu vrstu:", list(vocarstvo_data.keys()))
    godina = st.select_slider("Godina zasada:", options=["1. Godina", "2. Godina", "3. Godina", "4. Godina", "5. Godina"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛠 Radovi")
        st.write(vocarstvo_data[voce].get(godina, "Nema specifičnih saveta."))
    with col2:
        st.subheader("🛡 Zaštita")
        st.write(vocarstvo_data[voce]["Zaštita"])

with tab2:
    st.header("Saveti za povrtare")
    povrce = st.selectbox("Izaberite povrće:", list(povrtarstvo_data.keys()))
    tip_uzgoja = st.radio("Tip proizvodnje:", ["Plastenik", "Otvoreno"])
    st.write(povrtarstvo_data[povrce][tip_uzgoja])

with tab3:
    st.header("📍 Lokacija")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=400, width=800, key="agro_map_v8")

# --- NOVI TAB: AI SAVETNIK ---
with tab4:
    st.header("🤖 Pitajte AI Agronoma")
    st.write("Postavite specifično pitanje o bolestima, štetočinama ili uzgoju.")
    
    pitanje = st.text_area("Vaše pitanje:", placeholder="Npr: Zašto listovi paradajza žute?")
    
    if st.button("Pošalji upit", type="primary"):
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            # Direktan API poziv (najsigurnija metoda)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"Ti si stručni agronom u Srbiji. Odgovori stručno i sažeto na srpskom jeziku: {pitanje}"}]
                }]
            }
            
            with st.spinner("AI analizira vaš upit..."):
                try:
                    res = requests.post(url, json=payload, timeout=20)
                    data = res.json()
                    
                    if "candidates" in data:
                        odgovor = data["candidates"][0]["content"]["parts"][0]["text"]
                        st.info("### Odgovor AI Agronoma:")
                        st.markdown(odgovor)
                    else:
                        st.error(f"Greška servera: {data.get('error', {}).get('message', 'Nepoznat problem')}")
                except Exception as e:
                    st.error(f"Veza sa AI serverom nije uspostavljena: {e}")
        else:
            st.warning("API ključ nije podešen u Streamlit Secrets.")

st.markdown("---")
st.caption("AgroAsistent Srbija 2026 | Podaci su informativnog karaktera.")
