from datetime import date, datetime
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.contact.models import ContactInfo
from apps.core.models import HeroSlide, KeyFigure, MinisterMessage, PartnerSite, Timeline
from apps.documents.legacy_library import LEGACY, OTHER_DOCUMENTS, REFERENTIALS
from apps.documents.models import Document, DocumentCategory
from apps.news.models import Article, NewsCategory
from apps.structures.models import AttachedBody, Delegation, OrgUnit, Region, TrainingCenter

SOURCE_PDF_DIR = Path("/root/.claude/uploads/c7a73db5-06c7-58e1-9148-9e5a48db3149")

#: Logo addresses supplied for the portal, keyed by acronym. They are used
#: until the image is mirrored onto this domain — see the management command
#: "fetch_partner_logos".
PARTNER_LOGO_URLS = {
    "PRC": "https://www.minjec.gov.cm/portail/images/bloc/prc.png",
    "SPM": "https://www.minjec.gov.cm/portail/images/bloc/spm.jpg",
    "MINJEC": "https://minjec.gov.cm/site/wp-content/uploads/2022/10/logo.png",
    "ONJ": "https://www.minjec.gov.cm/portail/images/bloc/onj.png",
    "CNJC": "https://raw.githubusercontent.com/forchag/SOME-PICS/refs/heads/main/new.jpeg",
    "JobHub": "https://raw.githubusercontent.com/forchag/SOME-PICS/refs/heads/main/cnjcnycjoblogo.png",
    "FNE": "https://fnecm.org/images/stories/lefne7questions/LogoFNEnu.png",
    "ONEFOP": "https://onefop.cm/wp-content/uploads/2026/04/WhatsApp-Image-2026-04-07-at-07.43.13.jpeg",
    "PIAASI": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRRdA0liNY2iPRS6czCI_QXUASXGhpUNWkm1wSlw2YE&s=10",
    "CIOP": "https://www.orientation.cm/wp-content/uploads/2019/06/logo-cosup.png",
    "CNFFDP": "https://raw.githubusercontent.com/forchag/SOME-PICS/refs/heads/main/Logo%20CNFFDP.png",
}


def legacy_url(fragment):
    """Percent-encode a legacy ``minefop.cm/images`` path so it is a valid URL."""
    from urllib.parse import quote

    return LEGACY + quote(fragment)


