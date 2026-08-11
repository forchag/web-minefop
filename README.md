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
- **Typographie** : Inter (interface) et Source Serif 4 (titres institutionnels),
  auto-hébergées dans `static/fonts/` sous licence SIL OFL
- **Aucun CDN** : Bootstrap, les icônes et les polices sont servis depuis le
  domaine du Ministère ; le site n'émet aucune requête vers un tiers
- **i18n** : bilingue français / anglais via le framework de traduction Django
  (`{% trans %}` / `{% blocktrans %}`), URLs préfixées `/fr/` et `/en/`

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

Le site est servi sous `/fr/` et `/en/` (redirection automatique depuis `/`).
L'administration Django (`/admin/`) permet de gérer tout le contenu : actualités,
documents, centres de formation, délégations, mot du ministre, etc.

### Tests

```bash
python manage.py test
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

## Contenu à personnaliser

Les données injectées par `seed_data` (centres de formation, délégations,
actualités, mot du ministre) sont à compléter avec le registre officiel complet
du Ministère via l'espace d'administration. Les documents légaux (lois et
décrets) sont en revanche les textes officiels réels.
