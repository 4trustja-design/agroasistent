with tabs[2]: # DINAMIČKI AI PLANER
    mesec_naziv = meseci[datetime.now().month]
    st.header(f"📅 AI Dinamički Plan: {mesec_naziv}")
    
    # 1. Meteo podaci za kontekst
    meteo = dobij_prognozu(st.session_state.lat, st.session_state.lon)
    meteo_kontekst = ""
    if meteo:
        meteo_kontekst = f"Prognoza: {meteo['max_t']}°C, padavine {meteo['kisa']}mm."
        st.write(f"🌡️ **Trenutni uslovi:** {meteo_kontekst}")

    # 2. Odabir kulture
    izbor_biljke = st.selectbox("Za koju kulturu želiš plan?", ["Šljiva", "Malina", "Paradajz", "Jabuka", "Paprika"])

    # 3. Dugme za generisanje (da ne trošimo API ključ stalno)
    if st.button(f"Generiši plan za {izbor_biljke}"):
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            # Instrukcija za AI da vrati listu
            prompt = f"""Ti si agronom. Napravi listu od 4 konkretna i hitna zadatka za {izbor_biljke} u mjesecu {mesec_naziv} u Srbiji. 
            Uzmi u obzir i meteo uslove: {meteo_kontekst}. 
            Za svaki zadatak navedi konkretno zaštitno sredstvo ili đubrivo. 
            Odgovori isključivo u formatu:
            Zadatak 1 | Opis i sredstvo
            Zadatak 2 | Opis i sredstvo"""

            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            try:
                res = requests.post(url, json=payload, timeout=20).json()
                ai_odgovor = res["candidates"][0]["content"]["parts"][0]["text"]
                
                # Pretvaranje teksta u interaktivnu check-listu
                linije = ai_odgovor.split('\n')
                st.subheader("📋 Tvoja personalizovana check-lista:")
                
                for i, linija in enumerate(linije):
                    if "|" in linija:
                        zadatak, detalji = linija.split("|")
                        key = f"dynamic_{izbor_biljke}_{i}"
                        
                        col_c, col_t = st.columns([1, 10])
                        with col_c:
                            st.checkbox("", key=key)
                        with col_t:
                            st.markdown(f"**{zadatak.strip()}**")
                            st.caption(detalji.strip())
            except:
                st.error("AI trenutno ne može generisati plan. Pokušaj ponovo.")
        else:
            st.warning("API ključ nije podešen.")
