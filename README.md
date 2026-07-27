# MINEFOP — Site officiel

Site institutionnel du Ministère de l'Emploi et de la Formation Professionnelle
(MINEFOP) du Cameroun, développé avec Django.

## Stack

- **Backend** : Django 5, apps `core`, `news`, `documents`, `structures`, `contact`
- **Templates** : tous regroupés dans un unique dossier `templates/` (organisé en
  sous-dossiers par page, `APP_DIRS` désactivé au profit de `DIRS`)
- **CSS** : mélange Bootstrap 5 (composants) + Tailwind CSS (utilitaires, préflight
  désactivé) + `static/css/custom.css` (charte MINEFOP), tout vendorisé localement
  via npm — aucune dépendance à un CDN en production
- **i18n** : bilingue français / anglais via le framework de traduction Django
  (`{% trans %}` / `{% blocktrans %}`), URLs préfixées `/fr/` et `/en/`

## Démarrage rapide

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

npm install
npm run build:css        # compile static/css/tailwind-built.css

python manage.py migrate
python manage.py seed_data       # organigramme, régions, centres, textes légaux, actus
python manage.py createsuperuser
python manage.py runserver
```

Le site est servi sous `/fr/` et `/en/` (redirection automatique depuis `/`).
L'administration Django (`/admin/`) permet de gérer tout le contenu : actualités,
documents, centres de formation, délégations, mot du ministre, etc.

## Traductions

```bash
python manage.py makemessages -l en
# éditer locale/en/LC_MESSAGES/django.po
python manage.py compilemessages
```

## Contenu à personnaliser

Les données injectées par `seed_data` (centres de formation, délégations,
actualités, mot du ministre) sont des exemples illustratifs à remplacer par les
informations officielles du Ministère via l'espace d'administration. Les
documents légaux (lois et décrets) sont en revanche les textes officiels réels.
