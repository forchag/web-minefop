# MINEFOP — Site officiel

Site institutionnel du Ministère de l'Emploi et de la Formation Professionnelle
(MINEFOP) de la République du Cameroun, développé avec Django.

## Stack

- **Backend** : Django 5, apps `core`, `news`, `documents`, `structures`, `contact`
- **Templates** : tous regroupés dans un unique dossier `templates/` (organisé en
  sous-dossiers par page)
- **CSS** : Bootstrap 5 pour la grille et les composants, complété par
  `static/css/custom.css` — le système de design institutionnel du Ministère
  (tokens de couleur, masthead, navigation, cartes, états de focus, styles
  d'impression)
- **Typographie** : Inter (interface) et Source Serif 4 (titres institutionnels)
  pour le site, Poppins et Source Sans 3 pour le portail d'entrée — toutes
  auto-hébergées dans `static/fonts/` sous licence SIL OFL
- **Aucun CDN** : Bootstrap, les icônes et les polices sont servis depuis le
  domaine du Ministère ; le site n'émet aucune requête vers un tiers
- **i18n** : bilingue français / anglais via le framework de traduction Django
  (`{% trans %}` / `{% blocktrans %}`), URLs préfixées `/fr/` et `/en/`
- **Portail d'entrée** : la racine du domaine (`/`) sert une page bilingue
  autonome (`templates/core/portal.html`) qui ouvre les deux versions du site et
  publie l'annuaire des sites institutionnels, partenaires et services en ligne

## Démarrage rapide

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data       # organigramme, régions, centres, textes légaux, actus
python manage.py compilemessages # génère locale/en/LC_MESSAGES/django.mo
python manage.py createsuperuser
python manage.py runserver
```

La racine `/` affiche le portail d'entrée bilingue ; le site lui-même est servi
sous `/fr/` et `/en/`. L'administration Django (`/admin/`) permet de gérer tout le
contenu : actualités, documents, centres de formation, délégations, mot du
ministre, organismes et programmes, sites partenaires du portail, etc.

## Portail d'entrée et sites partenaires

La page servie à la racine du domaine reprend la charte du portail du
Ministère : une carte blanche posée sur le dégradé national, encadrée de deux
colonnes de vignettes d'institutions, avec au centre les deux portes vers les
versions française et anglaise du site.

Elle est alimentée par le modèle **Sites partenaires**
(`apps.core.models.PartnerSite`), organisé en trois rubriques : *institutions de
la République*, *organismes, projets et partenaires*, *services et plateformes
en ligne*. Les entrées actives sont réparties à parts égales entre les deux
colonnes, dans l'ordre des rubriques. Une entrée sans adresse de site reste
affichée, sans lien, avec la mention « Site en cours de publication ».

Chaque entrée porte sa **colonne** (gauche ou droite), son **rang** dans
celle-ci et la **couleur du bandeau** qui affiche le nom au survol de la
vignette — la place et la teinte de chaque vignette relèvent donc de
l'administration, pas du gabarit.

Pour le logo, l'ordre est : le fichier téléversé depuis l'administration
d'abord, puis l'**adresse du logo** fournie par la structure, et à défaut le
sigle sur le fond tricolore. Si l'adresse fournie cesse de répondre, la vignette
bascule elle aussi sur le sigle plutôt que d'afficher une image cassée.

Pour ne plus dépendre des serveurs des structures, la commande suivante
télécharge les logos une fois et les héberge sur le domaine du Ministère :

```bash
python manage.py fetch_partner_logos            # récupère ce qui manque
python manage.py fetch_partner_logos --dry-run  # liste sans rien modifier
python manage.py fetch_partner_logos --force    # retélécharge tout
```

Hormis ces logos, aucune police et aucun script n'est jamais chargé depuis un
tiers : le champ de particules et les portes coulissantes sont écrits à la main
dans `static/js/portal.js`, sans particles.js, jQuery ni GSAP. Le tout reste une
amélioration progressive : sans JavaScript, ou lorsque le visiteur demande un
mouvement réduit, les deux boutons restent de simples liens.

### Tests

```bash
python manage.py test
```

## Mettre à jour un déploiement

`scripts/update.sh` enchaîne toutes les étapes d'une mise à jour du serveur :
récupération du code depuis GitHub, installation des dépendances, exécution de
la suite de tests, application des migrations, compilation des traductions et
collecte des fichiers statiques, puis rechargement du service web.

```bash
./scripts/update.sh                       # met à jour la branche courante
./scripts/update.sh --branch main         # bascule sur main et la met à jour
./scripts/update.sh --check               # simulation : affiche sans exécuter
MINEFOP_SERVICE=minefop.service ./scripts/update.sh   # recharge le service
```

Le script s'arrête à la première erreur : tant qu'il n'est pas allé au bout, le
site continue de servir la version précédente. Les tests s'exécutent **avant**
la base de données et les fichiers publiés, de sorte qu'un dépôt cassé
n'atteigne jamais les visiteurs. Il refuse également d'avancer si la copie de
travail du serveur contient des modifications non validées, et ne crée jamais de
commit de fusion (`git merge --ff-only`).

Options utiles : `--no-pull` (reconstruire sans récupérer de code), `--no-deps`,
`--no-tests`, `--vendor` (régénérer `static/vendor/` avec npm), `--seed`
(injecter le contenu initial, sans jamais écraser l'existant). `./scripts/update.sh --help`
liste l'ensemble.

Le script retrouve l'environnement virtuel dans cet ordre : la variable
`MINEFOP_VENV` (pour un environnement situé hors du dépôt), l'environnement déjà
activé dans le shell appelant (`VIRTUAL_ENV`), puis `venv/`, `.venv/` ou `env/`
dans le dépôt. À défaut il utilise le Python du système et le signale — utile à
savoir lorsque le script est lancé depuis cron ou un hook de déploiement, sans
profil de shell derrière lui.

```bash
MINEFOP_VENV=/opt/minefop/venv ./scripts/update.sh
```

## Charte et identité de l'État

Les armoiries de la République et le logotype MINEFOP sont dans `static/img/` :

| Fichier | Usage |
| --- | --- |
| `minefop-emblem.png` | Armoiries seules — masthead, pied de page, page 500 |
| `minefop-logo.png` | Logotype complet (armoiries + « MINEFOP ») — hero, partages |
| `favicon-32.png`, `favicon-180.png`, `minefop-icon-512.png` | Icônes de navigateur |
| `minister-portrait.jpg`, `minister-square.jpg`, `minister-office.jpg` | Photographies officielles du Ministre |

Les photographies du Ministre servent de valeurs par défaut : dès qu'une photo
est téléversée dans **Mot du ministre** via l'espace d'administration, c'est
elle qui s'affiche.

## Dépendances front-end

Bootstrap et Bootstrap Icons sont vendorisés dans `static/vendor/` et versionnés
avec le projet — aucune étape de build n'est nécessaire pour servir le site.
Pour mettre à jour ces bibliothèques :

```bash
npm install          # installe les versions déclarées dans package.json
npm run vendor       # recopie les fichiers distribuables dans static/vendor/
```

## Traductions

```bash
python manage.py makemessages -l en --no-location --no-wrap
# éditer locale/en/LC_MESSAGES/django.po
python manage.py compilemessages
```

## Référencement et accessibilité

- `/sitemap.xml` (pages institutionnelles, actualités, centres de formation) et
  `/robots.txt` sont générés par l'application, hors préfixe de langue
- Chaque page déclare ses alternatives linguistiques (`hreflang`), ses métadonnées
  de partage (Open Graph) et une fiche `GovernmentOrganization` en JSON-LD
- Les pages « Mentions légales », « Déclaration d'accessibilité » et
  « Plan du site » sont accessibles depuis le pied de page

## Fonds documentaire repris de l'ancien site

Le catalogue des documents publiés sur le site précédent (référentiels de
formation des quatre générations PADESCE, référentiels homologués avec l'appui de
la coopération allemande, annuaires et rapports de l'ONEFOP, décisions,
communiqués, appels à candidatures et formulaires) est décrit dans
`apps/documents/legacy_library.py` et injecté par `seed_data`.

Ces fichiers PDF restent hébergés à leur adresse d'origine : le modèle
`Document` porte pour cela un champ `source_url` en plus de son champ `file`.
La propriété `Document.download_url` sert le fichier téléversé lorsqu'il existe,
et retombe sinon sur `source_url` — il suffit donc de téléverser un document
dans l'administration pour que le site cesse de pointer vers l'ancien domaine.

## Contenu à personnaliser

Les données injectées par `seed_data` (centres de formation, délégations,
actualités, mot du ministre, sites partenaires) sont à compléter avec le registre
officiel complet du Ministère via l'espace d'administration. Les documents
légaux (lois et décrets) sont en revanche les textes officiels réels.
