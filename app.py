def pozovi_ai_direktno(pitanje):
    # OVO JE PUNA ADRESA KOJA MORA BITI OVAKVA:
    link = "https://googleapis.com"
    
    # Čišćenje ključa od nevidljivih razmaka
    cist_kljuc = moj_tajni_kljuc.strip()
    
    # Parametri koji se šalju Google-u
    parametri = {'key': cist_kljuc}
    zaglavlje = {'Content-Type': 'application/json'}
    podaci = {"contents": [{"parts": [{"text": pitanje}]}]}
    
    try:
        # Šaljemo zahtev na punu adresu sa ključem
        r = requests.post(link, headers=zaglavlje, params=parametri, json=podaci)
        
        if r.status_code == 200:
            return r.json()['candidates']['content']['parts']['text']
        else:
            # Ako dobijemo grešku, ispisaće nam tačan razlog od Google-a
            return f"Greška sa Google servera (Kod {r.status_code}): {r.text}"
    except Exception as e:
        return f"Greška u konekciji: {str(e)}"
