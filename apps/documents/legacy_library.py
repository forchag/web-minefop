"""Catalogue of the documents published on the Ministry's previous website.

The PDF files themselves are still served from the legacy ``minefop.cm/images``
tree, so each entry carries a ``source_url`` rather than an uploaded file. Once
a document is re-uploaded through the administration interface, the stored file
takes precedence over the legacy address (see ``Document.download_url``).

Every title below comes from the previous site; the wording was normalised
(sentence case, expanded abbreviations, corrected typography) but no document
was added, removed or renamed beyond that.
"""

LEGACY = "https://minefop.cm/images/"

# Training reference frameworks ("référentiels de formation"). Each tuple is
# (title, reference label, URL fragment relative to LEGACY).
WAVE_1 = "PADESCE — référentiels de 2e génération (vague 1)"
WAVE_2 = "PADESCE — référentiels de 3e génération (vague 2)"
WAVE_3 = "PADESCE — référentiels de 4e génération (vague 3)"
GIZ = "Référentiels homologués avec l'appui de la coopération allemande (GIZ)"

REFERENTIALS = [
    # ---- PADESCE, vague 1 -------------------------------------------------
    ("Concepteur de logiciels", WAVE_1, "VAGUE1/CONCEPTEUR DE LOGICIEL.pdf"),
    ("Développeur web", WAVE_1, "VAGUE1/DEVELOPPEUR WEB.pdf"),
    ("Éleveur de bovins et de petits ruminants", WAVE_1, "VAGUE1/ELEVEUR DE BOVINS ET PETITS RUMINANTS.pdf"),
    ("Étanchéiste", WAVE_1, "VAGUE1/ETANCHEISTE.pdf"),
    ("Façadier-peintre", WAVE_1, "VAGUE1/Peintre facadier.pdf"),
    ("Informaticien industriel", WAVE_1, "VAGUE1/Informaticien_industriel.pdf"),
    ("Infographe", WAVE_1, "VAGUE1/Infographe.pdf"),
    ("Installateur des systèmes photovoltaïques", WAVE_1, "VAGUE1/Instalateur des sytemes photovoltaiques.pdf"),
    ("Maçon", WAVE_1, "VAGUE1/MACON.pdf"),
    ("Maintenancier des systèmes solaires", WAVE_1, "VAGUE1/Maintenancier des Systemes Solaires.pdf"),
    ("Producteur de céréales", WAVE_1, "VAGUE1/Producteur decereales.pdf"),
    ("Pupitreur", WAVE_1, "VAGUE1/PUPITREUR.pdf"),
    ("Staffeur", WAVE_1, "VAGUE1/STAFFEUR.pdf"),
    ("Transformateur de cacao", WAVE_1, "VAGUE1/Transformateur de CACAO.pdf"),
    ("Transformateur de lait", WAVE_1, "VAGUE1/Transformateur de lait.pdf"),
    # ---- PADESCE, vague 2 -------------------------------------------------
    ("Caissier", WAVE_2, "VAGUE 2/CAISSIER.pdf"),
    ("Coffreur-ferrailleur", WAVE_2, "VAGUE 2/Coffreur ferrailleur.pdf"),
    ("Électricien bâtiment", WAVE_2, "VAGUE 2/Electricien_Batiment.pdf"),
    ("Hydraulicien", WAVE_2, "VAGUE 2/HYDRAULICIEN.pdf"),
    ("Marketeur digital", WAVE_2, "VAGUE 2/Marketeur Digital.pdf"),
    ("Ouvrier de voirie et réseaux divers", WAVE_2, "VAGUE 2/OUVRIER DE VOIRIE ET RESEAUX DIVERS.pdf"),
    ("Ouvrier paysagiste", WAVE_2, "VAGUE 2/Ouvrier Paysagiste.pdf"),
    ("Pentester", WAVE_2, "VAGUE 2/Pentester.pdf"),
    ("Plombier tuyauteur industriel", WAVE_2, "VAGUE 2/Plombier Tuyauteur.pdf"),
    ("Réparateur des machines agricoles", WAVE_2, "VAGUE 2/REPARATEUR DES MACHINES AGRICOLES.pdf"),
    ("Technicien de télésurveillance, alarme et sécurité", WAVE_2, "VAGUE 2/Technicien des systemes des telesurveillances alarmes et securite.pdf"),
    ("Technicien en énergies renouvelables", WAVE_2, "VAGUE 2/Technicien en Energies Renouvelables.pdf"),
    ("Technicien en maintenance éolienne", WAVE_2, "VAGUE 2/Maintenancier Eolien.pdf"),
    ("Technicien en télécommunication", WAVE_2, "VAGUE 2/Technicien Telecommunication.pdf"),
    ("Transformateur de viande", WAVE_2, "VAGUE 2/TRANSFORMATEUR de VIANDE.pdf"),
    # ---- PADESCE, vague 3 -------------------------------------------------
    ("Administrateur des réseaux d'électricité", WAVE_3, "VAGUE 3/Administrateur de reseaux electrique.pdf"),
    ("Agent d'entretien d'espaces verts", WAVE_3, "VAGUE 3/Agent dEntretien dEspaces_Verts.pdf"),
    ("Apiculteur", WAVE_3, "VAGUE 3/Apiculteur.pdf"),
    ("Community manager", WAVE_3, "VAGUE 3/COMMUNITY MANAGER.pdf"),
    ("Constructeur d'ouvrages d'art", WAVE_3, "VAGUE 3/Constructeur dOuvrage dArt.pdf"),
    ("Data analyst", WAVE_3, "VAGUE 3/DATA ANALYST.pdf"),
    ("Domoticien", WAVE_3, "VAGUE 3/DOMOTICIEN.pdf"),
    ("Électricien", WAVE_3, "VAGUE 3/ELECTRICIEN.pdf"),
    ("Installateur des systèmes éoliens", WAVE_3, "VAGUE 3/Instalateur des systemes Eoliens.pdf"),
    ("Maintenancier biomédical", WAVE_3, "VAGUE 3/Maintenancier BIOMEDICAL.pdf"),
    ("Maintenancier des bâtiments", WAVE_3, "VAGUE 3/Maintenancier Batiment.pdf"),
    ("Producteur de boissons", WAVE_3, "VAGUE 3/Producteurs de boisson.pdf"),
    ("Raffineur-producteur des huiles", WAVE_3, "VAGUE 3/RAFFINEUR- PRODUCTEUR des huiles.pdf"),
    ("Serrurier", WAVE_3, "VAGUE 3/SERRURIER.pdf"),
    ("Technicien qualité", WAVE_3, "VAGUE 3/Technicien qualite.pdf"),
    # ---- Coopération allemande (GIZ) --------------------------------------
    ("Agent agro-aménagiste", GIZ, "REFERENTIEL2024/Agent agro aménagiste.pdf"),
    ("Agent d'encadrement agricole", GIZ, "REFERENTIEL2024/Agent d_encadrement agricole.pdf"),
    ("Conseiller agri-finance", GIZ, "REFERENTIEL2024/Conseiller Agri-Finance.pdf"),
    ("Éleveur naisseur des petits ruminants", GIZ, "REFERENTIEL2024/Eleveur naisseur des petits ruminants.pdf"),
    ("Emboucheur des petits ruminants", GIZ, "REFERENTIEL2024/Emboucheur des petits ruminants.pdf"),
    ("Fabricant de compost", GIZ, "REFERENTIEL2024/Fabricant de composte.pdf"),
    ("Guide méthodologique — stratégie genre", GIZ, "REFERENTIEL2024/Guide methodologique stratégie genre.pdf"),
    ("Opérateur (trice) d'engins agricoles", GIZ, "REFERENTIEL2024/Operateur trice dengins agricoles.pdf"),
    ("Opérateur (trice) de traite du lait", GIZ, "REFERENTIEL2024/operateur trice de traite du lait.pdf"),
    ("Ouvrier (ière) polyvalent (e) de ligne de transformation de l'arachide", GIZ, "REFERENTIEL2024/Ouvrier iere polyvalent e de ligne de transformation de larachide.pdf"),
    ("Ouvrier polyvalent de fabrication de produits laitiers", GIZ, "REFERENTIEL2024/Ouvrier polyvalent de fabrication de produits laitiers.pdf"),
    ("Pépiniériste professionnel d'anacardier", GIZ, "REFERENTIEL2024/Pepinieriste professionnel danacardier.pdf"),
    ("Pépiniériste professionnel de manguier", GIZ, "REFERENTIEL2024/Pepinieriste professionnel de manguier.pdf"),
    ("Producteur (trice) d'anacarde", GIZ, "REFERENTIEL2024/Producteur trice danacarde.pdf"),
    ("Producteur (trice) de biofertilisants et biopesticides", GIZ, "REFERENTIEL2024/Producteur _trice_ de biofertilisants - biopesticides.pdf"),
    ("Producteur (trice) des semences d'arachide", GIZ, "REFERENTIEL2024/Producteur trice des semences darachide.pdf"),
    ("Producteur (trice) laitier", GIZ, "REFERENTIEL2024/Producteur trice laitier.pdf"),
    ("Producteur d'arachide", GIZ, "REFERENTIEL2024/Producteur darachide.pdf"),
    ("Tisserand teinturier", GIZ, "REFERENTIEL2024/Tisserand teinturier.pdf"),
    ("Transformateur (trice) artisanal (e) d'arachide", GIZ, "REFERENTIEL2024/Transformateur _trice_ artisanal _e_ d_arachide.pdf"),
    ("Transformateur (trice) artisanal (e) du lait", GIZ, "REFERENTIEL2024/Transformateur trice artisanale du lait.pdf"),
    ("Transformateur professionnel de mangue", GIZ, "REFERENTIEL2024/transformateur Professionnel de mangue.pdf"),
]

