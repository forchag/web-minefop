from django.db import migrations

NEW_FRENCH_MESSAGE = (
    "Chères concitoyennes, chers concitoyens,\n\n"
    "C'est avec un profond sens du devoir que je m'adresse à vous en tant que Ministre "
    "de l'Emploi et de la Formation Professionnelle.\n\n"
    "Notre département ministériel a pour mission d'accompagner chaque Camerounais dans "
    "son parcours professionnel, de l'orientation vers un métier à la formation "
    "qualifiante, en passant par l'insertion dans la vie active, l'accès à l'emploi et "
    "l'appui à l'entrepreneuriat. Ces cinq axes, orientation, formation, insertion, "
    "emploi et entrepreneuriat, guident au quotidien l'action de nos services centraux "
    "et déconcentrés, sur l'ensemble du territoire national.\n\n"
    "Cette action s'inscrit pleinement dans les priorités fixées par Son Excellence Paul "
    "Biya, Président de la République, pour qui l'emploi et la formation professionnelle "
    "de la jeunesse camerounaise constituent une priorité nationale. Nous œuvrons, avec "
    "détermination, à donner à chaque citoyen les moyens d'apprendre un métier, de se "
    "qualifier et de trouver sa place dans le monde du travail, qu'il s'agisse d'un "
    "salarié, d'un travailleur en reconversion ou d'un entrepreneur.\n\n"
    "Ce site se veut un espace d'information transparent sur nos missions, notre "
    "organisation, nos centres de formation, nos référentiels de métiers et les textes qui "
    "encadrent notre action. Je vous souhaite une excellente navigation."
)

NEW_ENGLISH_MESSAGE = (
    "Dear fellow citizens,\n\n"
    "It is with a deep sense of duty that I address you as Minister of Employment and "
    "Vocational Training.\n\n"
    "Our Ministry's mission is to support every Cameroonian throughout their working "
    "life, from guidance towards a trade to qualifying training, through integration "
    "into working life, access to employment and support for entrepreneurship. These "
    "five pillars, orientation, training, integration, employment and entrepreneurship, "
    "guide the daily work of our central and decentralised services across the whole "
    "country.\n\n"
    "This work is fully in line with the priorities set by His Excellency Paul Biya, "
    "President of the Republic, for whom the employment and vocational training of "
    "Cameroonian youth are a national priority. We work with determination to give "
    "every citizen the means to learn a trade, gain a qualification and find their "
    "place in the world of work, whether as an employee, someone retraining or an "
    "entrepreneur.\n\n"
    "This site is intended as a transparent source of information on our missions, our "
    "organisation, our training centres, our occupational standards and the texts that "
    "govern our work. I wish you a pleasant visit."
)


def humanize_message(apps, schema_editor):
    """Requested rewrite: drop the minister's personal biography and dated
    history, keep the message generic and mission-focused (so it doesn't go
    stale across a change of minister), fold in the five pillars, and note
    that this is one of the President's priorities. Applied unconditionally
    since this is a direct content edit, not a data-integrity backfill."""
    MinisterMessage = apps.get_model("core", "MinisterMessage")
    MinisterMessage.objects.update(message_fr=NEW_FRENCH_MESSAGE, message_en=NEW_ENGLISH_MESSAGE)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_retranslate_stale_minister_message"),
    ]

    operations = [
        migrations.RunPython(humanize_message, migrations.RunPython.noop),
    ]
