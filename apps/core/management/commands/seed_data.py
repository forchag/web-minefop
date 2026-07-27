from datetime import date, datetime
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

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
            ("Diplômés suivis via Inserjeune", "15 000+", "bi-graph-up-arrow", 3),
            ("Budget 2026 Emploi & Formation Pro.", "33,4 Mds FCFA", "bi-cash-coin", 4),
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
            ("2023", "Déploiement d'Inserjeune", "Mise en service de la plateforme numérique de suivi de l'insertion professionnelle des diplômés de la formation professionnelle.", 7),
            ("2025", "Lancement du programme JEME", "« Un Jeune, un Métier, un Emploi », doté de 17,72 milliards de FCFA, lancé le 19 novembre 2025 au CNFFDP en application des orientations du Chef de l'État.", 8),
        ]
        for year, title, desc, order in data:
            Timeline.objects.create(year=year, title=title, description=desc, order=order)
        self.stdout.write("Timeline created.")

    def seed_minister(self):
        minister = MinisterMessage.load()
        if minister.message:
            return
        minister.full_name = "Mounouna Foutsou"
        minister.title = "Ministre de l'Emploi et de la Formation Professionnelle (par intérim)"
        minister.message = (
            "Chères concitoyennes, chers concitoyens,\n\n"
            "Ingénieur de formation et ancien Secrétaire d'État à l'Enseignement Secondaire, "
            "j'assure depuis juin 2025 l'intérim à la tête de ce Département ministériel, en "
            "cumul avec le Ministère de la Jeunesse et de l'Éducation Civique. C'est une mission "
            "que j'exerce avec le sens du devoir, au service de l'employabilité de la jeunesse "
            "camerounaise.\n\n"
            "Conformément aux orientations du Chef de l'État, Son Excellence Paul BIYA, exprimées "
            "lors de son discours d'investiture du 6 novembre 2025 selon lesquelles « aucun jeune "
            "Camerounais ne doit être condamné à l'inactivité », le Ministère a lancé le 19 novembre "
            "2025 le programme « Un Jeune, un Métier, un Emploi » (JEME), doté d'une enveloppe de "
            "17,72 milliards de FCFA, afin de former, insérer et autonomiser durablement les jeunes "
            "des zones rurales, péri-urbaines et urbaines.\n\n"
            "Cette ambition s'appuie sur la modernisation continue de notre dispositif : la "
            "plateforme numérique Inserjeune, qui assure le suivi de plus de 15 000 diplômés de la "
            "formation professionnelle, le projet D-CLIC mené avec l'Organisation Internationale de "
            "la Francophonie pour former les jeunes aux métiers du numérique, et le renforcement des "
            "capacités pédagogiques de nos formateurs à travers le Centre National de Formation des "
            "Formateurs et de Développement des Programmes (CNFFDP).\n\n"
            "Ce site se veut un espace d'information transparent sur nos missions, notre "
            "organisation, nos centres de formation et les textes qui encadrent notre action. "
            "Je vous souhaite une excellente navigation."
        )
        minister.save()
        self.stdout.write("Minister's message created.")

    def seed_contact_info(self):
        info = ContactInfo.load()
        if info.phone:
            return
        info.address = "65-67 Avenue Charles de Gaulle, Yaoundé, Cameroun"
        info.po_box = "BP 660 Yaoundé"
        info.phone = "+237 222 20 45 83 / +237 222 22 09 22"
        info.email = "minefop@outlook.fr"
        info.opening_hours = "Lundi – Vendredi : 7h30 – 15h30"
        info.facebook_url = "https://www.facebook.com/MINEFOPOFFICIEL/"
        info.save()
        self.stdout.write("Contact info created.")

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
             "Organisme chargé de la production de statistiques et d'études sur l'emploi et la formation professionnelle.",
             "https://onefop.cm/", 1),
            ("Projet Intégré d'Appui aux Acteurs du Secteur Informel", "PIAASI",
             "Projet d'appui à la structuration et à la formation des acteurs du secteur informel.", "", 2),
            ("Centres d'Organisation Scolaire, Universitaire et Professionnelle", "COSUP",
             "Structures d'information et d'orientation scolaire, universitaire et professionnelle.", "", 3),
        ]
        for name, acronym, desc, website, order in data:
            AttachedBody.objects.create(name=name, acronym=acronym, description=desc, website=website, order=order)
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
        # Real, publicly documented centres (press coverage of the Cameroon-Korea
        # cooperation CFPE programme and the CPFPR network). Towns are accurate;
        # replace/extend via the admin with the ministry's authoritative registry
        # as more structures are confirmed.
        data = [
            ("Centre de Formation Professionnelle d'Excellence de Sangmélima", TrainingCenter.CenterType.CFPE, "Sud", "Sangmélima", "Bâtiment, Électrotechnique, Froid et Climatisation"),
            ("Centre de Formation Professionnelle d'Excellence de Limbé", TrainingCenter.CenterType.CFPE, "Sud-Ouest", "Limbé", "Mécanique, Hôtellerie, Technologies de l'Information"),
            ("Centre de Formation Professionnelle d'Excellence de Douala", TrainingCenter.CenterType.CFPE, "Littoral", "Douala", "Génie Civil, Électronique, Mécanique Industrielle"),
            ("Centre Public de Formation Professionnelle Rapide de Yaoundé", TrainingCenter.CenterType.CPFPR, "Centre", "Yaoundé", "Informatique, Secrétariat Bureautique, Couture"),
            ("Centre Public de Formation Professionnelle Rapide de Buea", TrainingCenter.CenterType.CPFPR, "Sud-Ouest", "Buea", "Menuiserie, Électricité Bâtiment"),
            ("Centre Public de Formation Professionnelle Rapide de Garoua", TrainingCenter.CenterType.CPFPR, "Nord", "Garoua", "Mécanique Auto, Plomberie"),
            ("Centre Public de Formation Professionnelle Rapide de Pitoa", TrainingCenter.CenterType.CPFPR, "Nord", "Pitoa", "Agro-pastoral, Artisanat"),
            ("Centre National de Formation des Formateurs et de Développement des Programmes", TrainingCenter.CenterType.CNFFDP, "Centre", "Yaoundé", "Ingénierie de la formation, Formation de formateurs, Numérique (D-CLIC)"),
        ]
        for name, ctype, region_name, town, specialties in data:
            TrainingCenter.objects.create(
                name=name,
                center_type=ctype,
                region=regions.get(region_name),
                town=town,
                is_public=True,
                specialties=specialties,
                description=(
                    "Structure publique de formation professionnelle placée sous la tutelle du "
                    "Ministère de l'Emploi et de la Formation Professionnelle."
                ),
            )
        self.stdout.write(
            self.style.WARNING(
                "Verified public training centres created — extend via the admin with the ministry's full authoritative registry."
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
                "Lancement du programme « Un Jeune, un Métier, un Emploi » (JEME)",
                categories["Événement"],
                "Un programme national doté de 17,72 milliards de FCFA pour former, insérer et autonomiser durablement les jeunes camerounais.",
                "Le Ministère de l'Emploi et de la Formation Professionnelle a procédé, le 19 novembre 2025 au Centre National de Formation des Formateurs et de Développement des Programmes (CNFFDP) à Yaoundé, au lancement officiel du programme « Un Jeune, un Métier, un Emploi » (JEME).\n\n"
                "Doté d'une enveloppe globale de 17,72 milliards de FCFA, ce programme s'inscrit dans le prolongement des orientations données par le Chef de l'État, Son Excellence Paul BIYA, lors de son discours d'investiture du 6 novembre 2025 : « Aucun jeune Camerounais ne doit être condamné à l'inactivité. Chaque jeune doit pouvoir apprendre un métier, trouver un emploi ou créer son activité, où qu'il se trouve ».\n\n"
                "JEME cible les jeunes de 15 à 35 ans en zones rurales, péri-urbaines et urbaines, avec pour objectifs de renforcer les filières de formation porteuses, d'équiper les centres de formation professionnelle et de préparer les bénéficiaires à l'emploi salarié ou à l'auto-emploi.",
                date(2025, 11, 19),
            ),
            (
                "Le Ministère défend un budget de 33,4 milliards de FCFA pour 2026",
                categories["Communiqué"],
                "Devant la Commission des Finances et du Budget de l'Assemblée Nationale, le Ministre a présenté les priorités du secteur pour 2026, en particulier le déploiement du programme JEME.",
                "Le Ministre de l'Emploi et de la Formation Professionnelle, Mounouna Foutsou, a défendu le 1er décembre 2025 devant la Commission des Finances et du Budget de l'Assemblée Nationale un projet de budget de 33,4 milliards de FCFA pour l'exercice 2026.\n\n"
                "Ce budget doit permettre la poursuite du déploiement du programme « Un Jeune, un Métier, un Emploi » (JEME), le renforcement des centres publics de formation professionnelle et la modernisation des outils numériques de suivi de l'insertion, notamment la plateforme Inserjeune.",
                date(2025, 12, 1),
            ),
            (
                "Le CNFFDP remet ses premiers parchemins à une cohorte de formateurs",
                categories["Événement"],
                "Le Centre National de Formation des Formateurs et de Développement des Programmes a célébré, le 3 octobre 2025, la sortie de sa toute première promotion.",
                "Le Centre National de Formation des Formateurs et de Développement des Programmes (CNFFDP), créé par décret présidentiel, a franchi une étape historique le 3 octobre 2025 avec la cérémonie de remise des parchemins à sa toute première cohorte de formateurs certifiés.\n\n"
                "Cette promotion vient renforcer le vivier national de formateurs qualifiés, chargés de transmettre les référentiels et méthodes pédagogiques les plus récents dans les structures publiques et privées de formation professionnelle du pays.",
                date(2025, 10, 3),
            ),
            (
                "Recrutement de 265 formateurs et encadreurs au CNFFDP",
                categories["Communiqué"],
                "Le délai de dépôt des candidatures a été prolongé jusqu'au 27 mars 2026 à 15h30.",
                "Le Centre National de Formation des Formateurs et de Développement des Programmes (CNFFDP) a ouvert une campagne de recrutement et de formation certifiante pour 265 formateurs et encadreurs de la formation professionnelle.\n\n"
                "Face à l'intérêt suscité par cette opération stratégique de renforcement de la qualité de l'apprentissage technique et professionnel, le délai de dépôt des candidatures a été prolongé jusqu'au 27 mars 2026 à 15h30. Les candidats intéressés sont invités à se rapprocher du CNFFDP ou des délégations régionales du Ministère.",
                date(2026, 2, 20),
            ),
            (
                "Inserjeune : une plateforme numérique au service de l'insertion professionnelle",
                categories["Actualité"],
                "Plus de 15 000 diplômés de la formation professionnelle sont désormais suivis grâce à cet outil numérique.",
                "Développée avec l'appui de l'Organisation Internationale de la Francophonie, la plateforme « Inserjeune » permet au Ministère de l'Emploi et de la Formation Professionnelle de suivre le parcours d'insertion des diplômés de la formation professionnelle et d'orienter les futurs apprenants vers les filières porteuses.\n\n"
                "L'outil couvre déjà plus de 15 000 diplômés, 350 établissements de formation et 450 entreprises partenaires, répartis sur 19 secteurs et 228 spécialités professionnelles. Les entreprises peuvent y recruter directement et préciser leurs besoins en compétences.",
                date(2025, 9, 15),
            ),
            (
                "Projet D-CLIC : former 300 jeunes aux métiers du numérique",
                categories["Actualité"],
                "Piloté par le CNFFDP avec l'appui de l'Organisation Internationale de la Francophonie, le projet D-CLIC forme des jeunes de 18 à 35 ans à cinq métiers du numérique.",
                "Le projet D-CLIC, mis en œuvre par le Centre National de Formation des Formateurs et de Développement des Programmes avec le soutien de l'Organisation Internationale de la Francophonie (OIF), vise à sélectionner, former et accompagner l'insertion professionnelle de 300 jeunes Camerounais âgés de 18 à 35 ans dans les métiers du numérique.",
                date(2025, 9, 1),
            ),
        ]

        for title, category, excerpt, body, published_date in articles:
            Article.objects.create(
                title=title,
                slug=slugify(title)[:250],
                category=category,
                excerpt=excerpt,
                body=body,
                published_at=timezone.make_aware(datetime.combine(published_date, datetime.min.time())),
            )
        self.stdout.write(
            self.style.SUCCESS(
                "Real, sourced news articles created (JEME, CNFFDP, Inserjeune, D-CLIC — see PR description for sources)."
            )
        )
