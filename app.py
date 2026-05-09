import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="AgroAsistent Kruševac", layout="wide", page_icon="🌾")

try:
    TOKEN = st.secrets["GITHUB_TOKEN"].strip()
    USER = "4trustja-design"
    REPO = "NAZIV_TVOG_REPOZITORIJUMA"
except Exception:
    st.error("⚠️ Greška: Niste ispravno popunili Secrets u Streamlit podešavanjima!")
    st.stop()

FILE_PATH = "dnevnik.csv"

def snimi_na_github(kultura, radnja):
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        sha = None
        stari_sadrzaj = ""

        if res.status_code == 200:
            podaci = res.json()
            sha = podaci.get("sha")
            stari_sadrzaj = base64.b64decode(podaci["content"]).decode("utf-8")

        vreme = datetime.now().strftime("%d.%m.%Y %H:%M")
        novi_red = f"{vreme},{kultura},{radnja.replace(',', ' ')}\n"

        if not stari_sadrzaj:
            finalni_sadrzaj = "Datum,Kultura,Rad\n" + novi_red
        else:
            if not stari_sadrzaj.endswith("\n"):
                stari_sadrzaj += "\n"
            finalni_sadrzaj = stari_sadrzaj + novi_red

        payload = {
            "message": f"Unos: {kultura}",
            "content": base64.b64encode(finalni_sadrzaj.encode("utf-8")).decode("utf-8"),
        }
        if sha:
            payload["sha"] = sha

        r = requests.put(url, headers=headers, json=payload, timeout=10)

        if r.status_code in [200, 201]:
            st.success("✅ Podaci su trajno sačuvani na GitHub!")
            st.balloons()
            st.rerun()
        else:
            st.error(f"Greška {r.status_code}: {r.text}")

    except Exception as e:
        st.error(f"Kritična greška: {e}")

def savet_po_vremenu(kultura, temp_c, vlaga, vetar, padavine_pct, kisa):
    saveti = []

    if kisa or padavine_pct >= 60:
        saveti.append("🌧️ Najavljena je kiša: ne zalivaj i odloži zaštitu.")
    elif temp_c >= 25 and vlaga < 60:
        saveti.append("☀️ Toplo i suvo: pojačaj navodnjavanje ujutru ili uveče.")
    elif temp_c < 15 and vlaga > 75:
        saveti.append("🌫️ Hladno i vlažno: smanji zalivanje i prati pojavu bolesti.")
    else:
        saveti.append("💧 Zalivanje prilagodi stanju zemljišta, ne po navici.")

    if vetar >= 15:
        saveti.append("💨 Jak vetar: ne prskaj zbog zanošenja preparata.")
    if vlaga >= 80:
        saveti.append("🛡️ Visoka vlažnost: povećan rizik od gljivičnih bolesti.")

    if kultura in ["Paradajz", "Paprika", "Krastavac"]:
        saveti.append("🌿 Osetljiva kultura: ne kvasi list ako je vreme vlažno.")
    if kultura in ["Lubenica", "Boranija"]:
        saveti.append("🌱 Pazi na preterano zalivanje nakon padavina.")

    return saveti

st.title("🌾 AgroAsistent: Digitalni Savetnik i Dnevnik")

with st.sidebar:
    st.header("⚙️ Podešavanja")
    datum_sadnje = st.date_input("Kada ste posadili poslednji rasad?", datetime.now())
    st.markdown("---")
    st.info("Podaci se čuvaju u `dnevnik.csv` na vašem GitHub-u.")

tab1, tab2, tab3, tab4 = st.tabs(["🍎 Voćnjak (3.g)", "🥦 Povrtarstvo", "📍 Radar i Savet", "💰 Troškovnik"])

with tab1:
    st.header("🍎 Zaštita i Ishrana Voćnjaka (3. godina)")
    v_mesec = st.selectbox("Izaberi mesec:", ["Maj", "Jun", "Jul", "Avgust", "Septembar", "Oktobar"], key="v_m")
    baza_v = {
        "Maj": "🛡️ Zaštita: Captan (35g na 16L). Ishrana: Bor preko lista za bolju oplodnju.",
        "Jun": "🐛 Smotavac: Coragen (3ml na 16L). Ishrana: Kalcijum (Wuxal Calcium) - 40ml/16L.",
        "Jul": "💦 Navodnjavanje: Kritično za formiranje pupoljaka.",
        "Avgust": "🍎 Berba: Rani sortiment. Teldor (15ml na 16L) - kratka karenca.",
        "Septembar": "🧺 Berba: Glavna berba. Higijena: Skupljanje trulih plodova.",
        "Oktobar": "🧪 Ishrana: Jesenje đubrenje (NPK 6:12:24)."
    }
    st.info(baza_v.get(v_mesec, "Pratite redovno stanje."))
    v_rad = st.multiselect("Šta ste radili?", ["Prskanje", "Đubrenje", "Navodnjavanje", "Rezidba"], key=f"v_r_{v_mesec}")
    if st.button("Zapiši rad u voćnjaku"):
        if v_rad:
            snimi_na_github(f"Voće ({v_mesec})", ", ".join(v_rad))
        else:
            st.warning("Izaberi bar jednu aktivnost.")

