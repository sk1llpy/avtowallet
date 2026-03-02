from django.db import models

class CurtainTypeChoices(models.TextChoices):
    COMBO_BLINDS = "combo_blinds", "Kombo"
    PLEATED_BLINDS = "pleated_blinds", "Plisse"
    DIKEY = "dikey", "Dikey"
    TULLE_CURTAIN = "tulle_curtain", "Tyul"
    ROLLO = "rollo", "Rollo"
    ROLLO_SHTOR = "rollo_shtor", "Rollo-shtor"


class ClientTypeChoices(models.TextChoices):
    CLIENT = "client", "Klient"
    DEALER = "dealer", "Diller"


class MaterialTypeChoices(models.TextChoices):
    ROLL_NEW = "roll_new", "Rulon (yangi)"
    ROLL_OPENED = "roll_opened", "Rulon (ishlatilgan)"
    REMAINDER = "remainder", "Mayda rulon"


class ManufacturerTypeChoices(models.TextChoices):
    RATEX = "ratex", "Ratex"
    NEWMOON = "newmoon", "NewMoon"
    MOONRISE = "moonrise", "MoonRise"
    SAN_DECOR = "san_decor", "San Decor"
    

class StorePurchaseTypeChoices(models.TextChoices):
    CASH = "cash", "Naxd"
    DEBT = "debt", "Qarz"


class TransactionTypeChoices(models.TextChoices):
    INCOME = "income", "Kirim (+)"
    EXPENDITURE = "expenditure", "Chiqim (-)"


class RegionTypeChoices(models.TextChoices):
    TASHKENT_CITY = "tashkent_city", "Toshkent (shaxar)"
    TASHKENT_REGION = "tashkent_region", "Toshkent viloyati"
    SIRDARYO = "sirdaryo", "Sirdaryo"
    JIZZAKH = "jizzakh", "Jizzax"
    SAMARKAND = "samarkand", "Samarqand"
    FERGANA = "fergana", "Farg'ona"
    NAMANGAN = "namangan", "Namangan"
    ANDIJAN = "andijan", "Andijon"
    QASHQADARYO = "qashqadaryo", "Qashqadaryo"
    SURKHANDARYO = "surkhandaryo", "Surxandaryo"
    BUKHARA = "bukhara", "Buxoro"
    NAVOI = "navoi", "Navoiy"
    KHORAZM = "khorazm", "Xorazm"
    QORAQALPOGISTAN = "qoraqalpogiston", "Qoraqalpog'istion Respublikasi"


class PaymentTypeChoices(models.TextChoices):
    CASH = "cash", "Naxd"
    CARD = "card", "Karta"
    THROUGH_THE_COMPANY = "through_the_company", "Firma orqali"


class StandartLabrikentTypeChoices(models.TextChoices):
    STANDART = "standart", "Standart"
    LABRIKENT = "labrikent", "Labrikent"
    ARKA = "arka", "Arka"
    LABRIKENT_ARKA = "labrikent_arka", "Labrikent / Arka"