class Command(BaseCommand):
    help = "Seed the MINEFOP database with the ministry's organisational structure, legal texts and published content."

    def handle(self, *args, **options):
        self.seed_key_figures()
        self.seed_timeline()
        self.seed_minister()
        self.seed_contact_info()
        self.seed_partner_sites()
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
            ("Spécialités professionnelles recensées", "228", "bi-tools", 4),
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
            ("2021", "Lancement du PADESCE", "Projet d'appui au développement de l'enseignement secondaire et des compétences pour la croissance et l'emploi, soutenu par la Banque mondiale et articulé autour de quatre domaines de compétence : bâtiments et travaux publics, agro-industrie, énergie et numérique.", 6),
            ("2023", "Création du CNFFDP", "Décret portant création et organisation du Centre National de Formation des Formateurs et de Développement des Programmes.", 7),
            ("2023", "Déploiement d'Inserjeune", "Mise en service de la plateforme numérique de suivi de l'insertion professionnelle des diplômés de la formation professionnelle.", 8),
            ("2025", "Ouverture des Centres Sectoriels de Formation Professionnelle de Douala et d'Edéa", "Deux pôles de formation adossés au partenariat public-privé : maintenance industrielle, logistique et transport à Edéa, agroalimentaire à Douala.", 9),
            ("2025", "Lancement du programme national de formation et d'insertion professionnelles (JEME)", "Programme lancé le 19 novembre 2025 au CNFFDP, en application des orientations du Chef de l'État, pour former, qualifier et insérer durablement en zones rurales, péri-urbaines et urbaines.", 10),
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
            "que j'exerce avec le sens du devoir, au service de l'employabilité de nos "
            "compatriotes.\n\n"
            "Le chômage et le sous-emploi ne frappent pas une seule classe d'âge : ils touchent "
            "aussi bien celui qui sort d'un centre de formation que le travailleur dont le métier "
            "évolue ou disparaît. C'est pourquoi nos dispositifs de formation, de requalification "
            "et de placement sont ouverts à toute personne en recherche d'emploi, en reconversion "
            "ou en quête d'une qualification, sans condition d'âge — la loi n° 2018/010 du 11 "
            "juillet 2018 garantissant l'égal accès à la formation, dans les deux langues "
            "officielles, à toute personne remplissant les conditions requises.\n\n"
            "Conformément aux orientations du Chef de l'État, Son Excellence Paul BIYA, exprimées "
            "lors de son discours d'investiture du 6 novembre 2025, selon lesquelles chacun doit "
            "pouvoir apprendre un métier, trouver un emploi ou créer son activité où qu'il se "
            "trouve, le Ministère a lancé le 19 novembre 2025 le programme « Un Jeune, un Métier, "
            "un Emploi » (JEME), qui complète un dispositif national couvrant les zones rurales, "
            "péri-urbaines et urbaines.\n\n"
            "Cette ambition s'appuie sur la modernisation continue de notre dispositif : la "
            "plateforme numérique Inserjeune, qui assure le suivi de plus de 15 000 diplômés de la "
            "formation professionnelle, le projet D-CLIC mené avec l'Organisation Internationale de "
            "la Francophonie pour former aux métiers du numérique, la formation en alternance "
            "portée par FORMPRO 237, et le renforcement des capacités pédagogiques de nos "
            "formateurs à travers le Centre National de Formation des Formateurs et de "
            "Développement des Programmes (CNFFDP).\n\n"
            "Ce site se veut un espace d'information transparent sur nos missions, notre "
            "organisation, nos centres de formation, nos référentiels de métiers et les textes qui "
            "encadrent notre action. Je vous souhaite une excellente navigation."
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
    def seed_partner_sites(self):
        """The website directory published on the entry portal.

        Placement is deliberate: the institutions of the Republic and the youth
        bodies flank the card on the left, the employment and training bodies on
        the right, each tile carrying the banner colour of the Ministry's
        portal. Any of it can be reordered, recoloured or hidden afterwards from
        **Sites partenaires** in the administration.
        """
        if PartnerSite.objects.exists():
            return

        institution = PartnerSite.Group.INSTITUTION
        partner = PartnerSite.Group.PARTNER
        service = PartnerSite.Group.SERVICE
        left = PartnerSite.Column.LEFT
        right = PartnerSite.Column.RIGHT

        # (column, order, group, name, acronym, url, tint, description, active)
        # Logo addresses are supplied per structure below via LOGO_URLS.
        data = [
            (left, 1, institution, "Présidence de la République du Cameroun", "PRC",
             "https://www.prc.cm", "#27ae60",
             "Institution présidentielle de la République.", True),
            (left, 2, institution, "Services du Premier Ministre", "SPM",
             "https://www.spm.gov.cm", "#e74c3c",
             "Chef du Gouvernement et coordination de l'action gouvernementale.", True),
            (left, 3, institution, "Ministère de la Jeunesse et de l'Éducation Civique", "MINJEC",
             "https://minjec.gov.cm", "#e74c3c",
             "Politique nationale de la jeunesse et de l'éducation civique.", True),
            (left, 4, partner, "Observatoire National de la Jeunesse", "ONJ",
             "https://www.onjcameroun.cm", "#f39c12",
             "Observation et analyse des conditions de vie de la jeunesse.", True),
            (left, 5, partner, "Conseil National de la Jeunesse du Cameroun", "CNJC",
             "https://www.cnjcnyc.cm", "#3498db",
             "Instance nationale de représentation et de concertation de la jeunesse.", True),
            (left, 6, service, "CNJC JobHub", "JobHub",
             "https://www.cnjcjobhub.cm", "#3498db",
             "Plateforme de mise en relation entre offres d'emploi et candidats.", True),

            (right, 1, partner, "Fonds National de l'Emploi", "FNE",
             "https://fnecm.org", "#16a085",
             "Placement, financement de projets et formation des demandeurs d'emploi.", True),
            (right, 2, partner, "Observatoire National de l'Emploi et de la Formation Professionnelle", "ONEFOP",
             "https://onefop.cm", "#d35400",
             "Statistiques, annuaires et études sur l'emploi et la formation professionnelle.", True),
            (right, 3, partner, "Projet Intégré d'Appui aux Acteurs du Secteur Informel", "PIAASI",
             "", "#9b59b6",
             "Structuration, formation et accompagnement des acteurs du secteur informel.", True),
            (right, 4, partner, "Centres d'Information et d'Orientation Professionnelle", "CIOP",
             "http://www.orientation.cm", "#34495e",
             "Information, conseil et orientation scolaire, universitaire et professionnelle.", True),
            (right, 5, partner, "Centre National de Formation des Formateurs et de Développement des Programmes", "CNFFDP",
             "https://www.cnffdp.cm", "#34495e",
             "Formation des formateurs et ingénierie des programmes de formation.", True),

            # Recorded but not shown on the portal: switch "affiché sur le
            # portail" on in the administration to add either to a column.
            (right, 6, partner, "Projet d'Appui au Développement de l'Enseignement Secondaire et des Compétences pour la Croissance et l'Emploi", "PADESCE",
             "", "#34495e",
             "Refonte des référentiels de métiers et équipement des structures de formation.", False),
            (right, 7, service, "Plateforme SIGE — Système d'Information et de Gestion de l'Éducation", "SIGE",
             "http://www.sige-sectoriel.cm", "#34495e",
             "Système d'information sectoriel de l'éducation et de la formation.", False),
            (right, 8, service, "Inserjeune — suivi post-formation", "Inserjeune",
             "https://app.inserjeune.edu.cm", "#34495e",
             "Suivi de l'insertion des diplômés et mise en relation avec les entreprises.", False),
        ]

        logo_dir = Path(settings.STATICFILES_DIRS[0]) / "img" / "partners"
        for column, order, group, name, acronym, url, tint, description, is_active in data:
            site = PartnerSite(
                column=column,
                order=order,
                group=group,
                name=name,
                acronym=acronym,
                url=url,
                tint=tint,
                description=description,
                is_active=is_active,
            )
            site.logo_url = PARTNER_LOGO_URLS.get(acronym, "")
            logo_name = PartnerSite.BUNDLED_LOGOS.get(acronym)
            logo_path = logo_dir / logo_name if logo_name else None
            if logo_path and logo_path.exists():
                with logo_path.open("rb") as f:
                    site.logo.save(logo_name, File(f), save=False)
            site.save()
        self.stdout.write("Portal website directory created.")

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
            mission="Gestion des ressources humaines, des moyens financiers, des infrastructures et des équipements du Ministère.",
        )
        create("Cellule de Gestion du Projet SIGIPES", "cellule", parent=affaires_generales, order=1, legal_reference="Article 50")
        create("Sous-direction du Personnel, de la Solde et des Pensions", "sous_direction", parent=affaires_generales, order=2, legal_reference="Article 51")
        create("Sous-direction du Budget", "sous_direction", parent=affaires_generales, order=3, legal_reference="Article 55")
        create("Sous-direction des Infrastructures, des Équipements et de la Maintenance", "sous_direction", parent=affaires_generales, order=4, legal_reference="Article 58")

        self.stdout.write("Organisational chart created.")

    def seed_attached_bodies(self):
        if AttachedBody.objects.exists():
            return

        body = AttachedBody.Kind.BODY
        programme = AttachedBody.Kind.PROGRAMME

        data = [
            (body, "Fonds National de l'Emploi", "FNE",
             "Organisme sous tutelle du Ministère, chargé du placement des demandeurs d'emploi, "
             "du financement de projets et de la formation professionnelle des candidats à l'emploi "
             "comme des travailleurs en reconversion.",
             "https://fnecm.org", 1),
            (body, "Observatoire National de l'Emploi et de la Formation Professionnelle", "ONEFOP",
             "Organisme chargé de la production de statistiques et d'études sur l'emploi et la "
             "formation professionnelle : annuaire statistique de la formation professionnelle, "
             "études de suivi post-formation et publication « Regard sur l'emploi ».",
             "https://onefop.cm", 2),
            (body, "Centre National de Formation des Formateurs et de Développement des Programmes", "CNFFDP",
             "Créé par décret présidentiel en 2023, le Centre forme les formateurs et encadreurs de "
             "la formation professionnelle et développe les référentiels et programmes de formation.",
             "https://www.cnffdp.cm", 3),
            (body, "Centres d'Information et d'Orientation Professionnelle", "CIOP",
             "Structures d'information, de conseil et d'orientation scolaire, universitaire et "
             "professionnelle, ouvertes aux élèves, aux étudiants comme aux adultes en reconversion.",
             "http://www.orientation.cm", 4),
            (body, "Projet Intégré d'Appui aux Acteurs du Secteur Informel", "PIAASI",
             "Projet d'appui à la structuration, à la formation et au financement des acteurs du "
             "secteur informel.",
             "", 5),

            (programme, "Programme « Un Jeune, un Métier, un Emploi »", "JEME",
             "Programme national lancé le 19 novembre 2025 au CNFFDP. Il renforce les filières de "
             "formation porteuses, équipe les centres de formation professionnelle et prépare les "
             "bénéficiaires à l'emploi salarié comme à la création d'activité, en zones rurales, "
             "péri-urbaines et urbaines.",
             "", 1),
            (programme, "Projet d'Appui au Développement de l'Enseignement Secondaire et des Compétences pour la Croissance et l'Emploi", "PADESCE",
             "Projet gouvernemental soutenu par la Banque mondiale, conduit avec le Ministère des "
             "Enseignements Secondaires. Il couvre quatre domaines de compétence — bâtiments et "
             "travaux publics, agro-industrie, énergie et numérique — et a permis l'élaboration de "
             "quatre générations de référentiels de formation.",
             "", 2),
            (programme, "Mécanisme Compétitif de Développement des Compétences", "MCDC-PSOAF",
             "Fenêtres de financement du PADESCE destinées aux structures de formation et aux "
             "entreprises : qualification des prestataires de formation, accueil d'apprentis en "
             "entreprise et appuis aux entités bénéficiaires.",
             "", 3),
            (programme, "Coopération Cameroun – France, contrats de désendettement et de développement (C2D) Formation Professionnelle", "C2D",
             "Projets de formation professionnelle financés par l'Agence Française de Développement, "
             "dont FORMPRO 237, qui promeut la formation en alternance entre le centre et "
             "l'entreprise.",
             "", 4),
            (programme, "Projet D-CLIC — formation aux métiers du numérique", "D-CLIC",
             "Projet mis en œuvre par le CNFFDP avec l'appui de l'Organisation Internationale de la "
             "Francophonie : sélection, formation et accompagnement à l'insertion de 300 "
             "bénéficiaires dans cinq métiers du numérique.",
             "", 5),
            (programme, "Appui à la formation professionnelle avec la coopération allemande (GIZ)", "GIZ",
             "Élaboration et homologation de référentiels de formation agricoles et agro-alimentaires "
             "avec l'appui de la coopération allemande.",
             "", 6),
        ]
        for kind, name, acronym, description, website, order in data:
            AttachedBody.objects.create(
                kind=kind,
                name=name,
                acronym=acronym,
                description=description,
                website=website,
                order=order,
            )
        self.stdout.write("Attached bodies, programmes and projects created.")

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
        # cooperation CFPE programme, the CPFPR network and the sectoral centres
        # of Douala and Edéa). Towns are accurate; replace/extend via the admin
        # with the ministry's authoritative registry as more structures are
        # confirmed.
        default_description = (
            "Structure publique de formation professionnelle placée sous la tutelle du "
            "Ministère de l'Emploi et de la Formation Professionnelle."
        )
        sectoral_description = (
            "Centre sectoriel né du partenariat entre les secteurs public et privé. Il "
            "développe une offre de formation adaptée aux besoins des entreprises, afin de "
            "former des ouvriers et techniciens qualifiés et de faciliter l'accès à l'emploi "
            "des personnes formées."
        )
        data = [
            ("Centre de Formation Professionnelle d'Excellence de Sangmélima", TrainingCenter.CenterType.CFPE, "Sud", "Sangmélima", "Bâtiment, Électrotechnique, Froid et Climatisation", default_description),
            ("Centre de Formation Professionnelle d'Excellence de Limbé", TrainingCenter.CenterType.CFPE, "Sud-Ouest", "Limbé", "Mécanique, Hôtellerie, Technologies de l'Information", default_description),
            ("Centre de Formation Professionnelle d'Excellence de Douala", TrainingCenter.CenterType.CFPE, "Littoral", "Douala", "Génie Civil, Électronique, Mécanique Industrielle", default_description),
            ("Centre Sectoriel de Formation Professionnelle de Douala", TrainingCenter.CenterType.CSFP, "Littoral", "Douala", "Agroalimentaire", sectoral_description),
            ("Centre Sectoriel de Formation Professionnelle d'Edéa", TrainingCenter.CenterType.CSFP, "Littoral", "Edéa", "Maintenance industrielle, Logistique et Transport", sectoral_description),
            ("Centre Public de Formation Professionnelle Rapide de Yaoundé", TrainingCenter.CenterType.CPFPR, "Centre", "Yaoundé", "Informatique, Secrétariat Bureautique, Couture", default_description),
            ("Centre Public de Formation Professionnelle Rapide de Buea", TrainingCenter.CenterType.CPFPR, "Sud-Ouest", "Buea", "Menuiserie, Électricité Bâtiment", default_description),
            ("Centre Public de Formation Professionnelle Rapide de Garoua", TrainingCenter.CenterType.CPFPR, "Nord", "Garoua", "Mécanique Auto, Plomberie", default_description),
            ("Centre Public de Formation Professionnelle Rapide de Pitoa", TrainingCenter.CenterType.CPFPR, "Nord", "Pitoa", "Agro-pastoral, Artisanat", default_description),
            ("Centre de Formation aux Métiers de Bandjoun", TrainingCenter.CenterType.CFM, "Ouest", "Bandjoun", "Métiers techniques et artisanaux", default_description),
            ("Centre National de Formation des Formateurs et de Développement des Programmes", TrainingCenter.CenterType.CNFFDP, "Centre", "Yaoundé", "Ingénierie de la formation, Formation de formateurs, Numérique (D-CLIC)", default_description),
        ]
        for name, ctype, region_name, town, specialties, description in data:
            TrainingCenter.objects.create(
                name=name,
                center_type=ctype,
                region=regions.get(region_name),
                town=town,
                is_public=True,
                specialties=specialties,
                description=description,
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

        category_definitions = [
            ("lois", "Lois", 1),
            ("decrets", "Décrets", 2),
            ("arretes", "Arrêtés", 3),
            ("decisions", "Décisions", 4),
            ("communiques", "Communiqués & appels à candidatures", 5),
            ("formulaires", "Formulaires", 6),
            ("referentiels", "Référentiels de formation", 7),
            ("publications", "Publications & statistiques", 8),
            ("rapports", "Rapports & études", 9),
        ]
        categories = {}
        for slug, name, order in category_definitions:
            categories[slug], _created = DocumentCategory.objects.get_or_create(
                slug=slug, defaults={"name": name, "order": order}
            )

        legal_texts = [
            (
                "Décret n° 2012/644 du 28 décembre 2012 portant organisation du Ministère de l'Emploi et de la Formation Professionnelle",
                categories["decrets"],
                "Décret n° 2012/644 du 28/12/2012",
                date(2012, 12, 28),
                "e26900d9-DECRET_2012_ORGANISATION_DU_MINISTERE_DE_LEMPLOI__260726_114606.pdf",
            ),
            (
                "Loi n° 2018/010 du 11 juillet 2018 régissant la formation professionnelle au Cameroun",
                categories["lois"],
                "Loi n° 2018/010 du 11/07/2018",
                date(2018, 7, 11),
                "cc7835c2-LOI_SUR_LA_FORMATION_PROFESSIONNELLE_AU_CAMEROUN_260726_114636.pdf",
            ),
            (
                "Décret n° 2020/2592/PM du 9 juin 2020 fixant les modalités de création, d'organisation et de fonctionnement des centres de formation professionnelle et d'apprentissage",
                categories["decrets"],
                "Décret n° 2020/2592/PM du 09/06/2020",
                date(2020, 6, 9),
                "bbc65b8a-5120620Decretdu19juin2020_Centresdeformat_260726_120146.pdf",
            ),
            (
                "Décret n° 2023 portant création et organisation du Centre National de Formation des Formateurs et de Développement des Programmes (CNFFDP)",
                categories["decrets"],
                "Décret n° 2023",
                date(2023, 5, 4),
                "3af6feaf-721ef49c1081eaebbbbd9be87a80573b_260726_120323.pdf",
            ),
        ]

        for title, category, reference, published_date, filename in legal_texts:
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

        # Documentary holdings carried over from the Ministry's previous site.
        # The files stay at their original address until they are re-uploaded
        # through the administration interface.
        referential_description = (
            "Référentiel de formation homologué par le Ministère de l'Emploi et de la "
            "Formation Professionnelle : compétences visées, contenus et modalités "
            "d'évaluation du métier."
        )
        for title, reference, fragment in REFERENTIALS:
            Document.objects.create(
                title=f"Référentiel de formation — {title}",
                category=categories["referentiels"],
                reference_number=reference,
                description=referential_description,
                source_url=legacy_url(fragment),
            )

        for category_slug, title, reference, fragment in OTHER_DOCUMENTS:
            Document.objects.create(
                title=title,
                category=categories[category_slug],
                reference_number=reference,
                source_url=legacy_url(fragment),
            )

        self.stdout.write(
            "Legal texts and the documentary holdings of the previous site created "
            f"({Document.objects.count()} documents)."
        )

    def seed_news(self):
        if Article.objects.exists():
            return

        category_definitions = [("communique", "Communiqué"), ("actualite", "Actualité"), ("evenement", "Événement")]
        categories = {}
        for slug, name in category_definitions:
            categories[slug], _created = NewsCategory.objects.get_or_create(
                slug=slug, defaults={"name": name}
            )

        articles = [
            (
                "Lancement du programme national de formation et d'insertion professionnelles (JEME)",
                categories["evenement"],
                "Un programme national pour former, qualifier et insérer durablement, en zones rurales, péri-urbaines et urbaines.",
                "Le Ministère de l'Emploi et de la Formation Professionnelle a procédé, le 19 novembre 2025 au Centre National de Formation des Formateurs et de Développement des Programmes (CNFFDP) à Yaoundé, au lancement officiel du programme « Un Jeune, un Métier, un Emploi » (JEME).\n\n"
                "Le programme s'inscrit dans le prolongement des orientations données par le Chef de l'État, Son Excellence Paul BIYA, lors de son discours d'investiture du 6 novembre 2025, appelant à ce que chacun puisse apprendre un métier, trouver un emploi ou créer son activité, où qu'il se trouve.\n\n"
                "Il a pour objectifs de renforcer les filières de formation porteuses, d'équiper les centres de formation professionnelle et de préparer les bénéficiaires à l'emploi salarié comme à la création d'activité. Il complète un dispositif national ouvert à toute personne en recherche d'emploi, en reconversion ou en quête d'une qualification, sans condition d'âge.",
                date(2025, 11, 19),
            ),
            (
                "Le CNFFDP remet ses premiers parchemins à une cohorte de formateurs",
                categories["evenement"],
                "Le Centre National de Formation des Formateurs et de Développement des Programmes a célébré, le 3 octobre 2025, la sortie de sa toute première promotion.",
                "Le Centre National de Formation des Formateurs et de Développement des Programmes (CNFFDP), créé par décret présidentiel, a franchi une étape historique le 3 octobre 2025 avec la cérémonie de remise des parchemins à sa toute première cohorte de formateurs certifiés.\n\n"
                "Cette promotion vient renforcer le vivier national de formateurs qualifiés, chargés de transmettre les référentiels et méthodes pédagogiques les plus récents dans les structures publiques et privées de formation professionnelle du pays.",
                date(2025, 10, 3),
            ),
            (
                "Recrutement de 265 formateurs et encadreurs au CNFFDP",
                categories["communique"],
                "Le délai de dépôt des candidatures a été prolongé jusqu'au 27 mars 2026 à 15h30.",
                "Le Centre National de Formation des Formateurs et de Développement des Programmes (CNFFDP) a ouvert une campagne de recrutement et de formation certifiante pour 265 formateurs et encadreurs de la formation professionnelle.\n\n"
                "Face à l'intérêt suscité par cette opération stratégique de renforcement de la qualité de l'apprentissage technique et professionnel, le délai de dépôt des candidatures a été prolongé jusqu'au 27 mars 2026 à 15h30. Les candidats intéressés sont invités à se rapprocher du CNFFDP ou des délégations régionales du Ministère.",
                date(2026, 2, 20),
            ),
            (
                "Inserjeune : une plateforme numérique au service de l'insertion professionnelle",
                categories["actualite"],
                "Plus de 15 000 diplômés de la formation professionnelle sont désormais suivis grâce à cet outil numérique.",
                "Développée avec l'appui de l'Organisation Internationale de la Francophonie, la plateforme « Inserjeune » permet au Ministère de l'Emploi et de la Formation Professionnelle de suivre le parcours d'insertion des diplômés de la formation professionnelle et d'orienter les futurs apprenants vers les filières porteuses.\n\n"
                "L'outil couvre déjà plus de 15 000 diplômés, 350 établissements de formation et 450 entreprises partenaires, répartis sur 19 secteurs et 228 spécialités professionnelles. Les entreprises peuvent y recruter directement et préciser leurs besoins en compétences.",
                date(2025, 9, 15),
            ),
            (
                "Projet D-CLIC : former aux métiers du numérique",
                categories["actualite"],
                "Piloté par le CNFFDP avec l'appui de l'Organisation Internationale de la Francophonie, le projet D-CLIC forme 300 bénéficiaires à cinq métiers du numérique.",
                "Le projet D-CLIC, mis en œuvre par le Centre National de Formation des Formateurs et de Développement des Programmes avec le soutien de l'Organisation Internationale de la Francophonie (OIF), vise à sélectionner, former et accompagner l'insertion professionnelle de 300 bénéficiaires camerounais dans les métiers du numérique.",
                date(2025, 9, 1),
            ),
            # ----------------------------------------------------------------
            # Articles carried over from the Ministry's previous website.
            # ----------------------------------------------------------------
            (
                "Coopération Cameroun – France : le point à l'issue d'une mission de supervision de l'AFD sur les projets C2D Formation Professionnelle",
                categories["actualite"],
                "Une délégation de l'Agence Française de Développement a été reçue le 8 juillet 2025 par le Ministre de l'Emploi et de la Formation Professionnelle par intérim.",
                "Conduite par monsieur Sylvain Clément, responsable d'équipe projet en charge du portefeuille formation professionnelle pour le Cameroun au sein de la Division Éducation, Formation, Emploi de l'AFD à Paris, accompagné de madame Chrystelle Tapouh, responsable du Pôle Développement Humain et Gouvernance à l'Agence Française de Développement de Yaoundé, la délégation a été reçue par le Ministre de l'Emploi et de la Formation Professionnelle par intérim, S.E. Mounouna Foutsou, le mardi 8 juillet 2025 à 17 heures, dans la salle de réunions du Ministère de la Jeunesse et de l'Éducation Civique à Yaoundé.\n\n"
                "La séance de travail a donné lieu à une restitution des constats et observations de la mission. Celle-ci avait pour objectif de faire le point des activités en cours, afin de corriger, par des leviers appropriés, les éventuels manquements relevés.",
                date(2025, 7, 9),
            ),
            (
                "Coopération entre le MINEFOP et le groupe CFAO Mobility",
                categories["actualite"],
                "Une délégation du groupe CFAO Mobility a été reçue en audience le 7 juillet 2025 autour de la création de centres de formation aux métiers de la mécanique automobile.",
                "Le Ministre de l'Emploi et de la Formation Professionnelle par intérim, S.E. Mounouna Foutsou, a accordé une audience à une délégation du groupe CFAO Mobility conduite par madame Thérèse Souga, directrice des Ressources Humaines, accompagnée de madame Béla-Donne, responsable administratif et financier, et de monsieur Armand Ndomche, directeur des Relations Publiques et du Développement B2G, le lundi 7 juillet 2025 dans son cabinet.\n\n"
                "Entamée à 16h30, la séance de travail avait pour objet de présenter l'état de la coopération entre le MINEFOP et le groupe CFAO Mobility, avec en ligne de mire les possibilités de création de centres de formation professionnelle spécialisés dans les métiers de la mécanique automobile, en synergie avec le Centre de Formation régional Automotive & Equipment de CFAO basé à Douala.\n\n"
                "Pour mémoire, ce centre de formation avait autrefois bénéficié d'un agrément du MINEFOP. Ses formations ayant principalement pour objectif le recyclage des employés de CFAO Mobility en Afrique centrale et de l'Ouest en vue de certifications internes à l'entreprise, ses responsables n'avaient plus jugé utile d'en renouveler l'agrément, dans la mesure où elles ne débouchaient pas sur les certifications du MINEFOP.\n\n"
                "Dans l'optique de revenir à l'orthodoxie et de redonner une nouvelle dynamique à ce secteur à fort potentiel d'employabilité, un mémorandum d'entente a été proposé au membre du Gouvernement.",
                date(2025, 7, 8),
            ),
            (
                "Synopsis des Centres Sectoriels de Formation Professionnelle de Douala et d'Edéa",
                categories["actualite"],
                "Deux pôles de formation adossés au partenariat public-privé, conçus pour répondre aux besoins réels des entreprises.",
                "Les Centres Sectoriels de Formation Professionnelle (CFPS) de Douala et d'Edéa ont pour objectif principal de développer une offre de formation professionnelle de qualité, adaptée aux besoins des entreprises, afin de former des ouvriers et techniciens qualifiés et de favoriser ainsi la croissance économique et l'accès à l'emploi au Cameroun.\n\n"
                "Objectifs spécifiques des CFPS de Douala et d'Edéa :\n\n"
                "Formation professionnelle ciblée — les CFPS se concentrent sur des secteurs spécifiques : la maintenance industrielle, la logistique et le transport à Edéa, l'agroalimentaire à Douala.\n\n"
                "Partenariat public-privé — le projet repose sur une collaboration étroite entre les secteurs public et privé, assurant une meilleure adéquation de la formation aux besoins du marché.\n\n"
                "Qualité de la formation — l'objectif est d'offrir une formation de haut niveau, reconnue par les entreprises, et de garantir une meilleure insertion professionnelle des personnes formées.\n\n"
                "Croissance économique — en formant une main-d'œuvre qualifiée, les CFPS contribuent à la croissance économique du pays en répondant aux besoins des entreprises et en favorisant l'emploi.\n\n"
                "Développement des compétences — les CFPS développent les compétences des apprenants dans des domaines précis, en fonction des besoins des entreprises et des filières identifiées.\n\n"
                "En résumé, les CFPS de Douala et d'Edéa sont des pôles de formation professionnelle innovants, axés sur les besoins du marché du travail, qui contribuent au développement économique du Cameroun grâce à une formation de qualité et à un meilleur accès à l'emploi.",
                date(2025, 7, 6),
            ),
            (
                "« Capitaliser toutes les expériences » : la formation en alternance au cœur des priorités",
                categories["actualite"],
                "À l'issue d'échanges avec le CFAA de Limoges, le Ministre appelle à une mise en œuvre rapide du plan de travail sur la formation en alternance.",
                "Alors que l'alternance est citée comme modalité clé de la formation en apprentissage, Mounouna Foutsou déclare : « Je suis moi-même un amoureux de la formation en alternance. Quand en 2009 je suis nommé Secrétaire d'État, la première activité que j'ai recommandée, c'était de pouvoir faire la formation en alternance dans l'enseignement normal. » Il faut donc insister encore davantage sur cette formule, utilisée dans FORMPRO 237.\n\n"
                "Pour le MINEFOP, il est indispensable de « capitaliser toutes les expériences ». À ce sujet, l'accompagnement apporté par le CFAA de Limoges est le bienvenu, le Ministre affirmant qu'il peut être mené « en distanciel ».\n\n"
                "« Pour la suite, il faut passer à l'action rapidement », conclut-il.\n\n"
                "Après des échanges nourris, des résolutions ont été prises selon les instructions du membre du Gouvernement, pour une mise en œuvre rapide du plan de travail des jours, semaines et mois à venir. La photo de famille a mis un terme à une rencontre riche en échanges, en résolutions et en perspectives pour l'emploi et la formation professionnelle au Cameroun.",
                date(2025, 7, 6),
            ),
            (
                "Entreprises de travail temporaire : 147 structures agréées",
                categories["communique"],
                "Dans un communiqué rendu public le 16 février 2023, le Ministre de l'Emploi et de la Formation Professionnelle a dévoilé la liste des structures autorisées.",
                "Dans un communiqué, le Ministre de l'Emploi et de la Formation Professionnelle a informé les entreprises publiques, parapubliques et privées — en particulier celles utilisatrices de la main-d'œuvre temporaire — détentrices d'un agrément en cours de validité, qu'elles sont autorisées à exercer au titre de l'année 2023 jusqu'aux dates d'expiration respectives de leur agrément.\n\n"
                "Le communiqué daté du 16 février 2023 indique que cette sortie a pour objectif de mettre de l'ordre dans le secteur, d'une part, et de permettre aux usagers d'être orientés vers les entreprises agréées, d'autre part. 147 d'entre elles, détenant déjà un agrément, peuvent ainsi bénéficier de cette disposition. Le MINEFOP « invite par conséquent tous les chefs d'entreprises à ne faire recours qu'aux services des structures citées ».\n\n"
                "Par ailleurs, dans ce même document, le Ministre exhorte les promoteurs d'entreprises de travail temporaire dont les structures ne figurent pas sur la liste et qui continuent d'exercer leurs activités à se conformer à la réglementation en vigueur dans les meilleurs délais, faute de quoi ils s'exposent aux sanctions prévues.",
                date(2023, 5, 15),
            ),
            (
                "PADESCE : éducation et formation changent de cap",
                categories["actualite"],
                "Le Projet d'appui au développement de l'enseignement secondaire et des compétences pour la croissance et l'emploi a fait l'objet d'une communication institutionnelle à Douala.",
                "Le Projet d'appui au développement de l'enseignement secondaire et des compétences pour la croissance et l'emploi (PADESCE) a mobilisé, le vendredi 28 avril 2023 à Douala, cinq membres du Gouvernement et assimilés autour d'une communication institutionnelle. Les maîtres d'œuvre du projet — la Ministre des Enseignements Secondaires, le Ministre de l'Emploi et de la Formation Professionnelle, ainsi que leurs homologues des Postes et Télécommunications, de la Jeunesse et de l'Éducation Civique, de l'Agriculture et du Développement Rural, et le Secrétaire Général du MINPMEESA — étaient réunis pour l'occasion.\n\n"
                "Étaient également présents le représentant de la Banque mondiale, principal financier du projet, le gouverneur de la région du Littoral et le deuxième adjoint au maire de la ville.\n\n"
                "La première étape de la communication institutionnelle a été la présentation du projet par la coordinatrice générale, Dr Paulette Marceline Bayiha. Selon elle, le PADESCE part d'un constat précis : les programmes des établissements de formation technique et professionnelle (EFTP) du Cameroun ne produisent pas les types et les niveaux de compétences répondant à la demande actuelle du secteur formel de l'économie ni à la transformation économique du pays.\n\n"
                "Pour l'enseignement secondaire général, les taux de promotion sont faibles dans le public par rapport au privé, et l'on note un gaspillage des ressources dans les établissements. Il est donc question, à travers le PADESCE, d'améliorer l'accès équitable à un enseignement secondaire de qualité et à une formation technique et professionnelle adaptée au marché. Le PADESCE couvre quatre domaines de compétence : bâtiments et travaux publics, agro-industrie, énergie et numérique.",
                date(2023, 5, 15),
            ),
            (
                "Travailleurs étrangers en situation irrégulière : on passe à l'offensive",
                categories["actualite"],
                "Un groupe interministériel a effectué une descente inopinée dans des entreprises installées à Nanga-Eboko.",
                "Le groupe interministériel chargé de veiller à la régularité des travailleurs de nationalité étrangère sur l'ensemble du territoire a effectué une descente inopinée dans la ville de Nanga-Eboko, département de la Haute-Sanaga, région du Centre. La mission était conduite par Jeanine Ngo'o Eba, directeur de la Régulation de la Main-d'œuvre au Ministère de l'Emploi et de la Formation Professionnelle.\n\n"
                "Le premier arrêt, effectué au sein d'une entreprise spécialisée dans la transformation et l'exportation du bois, a permis à la délégation de relever plusieurs irrégularités. L'examen des documents d'un employé étranger rencontré sur le site a montré que son récépissé, l'indiquant comme commerçant, avait expiré ; entré au Cameroun avec un visa de 90 jours, il se trouvait en situation d'irrégularité depuis lors, et ne détenait aucun contrat de travail, document pourtant exigé par la réglementation en vigueur pour les travailleurs étrangers.\n\n"
                "Un procès-verbal de constat de violation de la réglementation en vigueur en matière d'emploi des personnes de nationalité étrangère au Cameroun a été dressé. Ledit document précise que l'entreprise concernée doit verser six millions de francs CFA au Trésor public au titre de pénalités.",
                date(2023, 5, 15),
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
                f"News articles created ({Article.objects.count()}), including those "
                "carried over from the Ministry's previous website."
            )
        )
