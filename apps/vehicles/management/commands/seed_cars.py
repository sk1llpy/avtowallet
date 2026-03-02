# apps/vehicles/management/commands/seed_cars.py
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.vehicles.models import Brand, CarModel


# Shu yerga o'zingizdagi dictni qo'ying (ALL_CARS)
ALL_CARS = {
    "Chevrolet": [
        "Spark","Matiz","Nexia","Nexia 2","Nexia 3","Cobalt","Lacetti","Gentra",
        "Malibu","Malibu 2","Epica","Orlando","Tracker","Tracker 2","Equinox",
        "Captiva","Traverse","Tahoe","Suburban","Camaro","Corvette","Aveo",
        "Cruze","Impala","Volt","Bolt","Blazer","Trailblazer","Damas","Labo"
    ],
    "Daewoo": ["Matiz","Nexia","Nexia 2","Tico","Damas","Labo","Leganza","Espero","Racer"],
    "Kia": ["Picanto","Rio","Rio X","Cerato","K3","K5","Optima","Stinger","Soul","Ceed","Seltos","Sportage","Sorento","Telluride","Carnival","Mohave","K8","K9","EV6","EV9"],
    "Hyundai": ["Atos","Accent","Solaris","Elantra","Avante","Sonata","Azera","Grandeur","Genesis","Coupe","Veloster","i10","i20","i30","Creta","Venue","Tucson","Santa Fe","Palisade","Terracan","Staria","H-1","Porter","Kona","Ioniq","Ioniq 5","Ioniq 6"],
    "Toyota": ["Yaris","Corolla","Corolla Cross","Camry","Avalon","Crown","Prius","Prius C","Prius V","Supra","86","GR86","RAV4","Highlander","Venza","C-HR","Land Cruiser 70","Land Cruiser 100","Land Cruiser 200","Land Cruiser 300","Prado","Fortuner","Hilux","Tacoma","Tundra","Sequoia"],
    "Lexus": ["IS","ES","GS","LS","UX","NX","RX","GX","LX","RC","LC","CT"],
    "BMW": ["1 Series","2 Series","3 Series","4 Series","5 Series","6 Series","7 Series","8 Series","X1","X2","X3","X4","X5","X6","X7","Z3","Z4","i3","i4","i7","iX","M2","M3","M4","M5","M8"],
    "Mercedes-Benz": ["A-Class","B-Class","C-Class","E-Class","S-Class","CLA","CLS","GLA","GLB","GLC","GLE","GLS","G-Class","V-Class","Vito","Sprinter","EQC","EQE","EQS","SL","SLC"],
    "Audi": ["A1","A3","A4","A5","A6","A7","A8","Q2","Q3","Q5","Q7","Q8","TT","R8","RS3","RS4","RS5","RS6","RS7","e-tron"],
    "Volkswagen": ["Polo","Jetta","Passat","Arteon","Golf","Tiguan","Touareg","Teramont","Atlas","Caddy","Transporter","Multivan","Amarok","ID.4","ID.6"],
    "Nissan": ["Micra","Sunny","Almera","Sentra","Altima","Maxima","Teana","Qashqai","X-Trail","Murano","Pathfinder","Patrol","Armada","Navara","Titan","Leaf","Ariya"],
    "Honda": ["Fit","City","Civic","Accord","Insight","Prelude","CR-V","HR-V","ZR-V","Pilot","Passport","Ridgeline"],
    "Mazda": ["Mazda 2","Mazda 3","Mazda 6","CX-3","CX-30","CX-5","CX-7","CX-9","MX-5"],
    "BYD": ["F3","Qin","Qin Plus","Han","Tang","Song","Song Plus","Song Pro","Yuan","Yuan Plus","Dolphin","Seal","Destroyer 05","E2","E5","Atto 3"],
    "Chery": ["QQ","Arrizo 3","Arrizo 5","Arrizo 6","Arrizo 8","Tiggo 2","Tiggo 3","Tiggo 4","Tiggo 5","Tiggo 7","Tiggo 8"],
    "Geely": ["Emgrand","Emgrand GT","Emgrand X7","Coolray","Atlas","Monjaro","Tugella","Okavango","Preface","Geometry A","Geometry C"],
    "Haval": ["H2","H6","H9","F7","F7x","Jolion","Dargo"],
    "Lada": ["2101","2103","2106","2107","2109","2110","2114","2115","Kalina","Granta","Vesta","XRAY","Largus","Niva","Niva Travel"],
    "Ford": ["Fiesta","Focus","Mondeo","Fusion","Taurus","EcoSport","Kuga","Escape","Edge","Explorer","Expedition","Ranger","F-150","Mustang","Mach-E"],
}


class Command(BaseCommand):
    help = "Brendlar va modellarning seed'i (ALL_CARS dict'dan)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Oldin CarModel va Brand'larni o‘chirib, keyin seed qiladi (DIQQAT!)."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        clear = options["clear"]

        if clear:
            self.stdout.write(self.style.WARNING("CLEAR mode: CarModel va Brand tozalanmoqda..."))
            CarModel.objects.all().delete()
            Brand.objects.all().delete()

        created_brands = 0
        created_models = 0
        existing_models = 0

        for brand_name, models in ALL_CARS.items():
            brand_name = (brand_name or "").strip()
            if not brand_name:
                continue

            brand, brand_created = Brand.objects.get_or_create(name=brand_name)
            if brand_created:
                created_brands += 1

            # Dedup: bir brend ichida bir xil model bo‘lmasin
            unique_models = []
            seen = set()
            for m in models:
                m = (m or "").strip()
                if not m:
                    continue
                key = m.lower()
                if key in seen:
                    continue
                seen.add(key)
                unique_models.append(m)

            for model_name in unique_models:
                obj, m_created = CarModel.objects.get_or_create(brand=brand, name=model_name)
                if m_created:
                    created_models += 1
                else:
                    existing_models += 1

        self.stdout.write(self.style.SUCCESS("✅ Seed tugadi!"))
        self.stdout.write(f"Yangi brendlar: {created_brands}")
        self.stdout.write(f"Yangi modellar: {created_models}")
        self.stdout.write(f"Oldindan bor modellar: {existing_models}")