from django.db import migrations

NEW_FRENCH_MESSAGE = (
    "Chères concitoyennes, chers concitoyens,\n\n"
    "Le Chef de l'État, Son Excellence Paul Biya, Président de la République, n'a de "
    "cesse de rappeler que l'emploi et la formation professionnelle de la jeunesse "
    "camerounaise constituent une priorité nationale. C'est dans cet esprit que le "
    "Ministère de l'Emploi et de la Formation Professionnelle conduit son action, au "
    "service de chaque Camerounaise et de chaque Camerounais, à toutes les étapes de "
    "son parcours professionnel.\n\n"
    "Notre ambition se décline en cinq axes indissociables : l'orientation, pour aider "
    "chacun à découvrir un métier porteur ; la formation, pour offrir des compétences "
    "reconnues et adaptées aux besoins de l'économie ; l'insertion, pour accompagner le "
    "passage de la formation à la vie active ; l'emploi, pour ouvrir l'accès au marché "
    "du travail ; et l'entrepreneuriat, pour soutenir celles et ceux qui choisissent de "
    "créer leur propre activité. Nous résumons cette ambition en une formule simple : "
    "« former, insérer, employer : notre engagement pour chaque Camerounais ».\n\n"
    "Cet engagement se traduit par des actions concrètes : le rapprochement de nos "
    "services des populations à travers nos délégations régionales et départementales, "
    "l'agrément et le suivi des centres de formation publics et privés, la "
    "simplification des démarches administratives et la modernisation continue de nos "
    "outils d'information et d'orientation.\n\n"
    "Nous voulons placer l'usager au centre de nos préoccupations. C'est pourquoi ce "
    "site a été conçu comme un espace d'information transparent et accessible sur nos "
    "missions, notre organisation, nos centres de formation, nos référentiels de "
    "métiers et les textes qui encadrent notre action. Chacune et chacun peut également "
    "nous faire part de ses observations à travers notre formulaire de contact, afin "
    "que nous puissions améliorer continuellement la qualité de nos services.\n\n"
    "C'est avec cette conviction que je vous souhaite une excellente navigation sur ce "
    "site, au service de tous les Camerounais."
)

NEW_ENGLISH_MESSAGE = (
    "Dear fellow citizens,\n\n"
    "The Head of State, His Excellency Paul Biya, President of the Republic, "
    "constantly reminds us that the employment and vocational training of Cameroonian "
    "youth are a national priority. It is in this spirit that the Ministry of "
    "Employment and Vocational Training carries out its work, in the service of every "
    "Cameroonian, at every stage of their professional journey.\n\n"
    "Our ambition rests on five inseparable pillars: orientation, to help everyone "
    "discover a promising trade; training, to provide recognised skills suited to the "
    "needs of the economy; integration, to support the passage from training into "
    "working life; employment, to open access to the labour market; and "
    "entrepreneurship, to support those who choose to start their own business. We sum "
    "up this ambition in a simple phrase: \"train, integrate, employ: our commitment to "
    "every Cameroonian\".\n\n"
    "This commitment translates into concrete action: bringing our services closer to "
    "the population through our regional and departmental delegations, approving and "
    "monitoring public and private training centres, simplifying administrative "
    "procedures and continuously modernising our information and guidance tools.\n\n"
    "We want to place the user at the centre of our concerns. That is why this site was "
    "designed as a transparent and accessible source of information on our missions, "
    "our organisation, our training centres, our occupational standards and the texts "
    "that govern our work. Everyone is also welcome to share their observations through "
    "our contact form, so that we can continuously improve the quality of our "
    "services.\n\n"
    "It is with this conviction that I wish you an excellent visit to this site, in the "
    "service of all Cameroonians."
)


def rewrite_message(apps, schema_editor):
    """Requested style rewrite, modelled on the register of real Cameroonian
    ministerial addresses (e.g. MINFOPRA's "L'usager est roi" and MINSEP's
    New Year message): a presidential-priority framing, a quotable
    programme phrase, and concrete citizen-facing commitments, while
    staying generic (no biography, no dated history) and free of em
    dashes. Applied unconditionally since this is a direct content edit."""
    MinisterMessage = apps.get_model("core", "MinisterMessage")
    MinisterMessage.objects.update(message_fr=NEW_FRENCH_MESSAGE, message_en=NEW_ENGLISH_MESSAGE)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_humanize_minister_message"),
    ]

    operations = [
        migrations.RunPython(rewrite_message, migrations.RunPython.noop),
    ]
