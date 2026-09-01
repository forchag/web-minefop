from django.db import migrations, models


def copy_existing_message_to_both_languages(apps, schema_editor):
    """Best-effort seed: the Minister's message only had a single-language
    body before. Copy it into both the French and English fields so nothing
    goes blank; an editor can then translate the English side properly."""
    MinisterMessage = apps.get_model("core", "MinisterMessage")
    for entry in MinisterMessage.objects.all():
        entry.message_fr = entry.message
        entry.message_en = entry.message
        entry.save(update_fields=["message_fr", "message_en"])


def copy_french_back_to_single_field(apps, schema_editor):
    MinisterMessage = apps.get_model("core", "MinisterMessage")
    for entry in MinisterMessage.objects.all():
        entry.message = entry.message_fr
        entry.save(update_fields=["message"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_replace_budget_key_figure"),
    ]

    operations = [
        migrations.AddField(
            model_name="ministermessage",
            name="message_fr",
            field=models.TextField(default="", verbose_name="mot du ministre (français)"),
        ),
        migrations.AddField(
            model_name="ministermessage",
            name="message_en",
            field=models.TextField(default="", blank=True, verbose_name="mot du ministre (anglais)"),
        ),
        migrations.RunPython(
            copy_existing_message_to_both_languages, copy_french_back_to_single_field
        ),
        migrations.RemoveField(model_name="ministermessage", name="message"),
        migrations.AlterField(
            model_name="ministermessage",
            name="message_fr",
            field=models.TextField(verbose_name="mot du ministre (français)"),
        ),
        migrations.AlterField(
            model_name="ministermessage",
            name="message_en",
            field=models.TextField(blank=True, verbose_name="mot du ministre (anglais)"),
        ),
    ]