# ================================
#   ACCESSORY TYPE CHOICES
# ================================
class AccessoryTypeChoices(models.TextChoices):
    # -------- COMBO --------
    COMBO_EAVES = "combo_eaves", "Karniz Kombo"
    COMBO_BRACKET = "combo_bracket", "Kronshteyn Kombo"
    COMBO_CLIP = "combo_clip", "Klipsa Kombo"
    COMBO_PLANK = "combo_plank", "Planla Kombo"
    COMBO_HANDLE = "combo_handle", "Tutqich Kombo"
    COMBO_TAPE = "combo_tape", "Tasma Kombo"
    COMBO_MECHANISM = "combo_mechanism", "Mexanizm Kombo"

    # -------- PLEATED --------
    PLEATED_YARN = "pleated_yarn", "Ip Plisse"
    PLEATED_TAPE = "pleated_tape", "Tasma Plisse"
    PLEATED_MECHANISM = "pleated_mechanism", "Mexanizm Plisse"
    PLEATED_EAVES = "pleated_eaves", "Karniz Plisse"

    # -------- DIKEY --------
    DIKEY_YARN = "dikey_yarn", "Ip Dikey"
    DIKEY_RUNNER = "dikey_runner", "Begunok Dikey"
    DIKEY_MECHANISM = "dikey_mechanism", "Mexanizm Dikey"
    DIKEY_EAVES = "dikey_eaves", "Karniz Dikey"
    DIKEY_BRACKET = "dikey_bracket", "Kronshteyn Dikey"
    DIKEY_FURUZILIN = "dikey_furuzilin", "Furuzilin Dikey"
    DIKEY_HANGER = "dikey_hanger", "Veshalka Dikey"
    DIKEY_GLUE = "dikey_glue", "Kley Dikey"
    DIKEY_CHAIN = "dikey_chain", "Sepochka Dikey"

    # -------- TULLE --------
    TULLE_EAVES = "tulle_eaves", "Karniz Tyul"
    TULLE_LOAD = "tulle_load", "Gruz Tyul"
    TULLE_MECHANISM = "tulle_mechanism", "Mexanizm Tyul"
    TULLE_LOADCOVER = "tulle_loadcover", "Gruz qopqoq Tyul"

    # -------- ROLLO-SHTOR --------
    ROLLOSHTOR_MECHANISM = "rolloshtor_mechanism", "Mexanizm Rollo-shtor"
    TULLE_TUBE = "tulle_tube", "Truba"


class HeightTypeChoices(models.TextChoices):
    METER = "meter", "Metr"
    UNIT = "unit", "Dona (faqat Plisseda)"


# ================================
#   COMBO SUB-CHOICES
# ================================
class ComboEavesTypeChoices(models.TextChoices):
    AL = "combo_eaves_al", "Alyumin"
    PL = "combo_eaves_pl", "Пластик"
    WITHOUT_PLANK = "combo_eaves_without_plank", "Plankasiz"

    PLANK_BROWN = "combo_eaves_plank_brown", "Planka (Jigarrang)"
    PLANK_WHITE = "combo_eaves_plank_white", "Planka (Oq)"
    PLANK_GRAY = "combo_eaves_plank_gray", "Planka (Seriy)"
    PLANK_WET = "combo_eaves_plank_wet", "Planka (Mokriy asfalt)"


class ComboMechanismTypeChoices(models.TextChoices):
    MECHANISM_1_2 = "combo_mechanism_1_2", "Mexanizm 1.2"
    MECHANISM_1_5 = "combo_mechanism_1_5", "Mexanizm 1.5"
    MECHANISM_1_8 = "combo_mechanism_1_8", "Mexanizm 1.8"
    MECHANISM_2 = "combo_mechanism_2", "Mexanizm 2"
    MECHANISM_2_5 = "combo_mechanism_2_5", "Mexanizm 2.5"
    MECHANISM_3 = "combo_mechanism_3", "Mexanizm 3"


class ComboBracketTypeChoices(models.TextChoices):
    BRACKET = "combo_bracket", "Kronshteyn"
    CLIP = "combo_clip", "Klipsa"


# ================================
#   PLEATED SUB-CHOICES
# ================================
class PleatedMechanismTypeChoices(models.TextChoices):
    MECHANISM_BLACK = "pleated_mechanism_black", "Qora Mexanizm"
    MECHANISM_BROWN = "pleated_mechanism_brown", "Jigarrang Mexanizm"
    MECHANISM_WET = "pleated_mechanism_wet", "Mokriy asfalt Mexanizm"
    MECHANISM_GRAY = "pleated_mechanism_gray", "Seriy Mexanizm"
    MECHANISM_WHITE = "pleated_mechanism_white", "Oq Mexanizm"
    MECHANISM_BRONZE = "pleated_mechanism_bronze", "Bronza Mexanizm"


