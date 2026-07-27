import shutil
from datetime import date
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from apps.contact.models import ContactInfo
from apps.core.models import HeroSlide, KeyFigure, MinisterMessage, Timeline
from apps.documents.models import Document, DocumentCategory
from apps.news.models import Article, NewsCategory
from apps.structures.models import AttachedBody, Delegation, OrgUnit, Region, TrainingCenter

SOURCE_PDF_DIR = Path("/root/.claude/uploads/c7a73db5-06c7-58e1-9148-9e5a48db3149")


class Command(BaseCommand):
    help = "Seed the MINEFOP database with the ministry's organisational structure, legal texts and sample content."

    def handle(self, *args, **options):
        self.seed_key_figures()
        self.seed_timeline()
        self.seed_minister()
        self.seed_contact_info()
        self.seed_org_units()
        self.seed_attached_bodies()
        self.seed_regions_and_delegations()
        self.seed_training_centers()
        self.seed_documents()
        self.seed_news()
        self.stdout.write(self.style.SUCCESS("MINEFOP seed data created successfully."))

    # ------------------------------------------------------------------
    def seed_key_figures(self):
        if KeyFigure.objects.exists():
            return
        data = [
            ("Régions couvertes", "10", "bi-geo-alt-fill", 1),
            ("Types de centres publics de formation", "6", "bi-building", 2),
            ("Langues officielles", "2", "bi-mortarboard-fill", 3),
            ("Loi cadre de la formation professionnelle", "2018", "bi-award-fill", 4),
        ]
        for label, value, icon, order in data:
            KeyFigure.objects.create(label=label, value=value, icon=icon, order=order)
        self.stdout.write("Key figures created.")

    def seed_timeline(self):
        if Timeline.objects.exists():
            return
        data = [
            ("1976", "Loi n° 76/12 du 8 juillet 1976", "Première organisation de la formation professionnelle rapide au Cameroun.", 1),
            ("2011", "Décret n° 2011/126 du 23 mai 2011", "Organisation antérieure du Ministère de l'Emploi et de la Formation Professionnelle.", 2),
            ("2012", "Décret n° 2012/644 du 28 décembre 2012", "Réorganisation du Ministère de l'Emploi et de la Formation Professionnelle, actuellement en vigueur.", 3),
            ("2018", "Loi n° 2018/010 du 11 juillet 2018", "Loi régissant la formation professionnelle au Cameroun : cadre juridique général et orientations fondamentales.", 4),
            ("2020", "Décret n° 2020/2592/PM du 9 juin 2020", "Modalités de création, d'organisation et de fonctionnement des centres de formation professionnelle et d'apprentissage.", 5),
            ("2023", "Création du CNFFDP", "Décret portant création et organisation du Centre National de Formation des Formateurs et de Développement des Programmes.", 6),
        ]
        for year, title, desc, order in data:
            Timeline.objects.create(year=year, title=title, description=desc, order=order)
        self.stdout.write("Timeline created.")

    def seed_minister(self):
        MinisterMessage.load()

    def seed_contact_info(self):
        ContactInfo.load()

    # ------------------------------------------------------------------
    def seed_org_units(self):
        if OrgUnit.objects.exists():
            return

        def create(name, unit_type, parent=None, head_title="", legal_reference="", order=0, mission=""):
            return OrgUnit.objects.create(
                name=name,
                unit_type=unit_type,
                parent=parent,
                head_title=head_title,
                legal_reference=legal_reference,
                order=order,
                mission=mission,
            )

        minister = create(
            "Cabinet du Ministre", "cabinet", order=1,
            mission="Élaboration et mise en œuvre de la politique du Gouvernement en matière d'emploi, de formation et d'insertion professionnelles.",
            legal_reference="Article 1er",
        )
        create("Secrétariat Particulier", "cellule", parent=minister, head_title="Chef de Secrétariat Particulier", order=1, legal_reference="Article 3")
        create("Conseillers Techniques (02)", "cellule", parent=minister, order=2, legal_reference="Article 4")

        create(
            "Inspection Générale des Services", "inspection", parent=minister,
            head_title="Inspecteur Général des Services", order=3, legal_reference="Article 5",
            mission="Évaluation des performances des services, contrôle interne, lutte contre la corruption.",
        )
        create(
            "Inspection Générale des Formations", "inspection", parent=minister,
            head_title="Inspecteur Général des Formations", order=4, legal_reference="Article 7",
            mission="Orientations pédagogiques et andragogiques, normalisation des dispositifs de formation professionnelle.",
        )

        # Administration Centrale (Article 8)
        sg = create(
            "Secrétariat Général", "direction", parent=minister,
            head_title="Secrétaire Général", order=5, legal_reference="Article 9",
            mission="Coordination de l'action des services centraux et déconcentrés, codification des procédures internes.",
        )
        create("Division des Affaires Juridiques", "division", parent=sg, head_title="Chef de Division", order=1, legal_reference="Article 11")
        create("Cellule de Suivi", "cellule", parent=sg, order=2, legal_reference="Article 14")
        create("Cellule de Communication", "cellule", parent=sg, order=3, legal_reference="Article 15")
        create("Cellule Informatique", "cellule", parent=sg, order=4, legal_reference="Article 16")
        create("Cellule de Traduction", "cellule", parent=sg, order=5, legal_reference="Article 17")
        create("Sous-direction de l'Accueil, du Courrier et de Liaison", "sous_direction", parent=sg, order=6, legal_reference="Article 18")
        create("Sous-direction de la Documentation et des Archives", "sous_direction", parent=sg, order=7, legal_reference="Article 22")

        promotion_emploi = create(
            "Division de la Promotion de l'Emploi", "division", parent=minister,
            head_title="Chef de Division", order=6, legal_reference="Article 25",
            mission="Élaboration et mise en œuvre de la politique de l'emploi, promotion de l'auto-emploi, études sur le marché de l'emploi.",
        )
        create("Cellule de la Planification et du Développement de l'Emploi", "cellule", parent=promotion_emploi, order=1, legal_reference="Article 26")
        create("Cellule de Lutte contre le Chômage", "cellule", parent=promotion_emploi, order=2, legal_reference="Article 27")

        regulation_mo = create(
            "Direction de la Régulation de la Main-d'œuvre", "direction", parent=minister,
            head_title="Directeur", order=7, legal_reference="Article 28",
            mission="Placement et protection de la main-d'œuvre, visa des contrats de travail, agrément des organismes de placement.",
        )
        create("Sous-direction de la Réglementation et de la Planification de la Main-d'œuvre", "sous_direction", parent=regulation_mo, order=1, legal_reference="Article 29")
        create("Sous-direction de l'Insertion et des Agréments", "sous_direction", parent=regulation_mo, order=2, legal_reference="Article 32")

        formation_orientation = create(
            "Direction de la Formation et de l'Orientation Professionnelles", "direction", parent=minister,
            head_title="Directeur", order=8, legal_reference="Article 36",
            mission="Politique de formation et d'orientation professionnelle, agrément des structures privées, organisation des examens.",
        )
        create("Sous-direction de la Gestion des Structures de Formation", "sous_direction", parent=formation_orientation, order=1, legal_reference="Article 37")
        create("Sous-direction des Examens, des Concours et de la Certification", "sous_direction", parent=formation_orientation, order=2, legal_reference="Article 40")
        create("Sous-direction de l'Orientation Professionnelle", "sous_direction", parent=formation_orientation, order=3, legal_reference="Article 43")

        etudes_cooperation = create(
            "Division des Études, de la Prospective et de la Coopération", "division", parent=minister,
            head_title="Chef de Division", order=9, legal_reference="Article 46",
            mission="Études et statistiques sur l'emploi et la formation, coopération internationale, banque de projets.",
        )
        create("Cellule des Études, de la Prospective et des Statistiques", "cellule", parent=etudes_cooperation, order=1, legal_reference="Article 47")
        create("Cellule de la Coopération", "cellule", parent=etudes_cooperation, order=2, legal_reference="Article 48")

        affaires_generales = create(
            "Direction des Affaires Générales", "direction", parent=minister,
            head_title="Directeur", order=10, legal_reference="Article 49",
            mission="Gestion des ressources humaines, budget, infrastructures et équipements du Ministère.",
        )
        create("Cellule de Gestion du Projet SIGIPES", "cellule", parent=affaires_generales, order=1, legal_reference="Article 50")
        create("Sous-direction du Personnel, de la Solde et des Pensions", "sous_direction", parent=affaires_generales, order=2, legal_reference="Article 51")
        create("Sous-direction du Budget", "sous_direction", parent=affaires_generales, order=3, legal_reference="Article 55")
        create("Sous-direction des Infrastructures, des Équipements et de la Maintenance", "sous_direction", parent=affaires_generales, order=4, legal_reference="Article 58")

        self.stdout.write("Organisational chart created.")

    def seed_attached_bodies(self):
        if AttachedBody.objects.exists():
            return
        data = [
            ("Observatoire National de l'Emploi et de la Formation Professionnelle", "ONEFOP",
             "Organisme chargé de la production de statistiques et d'études sur l'emploi et la formation professionnelle.", 1),
            ("Projet Intégré d'Appui aux Acteurs du Secteur Informel", "PIAASI",
             "Projet d'appui à la structuration et à la formation des acteurs du secteur informel.", 2),
            ("Centres d'Organisation Scolaire, Universitaire et Professionnelle", "COSUP",
             "Structures d'information et d'orientation scolaire, universitaire et professionnelle.", 3),
        ]
        for name, acronym, desc, order in data:
            AttachedBody.objects.create(name=name, acronym=acronym, description=desc, order=order)
        self.stdout.write("Attached bodies created.")

    def seed_regions_and_delegations(self):
        regions_data = [
            ("Adamaoua", "Ngaoundéré"),
            ("Centre", "Yaoundé"),
            ("Est", "Bertoua"),
            ("Extrême-Nord", "Maroua"),
            ("Littoral", "Douala"),
            ("Nord", "Garoua"),
            ("Nord-Ouest", "Bamenda"),
            ("Ouest", "Bafoussam"),
            ("Sud", "Ebolowa"),
            ("Sud-Ouest", "Buea"),
        ]
        regions = {}
        for name, capital in regions_data:
            region, _created = Region.objects.get_or_create(name=name, defaults={"capital": capital})
            regions[name] = region

        if not Delegation.objects.exists():
            for name, region in regions.items():
                Delegation.objects.create(
                    level=Delegation.Level.REGIONAL,
                    region=region,
                    town=region.capital,
                )
            self.stdout.write("Regions and regional delegations created.")

    def seed_training_centers(self):
        if TrainingCenter.objects.exists():
            return
        regions = {r.name: r for r in Region.objects.all()}
        data = [
            ("CFPE de Sangmélima", TrainingCenter.CenterType.CFPE, "Sud", "Bâtiment, Travaux Publics, Électrotechnique"),
            ("CFPE de Bafang", TrainingCenter.CenterType.CFPE, "Ouest", "Mécanique Automobile, Froid et Climatisation"),
            ("CSFP de Douala (BTP)", TrainingCenter.CenterType.CSFP, "Littoral", "Bâtiment et Travaux Publics"),
            ("CSFP de Kribi (Métiers Portuaires)", TrainingCenter.CenterType.CSFP, "Sud", "Logistique, Métiers Portuaires"),
            ("CFM de Bamenda", TrainingCenter.CenterType.CFM, "Nord-Ouest", "Menuiserie, Couture, Coiffure"),
            ("CFM de Maroua", TrainingCenter.CenterType.CFM, "Extrême-Nord", "Agro-pastoral, Artisanat"),
            ("CAP de Ngaoundéré", TrainingCenter.CenterType.CAP, "Adamaoua", "Élevage, Cuir et Peaux"),
            ("CAP d'Ebolowa", TrainingCenter.CenterType.CAP, "Sud", "Agriculture, Transformation Agroalimentaire"),
            ("CPFPR de Garoua", TrainingCenter.CenterType.CPFPR, "Nord", "Informatique, Secrétariat Bureautique"),
            ("CPFPR de Bertoua", TrainingCenter.CenterType.CPFPR, "Est", "Électricité Bâtiment, Plomberie"),
            ("SAR/SM de Yaoundé", TrainingCenter.CenterType.SARSM, "Centre", "Coupe-Couture, Économie Familiale"),
            ("Centre National de Formation des Formateurs et de Développement des Programmes", TrainingCenter.CenterType.CNFFDP, "Centre", "Ingénierie de la formation, Formation de formateurs"),
        ]
        for name, ctype, region_name, specialties in data:
            TrainingCenter.objects.create(
                name=name,
                center_type=ctype,
                region=regions.get(region_name),
                town=regions[region_name].capital if region_name in regions else "",
                is_public=True,
                specialties=specialties,
                description=(
                    "Structure publique de formation professionnelle placée sous la tutelle du "
                    "Ministère de l'Emploi et de la Formation Professionnelle."
                ),
            )
        self.stdout.write(
            self.style.WARNING(
                "Sample training centers created (illustrative — replace with the ministry's authoritative registry)."
            )
        )

    # ------------------------------------------------------------------
    def seed_documents(self):
        if Document.objects.exists():
            return

        categories = {}
        for name in ["Lois", "Décrets", "Arrêtés"]:
            cat, _created = DocumentCategory.objects.get_or_create(
                name=name, defaults={"slug": name.lower().replace(" ", "-").replace("é", "e")}
            )
            categories[name] = cat

        documents = [
            (
                "Décret n° 2012/644 du 28 décembre 2012 portant organisation du Ministère de l'Emploi et de la Formation Professionnelle",
                categories["Décrets"],
                "Décret n° 2012/644 du 28/12/2012",
                date(2012, 12, 28),
                "e26900d9-DECRET_2012_ORGANISATION_DU_MINISTERE_DE_LEMPLOI__260726_114606.pdf",
            ),
            (
                "Loi n° 2018/010 du 11 juillet 2018 régissant la formation professionnelle au Cameroun",
                categories["Lois"],
                "Loi n° 2018/010 du 11/07/2018",
                date(2018, 7, 11),
                "cc7835c2-LOI_SUR_LA_FORMATION_PROFESSIONNELLE_AU_CAMEROUN_260726_114636.pdf",
            ),
            (
                "Décret n° 2020/2592/PM du 9 juin 2020 fixant les modalités de création, d'organisation et de fonctionnement des centres de formation professionnelle et d'apprentissage",
                categories["Décrets"],
                "Décret n° 2020/2592/PM du 09/06/2020",
                date(2020, 6, 9),
                "bbc65b8a-5120620Decretdu19juin2020_Centresdeformat_260726_120146.pdf",
            ),
            (
                "Décret n° 2023 portant création et organisation du Centre National de Formation des Formateurs et de Développement des Programmes (CNFFDP)",
                categories["Décrets"],
                "Décret n° 2023",
                date(2023, 5, 4),
                "3af6feaf-721ef49c1081eaebbbbd9be87a80573b_260726_120323.pdf",
            ),
        ]

        for title, category, reference, published_date, filename in documents:
            source_path = SOURCE_PDF_DIR / filename
            doc = Document(
                title=title,
                category=category,
                reference_number=reference,
                published_date=published_date,
                description="Texte officiel régissant l'organisation et le fonctionnement du secteur de l'emploi et de la formation professionnelle au Cameroun.",
            )
            if source_path.exists():
                with source_path.open("rb") as f:
                    doc.file.save(filename.split("_260726", 1)[0] + ".pdf", File(f), save=False)
            doc.save()

        self.stdout.write("Legal documents created.")

    def seed_news(self):
        if Article.objects.exists():
            return

        categories = {}
        for name in ["Communiqué", "Actualité", "Événement"]:
            cat, _created = NewsCategory.objects.get_or_create(
                name=name, defaults={"slug": name.lower().replace("é", "e")}
            )
            categories[name] = cat

        articles = [
            (
                "Lancement de la campagne nationale d'orientation professionnelle",
                categories["Actualité"],
                "Le Ministère lance une campagne d'information à destination des jeunes bacheliers sur les filières de formation professionnelle porteuses d'emploi.",
                "Dans le cadre de sa politique d'orientation professionnelle, le Ministère de l'Emploi et de la Formation Professionnelle a lancé une campagne nationale d'information à destination des jeunes bacheliers et des chercheurs d'emploi. Cette campagne vise à mieux faire connaître les filières de formation professionnelle porteuses d'emploi, en particulier dans le bâtiment, l'agro-industrie et les métiers du numérique.\n\nDes sessions d'information seront organisées dans les dix régions du pays, en collaboration avec les délégations régionales et les centres de formation professionnelle publics.",
            ),
            (
                "Journée mondiale des compétences des jeunes",
                categories["Événement"],
                "Le Ministère célèbre la Journée mondiale des compétences des jeunes autour du thème de l'employabilité durable.",
                "À l'occasion de la Journée mondiale des compétences des jeunes, le Ministère de l'Emploi et de la Formation Professionnelle a organisé une série d'activités dans plusieurs centres de formation professionnelle du pays, mettant en avant les parcours réussis d'anciens apprenants insérés dans la vie active.",
            ),
            (
                "Signature d'une convention de partenariat avec le secteur privé",
                categories["Communiqué"],
                "Une convention-cadre a été signée afin de renforcer l'adéquation entre l'offre de formation et les besoins des entreprises.",
                "Le Ministère de l'Emploi et de la Formation Professionnelle a signé une convention-cadre avec plusieurs organisations professionnelles afin de renforcer la formation en alternance et faciliter l'insertion des apprenants dans les entreprises partenaires.",
            ),
            (
                "Ouverture de la session des examens de fin de formation professionnelle",
                categories["Communiqué"],
                "Le calendrier des examens de fin de formation professionnelle a été publié pour la présente session.",
                "La Direction de la Formation et de l'Orientation Professionnelles informe l'ensemble des centres de formation publics et privés agréés du calendrier des examens de fin de formation professionnelle pour la session en cours. Les candidats sont invités à se rapprocher de leurs centres respectifs pour les modalités d'inscription.",
            ),
        ]

        for title, category, excerpt, body in articles:
            Article.objects.create(
                title=title,
                slug=title.lower()
                .replace("é", "e").replace("è", "e").replace("ê", "e")
                .replace("'", "-").replace(",", "").replace(" ", "-")[:250],
                category=category,
                excerpt=excerpt,
                body=body,
            )
        self.stdout.write(
            self.style.WARNING(
                "Sample news articles created (illustrative content — replace with real releases via the admin)."
            )
        )
