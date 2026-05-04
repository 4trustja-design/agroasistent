def pitaj_ai(pitanje):
    # Koristimo v1 verziju i stariji, ali ultra-stabilan model koji ne baca 404
    cist_kljuc = moj_kljuc.strip()
    url = f"https://googleapis.com{cist_kljuc}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": pitanje}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            res_json = response.json()
            return res_json['candidates']['content']['parts']['text']
        else:
            # Ako dobijemo grešku, ovde će pisati TAČAN RAZLOG (npr. neispravan ključ)
            return f"Greška sa servera (Kod {response.status_code}): {response.text}"
            
    except Exception as e:
        return f"Greška u konekciji: {str(e)}"