class PleatedEavesTypeChoices(models.TextChoices):
    PLANK_BLACK = "pleated_eaves_plank_black", "Planka (Qora)"
    PLANK_BROWN = "pleated_eaves_plank_brown", "Planka (Jigarrang)"
    PLANK_WET = "pleated_eaves_plank_wet", "Planka (Mokriy asfalt)"
    PLANK_GRAY = "pleated_eaves_plank_gray", "Planka (Seriy)"
    PLANK_WHITE = "pleated_eaves_plank_white", "Planka (Oq)"
    PLANK_BRONZE = "pleated_eaves_plank_bronze", "Planka (Bronza)"

    WITHOUT_PLANK_BLACK = "pleated_eaves_without_plank_black", "Plankasiz (Qora)"
    WITHOUT_PLANK_BROWN = "pleated_eaves_without_plank_brown", "Plankasiz (Jigarrang)"
    WITHOUT_PLANK_WET = "pleated_eaves_without_plank_wet", "Plankasiz (Mokriy asfalt)"
    WITHOUT_PLANK_GRAY = "pleated_eaves_without_plank_gray", "Plankasiz (Seriy)"
    WITHOUT_PLANK_WHITE = "pleated_eaves_without_plank_white", "Plankasiz (Oq)"
    WITHOUT_PLANK_BRONZE = "pleated_eaves_without_plank_bronze", "Plankasiz (Bronza)"


# ================================
#   DIKEY SUB-CHOICES
# ================================
class DikeyEavesTypeChoices(models.TextChoices):
    AL = "dikey_eaves_al", "Alyumin"
    PL = "dikey_eaves_pl", "Plastik"


# ================================
#   TULLE SUB-CHOICES
# ================================
class TulleEavesTypeChoices(models.TextChoices):
    AL = "combo_eaves_al", "Алюминий"
    PL = "combo_eaves_pl", "Plastik"
    
