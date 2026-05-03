from typing import Optional

KEYWORD_RULES = [
    (["SONELGAZ", "FACTURE GAZ", "FACTURE ELEC"], 22),
    (["ADE", "FACTURE EAU"], 23),
    (["ALGERIE TELECOM", "ATM INTERNET"], 24),
    (["MOBILIS"], 41),
    (["DJEZZY"], 42),
    (["OOREDOO"], 43),
    (["YASSIR", "TEMMA", "TAXI"], 31),
    (["ETUSA", "BUS URBAIN"], 32),
    (["STATION", "NAFTAL", "CARBURANT"], 33),
    (["SNTF", "TRAIN"], 34),
    (["SALAIRE", "SOLDE MENSUEL", "TRAITEMENT", "VIREMENT SALAIRE"], 2),
    (["PRIME", "BONUS", "GRATIFICATION"], 3),
    (["MANDAT", "CCP PAIEMENT"], 81),
    (["PHARMACIE", "PARA ", "PARAPHARMACIE"], 51),
    (["CLINIQUE", "HOPITAL", "CABINET"], 52),
    (["RESTAURANT", "BRASSERIE", "PIZZERIA", "SNACK"], 13),
    (["CAFE", "PATISSERIE", "SALON DE THE"], 14),
    (["MARCHE", "EPICERIE", "SUPERETTE", "FRAIS ET LEGUMES"], 12),
    (["BARIDIMOB", "CCP MOBILE"], 83),
    (["LOYER", "LOVER"], 21),
    (["UNIVERSITE", "ECOLE", "LYCEE"], 61),
    (["MOUTON", "BETAIL", "AID ADHA"], 91),
]

def auto_categorize(label: str) -> Optional[int]:
    label_upper = label.upper()
    for keywords, category_id in KEYWORD_RULES:
        if any(kw in label_upper for kw in keywords):
            return category_id
    return 99
