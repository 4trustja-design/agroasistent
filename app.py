def plan_vocnjak(kultura, mesec):
    plan = {
        "Voće": {
            "Maj": [("Captan", "35 g / 16 L", "Preventiva protiv gljivičnih bolesti"),
                    ("Bor", "folijarno po etiketi", "Poboljšanje oplodnje")],
            "Jun": [("Coragen", "3 ml / 16 L", "Suzbijanje smotavca"),
                    ("Wuxal Calcium", "40 ml / 16 L", "Prihrana kalcijumom")],
            "Jul": [("Kalcijum", "po etiketi", "Kvalitet ploda i čvrstina"),
                    ("Biostimulator", "po etiketi", "Ublažavanje stresa")],
            "Avgust": [("Teldor", "15 ml / 16 L", "Zaštita od truleži pred berbu")],
            "Septembar": [("Bakreni preparat", "po etiketi", "Higijenska zaštita posle berbe")],
            "Oktobar": [("NPK 6:12:24", "po etiketi", "Jesenje đubrenje")]
        }
    }
    return plan["Voće"].get(mesec, [])

def plan_povrce(kultura, mesec):
    plan = {
        "Paradajz": {
            "Maj": [("Bakarni preparat", "po etiketi", "Prevencija plamenjače"),
                    ("Kalcijum", "30-40 ml / 16 L", "Jačanje ploda i lista")],
            "Jun": [("Bakarni preparat", "po etiketi", "Zaštita lista"),
                    ("Sumporni preparat", "po etiketi", "Ako je suvo vreme")],
        },
        "Paprika": {
            "Maj": [("Kalcijum", "30-40 ml / 16 L", "Prevencija ožegotina"),
                    ("Biostimulator", "po etiketi", "Oporavak od presadnje")],
        },
        "Krastavac": {
            "Maj": [("Sumporni preparat", "po etiketi", "Pepelnica"),
                    ("Biološki preparat", "po etiketi", "Lakša zaštita")],
        },
        "Krompir": {
            "Maj": [("Mankozeb", "po etiketi", "Preventiva protiv plamenjače"),
                    ("Bakreni preparat", "po etiketi", "Dodatna zaštita")],
        },
        "Luk": {
            "Maj": [("Bakreni preparat", "po etiketi", "Zaštita od bolesti lista")],
        },
        "Lubenica": {
            "Maj": [("Kalcijum", "30 ml / 16 L", "Kvalitet i otpornost"),
                    ("Biostimulator", "po etiketi", "Ukorenjavanje")],
        },
        "Boranija": {
            "Maj": [("Bakreni preparat", "po etiketi", "Preventiva bolesti")],
        },
        "Grašak": {
            "Maj": [("Blagi fungicid", "po etiketi", "Zaštita cveta i lista")],
        }
    }
    return plan.get(kultura, {}).get(mesec, [])