class AllAccessoryTypeChoices(models.TextChoices):
    # ======================
    #        COMBO
    # ======================
    COMBO_TAPE = "combo_tape", "Tasma kombo"
    COMBO_HANDLE = "combo_handle", "Tutqich kombo"

    COMBO_EAVES_AL = "combo_eaves_al", "Alyumin karniz kombo"
    COMBO_EAVES_PL = "combo_eaves_pl", "Plastik karniz kombo"
    COMBO_EAVES_WITHOUT_PLANK = "combo_eaves_without_plank", "Bez planka karniz kombo"

    COMBO_EAVES_PLANK_BROWN = "combo_eaves_plank_brown", "Plankali jigarrang karniz kombo"
    COMBO_EAVES_PLANK_WHITE = "combo_eaves_plank_white", "Plankali oq karniz kombo"
    COMBO_EAVES_PLANK_GRAY = "combo_eaves_plank_gray", "Plankali seriy karniz kombo"
    COMBO_EAVES_PLANK_WET = "combo_eaves_plank_wet", "Plankali mokriy asfalt karniz kombo"

    COMBO_MECHANISM_1_2 = "combo_mechanism_1_2", "Mexanizm 1.2"
    COMBO_MECHANISM_1_5 = "combo_mechanism_1_5", "Mexanizm 1.5"
    COMBO_MECHANISM_1_8 = "combo_mechanism_1_8", "Mexanizm 1.8"
    COMBO_MECHANISM_2 = "combo_mechanism_2", "Mexanizm 2.0"
    COMBO_MECHANISM_2_5 = "combo_mechanism_2_5", "Mexanizm 2.5"
    COMBO_MECHANISM_3 = "combo_mechanism_3", "Mexanizm 3.0"

    COMBO_BRACKET = "combo_bracket", "Kronshteyn Kombo"
    COMBO_CLIP = "combo_clip", "Klipsa Kombo"
    COMBO_PLANK = "combo_plank", "Planka Kombo"

    # ======================
    #        PLEATED
    # ======================
    PLEATED_YARN = "pleated_yarn", "Ip Plisse"
    PLEATED_TAPE = "pleated_tape", "Tasma Plisse"

    PLEATED_MECHANISM_BLACK = "pleated_mechanism_black", "Mexanizm qora Plisse"
    PLEATED_MECHANISM_BROWN = "pleated_mechanism_brown", "Mexanizm jigarrang Plisse"
    PLEATED_MECHANISM_WET = "pleated_mechanism_wet", "Mexanizm mokriy asfalt Plisse"
    PLEATED_MECHANISM_GRAY = "pleated_mechanism_gray", "Mexanizm seriy Plisse"
    PLEATED_MECHANISM_WHITE = "pleated_mechanism_white", "Mexanizm oq Plisse"
    PLEATED_MECHANISM_BRONZE = "pleated_mechanism_bronze", "Mexanizm bronza Plisse"

    PLEATED_EAVES_PLANK_BLACK = "pleated_eaves_plank_black", "Planka Karniz qora Plisse"
    PLEATED_EAVES_PLANK_BROWN = "pleated_eaves_plank_brown", "Planka Karniz jigarrang Plisse"
    PLEATED_EAVES_PLANK_WET = "pleated_eaves_plank_wet", "Planka Karniz mokriy asfalt Plisse"
    PLEATED_EAVES_PLANK_GRAY = "pleated_eaves_plank_gray", "Planka Karniz seriy Plisse"
    PLEATED_EAVES_PLANK_WHITE = "pleated_eaves_plank_white", "Planka Karniz oq Plisse"
    PLEATED_EAVES_PLANK_BRONZE = "pleated_eaves_plank_bronze", "Planka Karniz bronza Plisse"

    PLEATED_EAVES_WITHOUT_PLANK_BLACK = "pleated_eaves_without_plank_black", "Karniz Plankasiz qora Plisse"
    PLEATED_EAVES_WITHOUT_PLANK_BROWN = "pleated_eaves_without_plank_brown", "Karniz Plankasiz jigarrang Plisse"
    PLEATED_EAVES_WITHOUT_PLANK_WET = "pleated_eaves_without_plank_wet", "Karniz Plankasiz mokriy asfalt Plisse"
    PLEATED_EAVES_WITHOUT_PLANK_GRAY = "pleated_eaves_without_plank_gray", "Karniz Plankasiz seriy Plisse"
    PLEATED_EAVES_WITHOUT_PLANK_WHITE = "pleated_eaves_without_plank_white", "Karniz Plankasiz oq Plisse"
    PLEATED_EAVES_WITHOUT_PLANK_BRONZE = "pleated_eaves_without_plank_bronze", "Karniz Plankasiz bronza Plisse"

    # ======================
    #         DIKEY
    # ======================
    DIKEY_YARN = "dikey_yarn", "Ip Dikey"
    DIKEY_BEGUNOK = "dikey_begunok", "Begunok Dikey"
    DIKEY_MECHANISM = "dikey_mechanism", "Mexanizm Dikey"

    DIKEY_EAVES_AL = "dikey_eaves_al", "Alyumin Karniz Dikey"
    DIKEY_EAVES_PL = "dikey_eaves_pl", "Plastik Karniz Dikey"

    DIKEY_BRACKET = "dikey_bracket", "Kronshteyn Dikey"
    DIKEY_FURUZILIN = "dikey_furuzilin", "Furuzilin Dikey"
    DIKEY_HANGER = "dikey_hanger", "Veshalka Dikey"
    DIKEY_GLUE = "dikey_glue", "Kley Dikey"
    DIKEY_CHAIN = "dikey_chain", "Sepochka Dikey"

    # ======================
    #         TULLE
    # ======================
    TULLE_LOAD = "tulle_load", "Gruz Tyul"
    TULLE_MECHANISM = "tulle_mechanism", "Mexanizm Tyul"
    TULLE_LOADCOVER = "tulle_loadcover", "Gruz qopqoq"
    TULLE_TUBE = "tulle_tube", "Truba"

    # ======================
    #     ROLLO-SHTOR
    # ======================
    ROLLO_SHTOR_MECHANISM = "rolloshtor_mechanism", "Mexanizm Rollo-shtor"


class PrepareOrderStatusTypeChoices(models.TextChoices):
    IN_PROCCESS = "in_proccess", "Jarayonda"
    DONE = "done", "Tayyor"
    