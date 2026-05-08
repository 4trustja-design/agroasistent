import streamlit as st
from streamlit_folium import st_folium
import folium
from datetime import datetime
import pandas as pd
import requests
import io

st.set_page_config(page_title="AgroAsistent Pro", layout="wide", page_icon="🌿")

if 'dnevnik' not in st.session_state: st.session_state.dnevnik = []

st.title("🌿 AgroAsistent: Pametna Organska Zaštita")

# --- BOČNI MENI ---
with st.sidebar:
    st.header("⚙️ Podešavanja")
    meteo_key = st.text_input("Unesi OpenWeather Ključ:", type="password")
    st.info("Ključ je potreban za pametna upozorenja o plamenjači.")

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćnjak", "🥦 Povrće", "📍 Mapa i Alarm", "💰 Troškovnik"])

# --- FUNKCIJA ZA PAMETNU PREPORUKU ---
def meteo_alarm(vazduh_vlaga, temp):
    if vazduh_vlaga > 80 and temp > 15:
        return "🚨 **ALARM:** Visoka vlaga i toplota! Idealno za plamenjaču. Poprskati u narednih 24h!"
    elif temp < 2:
        return "❄️ **ALARM:** Mraz u najavi! Štitite mlade zasade voća."
    return "✅ Uslovi su stabilni. Držite se redovnog organskog plana."

# --- TAB 1: VOĆARSTVO ---
with tab1:
    st.header("🍎 Zaštita voćnjaka (3. godina)")
    v_mesec = st.selectbox("Mesec:", ["Mart", "April", "Maj", "Jun", "Jul", "Avgust"])
    
    baza_v = {
        "Maj": {
            "Organski": "Neem ulje (50ml/16L) za vaši + Soda bikarbona (50g/10L) za krastavost.",
            "Hitna_Hemija": "Mancogal (40g/16L) - Karenca: 21 dan. (Samo ako se bolest širi)."
        },
        "Jun": {
            "Organski": "Lepinox Plus (15g/16L) protiv crva. Bacillus thuringiensis podloga.",
            "Hitna_Hemija": "Coragen (3ml/16L) - Karenca: 14 dana. (Ako su plodovi već napadnuti)."
        }
    }
    info = baza_v.get(v_mesec, {"Organski": "Bakar u mirovanju, posle soda i mleko.", "Hitna_Hemija": "Pratiti stanje."})
    st.success(f"🌿 **Organska opcija:** {info['Organski']}")
    st.error(f"🚑 **Hitna hemija (ako mora):** {info['Hitna_Hemija']}")

# --- TAB 2: POVRTARSTVO ---
with tab2:
    st.header("🥦 Zaštita povrća")
    tip = st.radio("Sistem:", ["Plastenik", "Otvoreno polje"], horizontal=True)
    kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk"])
    
    baza_p = {
        "Paradajz": {
            "Organski": "Polyversum (prirodna gljiva) ili mešavina Mleko/Voda (1:9). Karenca: 0 dana.",
            "Hitna_Hemija": "Quadris (15ml/16L). **Karenca: samo 3 dana.** Najbolje za plastenik."
        },
        "Krompir": {
            "Organski": "Fitobakter (za plamenjaču) + Lepinox (za zlaticu). Karenca: 0 dana.",
            "Hitna_Hemija": "Ridomil Gold (40g/16L). **Karenca: 21 dan.** Koristiti samo pre formiranja krtola."
        },
        "Krastavac": {
            "Organski": "Soda bikarbona (50g/10L) + sapun. Karenca: 0 dana.",
            "Hitna_Hemija": "Equation Pro (10g/16L). **Karenca: 3 dana.**"
        }
    }
    p_info = baza_p.get(kultura, {"Organski": "Preventiva mlekom.", "Hitna_Hemija": "Kontaktni fungicidi."})
    st.success(f"🌿 **Organski:** {p_info['Organski']}")
    st.error(f"🚑 **Hitna hemija:** {p_info['Hitna_Hemija']}")

# --- TAB 3: MAPA I METEO ALARM ---
with tab3:
    st.header("📍 Pametni meteo nadzor")
    m = folium.Map(location=[44.0165, 21.0059], zoom_start=7)
    folium.LatLngPopup().add_to(m)
    izlaz_mape = st_folium(m, width=700, height=450, key="mapa_v4")

    if izlaz_mape and izlaz_mape.get('last_clicked'):
        lat, lon = izlaz_mape['last_clicked']['lat'], izlaz_mape['last_clicked']['lng']
        if meteo_key:
            url = f"https://openweathermap.org{lat}&lon={lon}&appid={meteo_key}&units=metric&lang=sr"
            d = requests.get(url).json()
            if "main" in d:
                vlaga = d['main']['humidity']
                temp = d['main']['temp']
                st.metric("Vlažnost vazduha", f"{vlaga}%")
                st.write(meteo_alarm(vlaga, temp))
            else: st.error("Meteo ključ ne radi.")
        else: st.warning("Unesi meteo ključ u sidebar za pametne savete.")

# --- TAB 4: TROŠKOVNIK ---
with tab4:
    # (Kalkulator troškova ostaje isti kao u prošlom kodu)
    pass
