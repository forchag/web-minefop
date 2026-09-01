from django.db import migrations

CURRENT_FRENCH = (
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
    "lors de son discours d'investiture du 6 novembre 2025 selon lesquelles chacun doit "
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

CURRENT_ENGLISH = (
    "Dear fellow citizens,\n\n"
    "A trained engineer and former Secretary of State for Secondary Education, I have "
    "served as Acting Minister at the head of this Department since June 2025, alongside "
    "the Ministry of Youth Affairs and Civic Education. It is a mission I carry out with a "
    "strong sense of duty, in the service of the employability of our fellow Cameroonians.\n\n"
    "Unemployment and underemployment do not strike a single age group: they affect both "
    "the person leaving a training centre and the worker whose trade is changing or "
    "disappearing. That is why our training, retraining and placement schemes are open to "
    "everyone looking for work, changing career or seeking a qualification, with no age "
    "condition — Law n° 2018/010 of 11 July 2018 guarantees equal access to training, in "
    "both official languages, to anyone who meets the required conditions.\n\n"
    "In line with the direction set by the Head of State, His Excellency Paul BIYA, in his "
    "inaugural address of 6 November 2025 — that everyone should be able to learn a trade, "
    "find a job or start their own activity wherever they live — the Ministry launched the "
    "« Un Jeune, un Métier, un Emploi » (JEME) programme on 19 November 2025, completing a "
    "national scheme covering rural, peri-urban and urban areas.\n\n"
    "This ambition rests on the continuous modernisation of our system: the Inserjeune "
    "digital platform, which tracks more than 15,000 graduates of vocational training; the "
    "D-CLIC project run with the International Organisation of La Francophonie to train "
    "people in digital trades; work-linked training carried by FORMPRO 237; and the "
    "strengthening of our trainers' pedagogical skills through the National Centre for "
    "Trainer Training and Curriculum Development (CNFFDP).\n\n"
    "This site is intended as a transparent source of information on our missions, our "
    "organisation, our training centres, our occupational standards and the texts that "
    "govern our work. I wish you a pleasant visit."
)

# A phrase present in every known past wording of the ministry's standard
# message (with or without the budget figures / youth-restricted phrasing
# used before that content was revised) — used to recognise it's still the
# stock message and not something an editor has since written from scratch.
SIGNATURE = "Un Jeune, un Métier, un Emploi"


def retranslate_if_stale(apps, schema_editor):
    """0009 only replaced message_en when message_fr matched one exact known
    string. On a database seeded before that string existed (e.g. still
    carrying the old budget-figures wording), the guard silently didn't
    fire, so message_en stayed equal to message_fr and the English page kept
    showing French. Catch any such row here: whenever message_en still
    equals message_fr and it's recognisably the ministry's standard message,
    replace both fields with the current, correct bilingual text — this also
    picks up any pre-existing wording that predates the later French
    content revision."""
    MinisterMessage = apps.get_model("core", "MinisterMessage")
    for message in MinisterMessage.objects.all():
        if message.message_en == message.message_fr and SIGNATURE in message.message_fr:
            message.message_fr = CURRENT_FRENCH
            message.message_en = CURRENT_ENGLISH
            message.save(update_fields=["message_fr", "message_en"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_translate_minister_message"),
    ]

    operations = [
        migrations.RunPython(retranslate_if_stale, migrations.RunPython.noop),
    ]
