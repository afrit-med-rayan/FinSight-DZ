from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.category import Category

CATEGORIES = [
    # INCOME (is_income=True)
    {"id": 1, "name_fr": "Revenus", "name_ar": "الدخل", "icon_slug": "trending-up", "parent_id": None, "is_income": True, "is_essential": False},
    {"id": 2, "name_fr": "Salaire", "name_ar": "الراتب", "icon_slug": "briefcase", "parent_id": 1, "is_income": True, "is_essential": False},
    {"id": 3, "name_fr": "Prime / Bonus", "name_ar": "مكافأة", "icon_slug": "gift", "parent_id": 1, "is_income": True, "is_essential": False},
    {"id": 4, "name_fr": "Freelance", "name_ar": "عمل حر", "icon_slug": "laptop", "parent_id": 1, "is_income": True, "is_essential": False},
    {"id": 5, "name_fr": "Mandat reçu", "name_ar": "حوالة مستلمة", "icon_slug": "mail", "parent_id": 1, "is_income": True, "is_essential": False},

    # ALIMENTATION
    {"id": 10, "name_fr": "Alimentation", "name_ar": "الغذاء", "icon_slug": "shopping-basket", "parent_id": None, "is_essential": True},
    {"id": 11, "name_fr": "Épicerie", "name_ar": "بقالة", "icon_slug": "store", "parent_id": 10, "is_essential": True},
    {"id": 12, "name_fr": "Marché", "name_ar": "سوق", "icon_slug": "shop", "parent_id": 10, "is_essential": True},
    {"id": 13, "name_fr": "Restaurant", "name_ar": "مطعم", "icon_slug": "utensils", "parent_id": 10, "is_essential": False},
    {"id": 14, "name_fr": "Café / Pâtisserie", "name_ar": "مقهى", "icon_slug": "coffee", "parent_id": 10, "is_essential": False},

    # LOGEMENT
    {"id": 20, "name_fr": "Logement", "name_ar": "السكن", "icon_slug": "home", "parent_id": None, "is_essential": True},
    {"id": 21, "name_fr": "Loyer", "name_ar": "الإيجار", "icon_slug": "key", "parent_id": 20, "is_essential": True},
    {"id": 22, "name_fr": "Sonelgaz (Gaz/Élec)", "name_ar": "سونلغاز", "icon_slug": "zap", "parent_id": 20, "is_essential": True},
    {"id": 23, "name_fr": "Eau (ADE)", "name_ar": "الماء", "icon_slug": "droplets", "parent_id": 20, "is_essential": True},
    {"id": 24, "name_fr": "Internet / Téléphone fixe", "name_ar": "الإنترنت", "icon_slug": "wifi", "parent_id": 20, "is_essential": True},

    # TRANSPORT
    {"id": 30, "name_fr": "Transport", "name_ar": "النقل", "icon_slug": "car", "parent_id": None, "is_essential": True},
    {"id": 31, "name_fr": "Taxi / Yassir / Temma", "name_ar": "تاكسي", "icon_slug": "car", "parent_id": 30, "is_essential": False},
    {"id": 32, "name_fr": "Bus / ETUSA", "name_ar": "حافلة", "icon_slug": "bus", "parent_id": 30, "is_essential": True},
    {"id": 33, "name_fr": "Carburant", "name_ar": "الوقود", "icon_slug": "fuel", "parent_id": 30, "is_essential": False},
    {"id": 34, "name_fr": "Train SNTF", "name_ar": "قطار", "icon_slug": "train", "parent_id": 30, "is_essential": False},

    # TÉLÉCOMS
    {"id": 40, "name_fr": "Télécommunications", "name_ar": "اتصالات", "icon_slug": "smartphone", "parent_id": None, "is_essential": True},
    {"id": 41, "name_fr": "Mobilis", "name_ar": "موبيليس", "icon_slug": "phone", "parent_id": 40, "is_essential": True},
    {"id": 42, "name_fr": "Djezzy", "name_ar": "جيزي", "icon_slug": "phone", "parent_id": 40, "is_essential": True},
    {"id": 43, "name_fr": "Ooredoo", "name_ar": "أوريدو", "icon_slug": "phone", "parent_id": 40, "is_essential": True},

    # SANTÉ
    {"id": 50, "name_fr": "Santé", "name_ar": "الصحة", "icon_slug": "heart-pulse", "parent_id": None, "is_essential": True},
    {"id": 51, "name_fr": "Pharmacie", "name_ar": "صيدلية", "icon_slug": "pill", "parent_id": 50, "is_essential": True},
    {"id": 52, "name_fr": "Consultation médicale", "name_ar": "استشارة طبية", "icon_slug": "stethoscope", "parent_id": 50, "is_essential": True},
    {"id": 53, "name_fr": "Clinique / Hôpital", "name_ar": "عيادة", "icon_slug": "hospital", "parent_id": 50, "is_essential": True},

    # ÉDUCATION
    {"id": 60, "name_fr": "Éducation", "name_ar": "التعليم", "icon_slug": "graduation-cap", "parent_id": None, "is_essential": True},
    {"id": 61, "name_fr": "Université / Frais", "name_ar": "جامعة", "icon_slug": "school", "parent_id": 60, "is_essential": True},
    {"id": 62, "name_fr": "Cours particuliers", "name_ar": "دروس خصوصية", "icon_slug": "book-open", "parent_id": 60, "is_essential": False},
    {"id": 63, "name_fr": "Fournitures scolaires", "name_ar": "لوازم مدرسية", "icon_slug": "pencil", "parent_id": 60, "is_essential": False},

    # LOISIRS
    {"id": 70, "name_fr": "Loisirs", "name_ar": "الترفيه", "icon_slug": "gamepad-2", "parent_id": None, "is_essential": False},
    {"id": 71, "name_fr": "Sport / Salle", "name_ar": "رياضة", "icon_slug": "dumbbell", "parent_id": 70, "is_essential": False},
    {"id": 72, "name_fr": "Cinéma / Divertissement", "name_ar": "سينما", "icon_slug": "clapperboard", "parent_id": 70, "is_essential": False},
    {"id": 73, "name_fr": "Vacances / Voyage", "name_ar": "عطلة", "icon_slug": "plane", "parent_id": 70, "is_essential": False},
    {"id": 74, "name_fr": "Shopping / Vêtements", "name_ar": "تسوق", "icon_slug": "shirt", "parent_id": 70, "is_essential": False},

    # TRANSFERTS
    {"id": 80, "name_fr": "Transferts", "name_ar": "التحويلات", "icon_slug": "send", "parent_id": None, "is_essential": False},
    {"id": 81, "name_fr": "Mandat postal", "name_ar": "حوالة بريدية", "icon_slug": "mail", "parent_id": 80, "is_essential": False},
    {"id": 82, "name_fr": "Virement bancaire", "name_ar": "تحويل بنكي", "icon_slug": "arrow-right-left", "parent_id": 80, "is_essential": False},
    {"id": 83, "name_fr": "Baridimob / CCP", "name_ar": "بريدي موب", "icon_slug": "smartphone", "parent_id": 80, "is_essential": False},

    # FÊTES
    {"id": 90, "name_fr": "Fêtes / Occasions", "name_ar": "مناسبات", "icon_slug": "star", "parent_id": None, "is_essential": False},
    {"id": 91, "name_fr": "Aïd al-Adha (Mouton)", "name_ar": "عيد الأضحى", "icon_slug": "star", "parent_id": 90, "is_essential": False},
    {"id": 92, "name_fr": "Aïd el-Fitr / Cadeaux", "name_ar": "عيد الفطر", "icon_slug": "gift", "parent_id": 90, "is_essential": False},
    {"id": 93, "name_fr": "Mariage / Fête", "name_ar": "عرس", "icon_slug": "heart", "parent_id": 90, "is_essential": False},

    # AUTRE
    {"id": 99, "name_fr": "Autre", "name_ar": "أخرى", "icon_slug": "more-horizontal", "parent_id": None, "is_essential": False},
]

def seed_categories(db: Session):
    for cat_data in CATEGORIES:
        existing = db.query(Category).filter(Category.id == cat_data["id"]).first()
        if not existing:
            cat = Category(**cat_data)
            db.add(cat)
    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    seed_categories(db)
    db.close()
    print("Categories seeded successfully.")
