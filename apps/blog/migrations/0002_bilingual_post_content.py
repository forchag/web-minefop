from django.db import migrations, models


def copy_existing_content_to_both_languages(apps, schema_editor):
    """Best-effort seed: any post created before this migration only had a
    single-language title/excerpt/body. Copy that value into both the French
    and English fields so nothing goes blank; an editor can then translate
    the English side properly."""
    BlogPost = apps.get_model("blog", "BlogPost")
    for post in BlogPost.objects.all():
        post.title_fr = post.title
        post.title_en = post.title
        post.excerpt_fr = post.excerpt
        post.excerpt_en = post.excerpt
        post.body_fr = post.body
        post.body_en = post.body
        post.save(update_fields=["title_fr", "title_en", "excerpt_fr", "excerpt_en", "body_fr", "body_en"])


def copy_french_back_to_single_field(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")
    for post in BlogPost.objects.all():
        post.title = post.title_fr
        post.excerpt = post.excerpt_fr
        post.body = post.body_fr
        post.save(update_fields=["title", "excerpt", "body"])


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="title_fr",
            field=models.CharField(default="", max_length=250, verbose_name="titre (français)"),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="title_en",
            field=models.CharField(default="", max_length=250, verbose_name="titre (anglais)"),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="excerpt_fr",
            field=models.CharField(default="", max_length=300, verbose_name="chapô (français)"),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="excerpt_en",
            field=models.CharField(default="", max_length=300, verbose_name="chapô (anglais)"),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="body_fr",
            field=models.TextField(default="", verbose_name="contenu (français)"),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="body_en",
            field=models.TextField(default="", verbose_name="contenu (anglais)"),
        ),
        migrations.RunPython(
            copy_existing_content_to_both_languages, copy_french_back_to_single_field
        ),
        migrations.RemoveField(model_name="blogpost", name="title"),
        migrations.RemoveField(model_name="blogpost", name="excerpt"),
        migrations.RemoveField(model_name="blogpost", name="body"),
        migrations.AlterField(
            model_name="blogpost",
            name="title_fr",
            field=models.CharField(max_length=250, verbose_name="titre (français)"),
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="title_en",
            field=models.CharField(max_length=250, verbose_name="titre (anglais)"),
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="excerpt_fr",
            field=models.CharField(
                help_text="Court résumé affiché dans la liste des articles.",
                max_length=300,
                verbose_name="chapô (français)",
            ),
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="excerpt_en",
            field=models.CharField(
                help_text="Court résumé affiché dans la liste des articles.",
                max_length=300,
                verbose_name="chapô (anglais)",
            ),
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="body_fr",
            field=models.TextField(verbose_name="contenu (français)"),
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="body_en",
            field=models.TextField(verbose_name="contenu (anglais)"),
        ),
    ]