# Everything else: (category slug, title, reference label, URL fragment).
OTHER_DOCUMENTS = [
    # ---- Publications et statistiques -------------------------------------
    (
        "publications",
        "Annuaire de la formation professionnelle 2024-2025 (français)",
        "ONEFOP",
        "ANNUAIRE _FORMATION_PROFFESSIONNELE 2024-2025_Francais.pdf",
    ),
    (
        "publications",
        "Vocational training yearbook 2024-2025 (English)",
        "ONEFOP",
        "ANNUAIRE _FORMATION_PROFFESSIONNELE 2024-2025 ENGLISH.pdf",
    ),
    (
        "publications",
        "Rapport d'analyse de l'annuaire statistique de la formation professionnelle 2025",
        "ONEFOP",
        "RAPPORT_DANALYSE_DE LANNUAIRE STAT FOP 2025.pdf",
    ),
    (
        "publications",
        "Regard sur l'emploi 2023-2025",
        "ONEFOP",
        "REGARD SUR LEMPLOI EN  2023-2025.pdf",
    ),
    # ---- Rapports et études ------------------------------------------------
    (
        "rapports",
        "Rapport final de l'étude de suivi de l'insertion des sortants des établissements de formation technique et professionnelle",
        "PADESCE",
        "RAPPORT_PADESCE_V5_114039.pdf",
    ),
    (
        "rapports",
        "Rapport d'analyse ONEFOP",
        "ONEFOP",
        "phocadownload/GOPM/RAPPORT DANALYSE ONEFOP 2-1.pdf",
    ),
    (
        "rapports",
        "Rapport d'analyse ONEFOP de l'étude de suivi post-formation",
        "ONEFOP",
        "phocadownload/GOPM/RAPPORT DANALYSE ONEFOP DE LETUDE DE SUIVI POST FORMATION.pdf",
    ),
    (
        "rapports",
        "Rapport de synthèse ONEFOP — étude de suivi post-formation 2025",
        "ONEFOP",
        "Rapport synthese ONEFOP Etude de suivi post formation 2025.pdf",
    ),
    (
        "rapports",
        "Transmission à l'UCP du rapport de synthèse ONEFOP",
        "ONEFOP",
        "Transmission a lUCP Rapport synthese ONEFOP.pdf",
    ),
    (
        "rapports",
        "Déclaration d'engagement MCDC",
        "MCDC-PADESCE",
        "3-DECLARATION DENGAGEMENT MCDC 1.pdf",
    ),
    (
        "rapports",
        "Procès-verbal de la double session PSOAF — fenêtre 2",
        "MCDC-PADESCE",
        "4-PV DOUBLE SESSION PSOAF F2 1.pdf",
    ),
    (
        "rapports",
        "Procès-verbal de la double session PSOAF — fenêtre 3",
        "MCDC-PADESCE",
        "5-PV DOUBLE SESSION PSOAF F3 1 1.pdf",
    ),
    # ---- Communiqués et appels à candidatures ------------------------------
    (
        "communiques",
        "Communiqué portant avis d'appel à candidatures pour la sélection et la formation des formateurs et personnels des structures de formation professionnelle",
        "",
        "Communique ok.pdf",
    ),
    (
        "communiques",
        "Avis d'appel à candidatures pour la sélection et la formation des formateurs et personnels des structures de formation professionnelle",
        "",
        "APPEL A CANDIDATURES FORMATION DES FORMATEURS ET PERSONNELS DES STRUCTURES DE FORMATION 1.pdf",
    ),
    (
        "communiques",
        "Communiqué portant avis d'appel à candidatures pour la sélection et la formation aux métiers de l'agriculture et de la transformation alimentaire durable",
        "",
        "banners/Communique Radio et Presse  P 19 du 22 -07-2025.pdf - -1.pdf",
    ),
    (
        "communiques",
        "Radio announcement — call for applications for training in sustainable agriculture and food processing",
        "",
        "banners/Communique Radio et Presse  P 19 du 22 -07-2025.pdf - -2.pdf",
    ),
    (
        "communiques",
        "Communiqué portant recrutement d'un administrateur pour le compte du Centre de Formation aux Métiers de Bandjoun",
        "",
        "A communique recrut person gip cfm bandjoun.pdf",
    ),
    (
        "communiques",
        "Communiqué de soumission complète au PSOAF",
        "MCDC-PADESCE",
        "1-FINAL Communique_Pdt_PSOAF_soumission_complete 1.pdf",
    ),
    (
        "communiques",
        "Communiqué de publication des résultats — fenêtre 1",
        "MCDC-PADESCE",
        "Communique publication Resultat F1.pdf",
    ),
    (
        "communiques",
        "Communiqué de publication des résultats — fenêtre 2",
        "MCDC-PADESCE",
        "Communique publication Resultat F2.pdf",
    ),
    (
        "communiques",
        "Communiqué aux entités bénéficiaires — fenêtres 2 et 3",
        "MCDC-PADESCE",
        "Communique aux entites beneficiaires F2 F3.pdf",
    ),
    # ---- Décisions ---------------------------------------------------------
    (
        "decisions",
        "Décision portant publication des résultats de sélection des personnels formateurs",
        "",
        "DECISON PERSONNELS FORMATEURS FR.pdf",
    ),
    (
        "decisions",
        "Decision to publish the results of the selection of training personnel",
        "",
        "DECISION PERSONNELS FORMATEURS ENG.pdf",
    ),
    (
        "decisions",
        "Décision portant publication des résultats de sélection des personnels d'encadrement",
        "",
        "DECISION PERSONNELS ENCADREURS FR.pdf",
    ),
    (
        "decisions",
        "Decision to publish the results of the selection of supervisory personnel",
        "",
        "DECISION PERSONNELS ENCADREURS ENG.pdf",
    ),
    # ---- Formulaires -------------------------------------------------------
    (
        "formulaires",
        "Fiche de candidature — sélection et formation des formateurs et personnels des structures de formation professionnelle",
        "",
        "FICHE DE CANDIDATURE 2.pdf",
    ),
    (
        "formulaires",
        "Fiche de candidature — appel à candidatures pour les métiers de l'agriculture et de la transformation alimentaire durable",
        "",
        "banners/Communique Radio et Presse  P 19 du 22 -07-2025.pdf - -3.pdf",
    ),
    (
        "formulaires",
        "Application form — call for applications for training in sustainable agriculture and food processing",
        "",
        "banners/Communique Radio et Presse  P 19 du 22 -07-2025.pdf - -4.pdf",
    ),
    (
        "formulaires",
        "Fiche de candidature portant avis d'appel à candidatures des formateurs",
        "",
        "Fiche de canditature.pdf",
    ),
    (
        "formulaires",
        "Formulaire de qualification des prestataires de formation (français)",
        "",
        "FRANCAIS FORMULAIRE DE QUALIFICATION DES PRESTATAIRES DE FORMATION.pdf",
    ),
    (
        "formulaires",
        "Qualification form for training providers (English)",
        "",
        "ENGLISH QUALIFICATION FORM FOR TRAINING PROVIDERS.pdf",
    ),
    (
        "formulaires",
        "Formulaire d'accueil des apprentis en entreprise (français)",
        "",
        "vf_FRANCAIS_FORMULAIRE_ENTREPRISE_APPRENTIS.pdf",
    ),
    (
        "formulaires",
        "Request for apprentices form (English)",
        "",
        "ENGLISH_REQUEST_FOR_APPRENTICES_FORM.pdf",
    ),
]