with tab2:
    st.header("🥦 Saveti i Mešovita sadnja")
    razlika = (datetime.now().date() - datum_sadnje).days
    st.subheader(f"🌱 Status rasada: {razlika} dana")

    if razlika < 4:
        st.error("❗ UKORENJAVANJE: Ne prskaj ničim! Samo umereno zalivanje ujutru.")
    elif 4 <= razlika <= 10:
        st.warning("⚠️ STABILIZACIJA: Može mleko (1:10). Bez sode bikarbone.")
    else:
        st.success("✅ STABILNA BILJKA: Možeš početi sa redovnom zaštitom.")

    with st.expander("🤝 Vodič: Šta saditi pored čega"):
        st.write("Luk + Šargarepa (teraju muve). Paradajz + Bosiljak (ukus i vaši). Krompir + Pasulj (azot).")

    st.markdown("---")
    kultura = st.selectbox("Kultura:", ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak"])
    baza_p = {
        "Paradajz": "🌿 Maj: Ukorenjavanje i pinciranje. Ne kvasi list!",
        "Paprika": "🧪 Maj: Prihrana kalcijumom. Prati tripsa.",
        "Krastavac": "🥒 Maj: Vođenje na kanap. Soda bikarbona protiv pepelnice.",
        "Krompir": "🚜 Maj: Nagrtanje. Zlatica: Ručno skupljanje jaja.",
        "Lubenica": "🍉 Maj: Ukorenjavanje. Ne preteruj sa vodom.",
        "Grašak": "🌸 Maj: Cvetanje! Obavezno navodnjavanje.",
        "Boranija": "🌱 Maj: Setva ili okopavanje tek ponikle."
    }
    st.info(baza_p.get(kultura, "Pratite vlažnost."))

    p_rad = st.multiselect("Šta je urađeno?", ["Sadnja", "Zalivanje", "Zaštita", "Berba"], key=f"p_{kultura}")
    if st.button("Zapiši rad u povrtnjaku"):
        if p_rad:
            snimi_na_github(kultura, ", ".join(p_rad))
        else:
            st.warning("Izaberi bar jednu aktivnost.")

with tab3:
    st.header("🛰️ Radar i Pametni Savet")
    components.html(
        '<iframe src="https://vremeradar.rs" width="100%" height="600" style="border:none;"></iframe>',
        height=620
    )

    st.markdown("---")
    st.subheader("📢 Agronomski savet za Kruševac")

    temp_c = st.slider("Temperatura (°C):", -10, 45, 12)
    vlaga = st.slider("Vlažnost (%):", 0, 100, 81)
    vetar = st.slider("Brzina vetra (km/h):", 0, 80, 7)
    padavine_pct = st.slider("Verovatnoća padavina (%):", 0, 100, 60)
    kisa = st.checkbox("Pada kiša / očekuje se kiša", value=True)

    if "razlika" in locals():
        if vlaga > 85:
            st.warning(f"**PAŽNJA:** Velika sparina ({vlaga}%). Ne preteruj sa vodom i obavezno provetri plastenik!")
        if vlaga > 80 and razlika > 4:
            st.info("🛡️ RECEPT (16L): 1.5L mleka + 14.5L vode. Prskaj čim se list prosuši.")

    savet_kultura = st.selectbox(
        "Za koju kulturu želiš savet?",
        ["Paradajz", "Paprika", "Krastavac", "Krompir", "Luk", "Lubenica", "Boranija", "Grašak"],
        key="savet_kultura"
    )

    saveti = savet_po_vremenu(savet_kultura, temp_c, vlaga, vetar, padavine_pct, kisa)

    st.subheader("Saveti prema vremenu")
    for s in saveti:
        st.info(s)

with tab4:
    st.header("💰 Troškovnik")
    stavka = st.text_input("Naziv investicije:")
    iznos = st.number_input("Iznos (RSD):", min_value=0.0)
    if st.button("Zapiši trošak"):
        if stavka:
            snimi_na_github("TROŠAK", f"{stavka}: {iznos} RSD")
        else:
            st.warning("Unesi naziv troška.")

st.write("---")
st.subheader("📓 Tvoj digitalni dnevnik (Uživo)")

try:
    url_raw = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{FILE_PATH}"
    df = pd.read_csv(f"{url_raw}?v={datetime.now().timestamp()}")
    st.dataframe(df.tail(20), use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Preuzmi tabelu kao CSV",
        data=csv,
        file_name="dnevnik.csv",
        mime="text/csv",
    )
except Exception:
    st.info("Tabela će se pojaviti ovde nakon prvog uspešnog upisa.")
