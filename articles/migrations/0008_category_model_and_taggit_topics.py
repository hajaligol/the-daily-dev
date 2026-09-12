import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify

import taggit.managers


def populate_category_fk(apps, schema_editor):
    """Turn each Article's free-text `category_name` into a real Category
    row, and point the new `category` foreign key at it. Articles sharing
    the same category text (e.g. two articles both labelled "Mindset")
    are folded onto the same Category row rather than duplicated."""
    Article = apps.get_model("articles", "Article")
    Category = apps.get_model("articles", "Category")

    for article in Article.objects.all():
        name = (article.category_name or "").strip() or "Uncategorized"
        category, _ = Category.objects.get_or_create(
            name=name, defaults={"slug": slugify(name)}
        )
        article.category_id = category.pk
        article.save(update_fields=["category"])


def revert_category_fk(apps, schema_editor):
    """Copy each Article's Category name back into the free-text field so
    the reverse migration can safely drop the `category` FK column."""
    Article = apps.get_model("articles", "Article")
    for article in Article.objects.all():
        if article.category_id:
            article.category_name = article.category.name
            article.save(update_fields=["category_name"])


def populate_tags(apps, schema_editor):
    """Split each Article's legacy comma-separated `topics_legacy` string
    into individual django-taggit tags.

    django-taggit's `TaggableManager.add()` relies on classmethods defined
    on the *real* `TaggedItem`/`Tag` model classes (e.g. `tag_model()`),
    which historical (frozen) migration models don't carry. So the
    tag/through rows are created directly here instead of going through
    the manager API.
    """
    Article = apps.get_model("articles", "Article")
    Tag = apps.get_model("taggit", "Tag")
    TaggedItem = apps.get_model("taggit", "TaggedItem")
    ContentType = apps.get_model("contenttypes", "ContentType")

    article_content_type = ContentType.objects.get_for_model(Article)

    for article in Article.objects.all():
        names = [
            name.strip()
            for name in (article.topics_legacy or "").split(",")
            if name.strip()
        ]
        for name in names:
            tag, _ = Tag.objects.get_or_create(
                name=name, defaults={"slug": slugify(name)}
            )
            TaggedItem.objects.get_or_create(
                tag=tag,
                content_type=article_content_type,
                object_id=article.pk,
            )


def revert_tags(apps, schema_editor):
    """Rebuild the legacy comma-separated `topics_legacy` string from the
    tags attached to each Article, so the reverse migration can safely drop
    the taggit-backed `topics` field."""
    Article = apps.get_model("articles", "Article")
    TaggedItem = apps.get_model("taggit", "TaggedItem")
    ContentType = apps.get_model("contenttypes", "ContentType")

    article_content_type = ContentType.objects.get_for_model(Article)

    for article in Article.objects.all():
        names = list(
            TaggedItem.objects.filter(
                content_type=article_content_type, object_id=article.pk
            ).values_list("tag__name", flat=True)
        )
        article.topics_legacy = ", ".join(names)
        article.save(update_fields=["topics_legacy"])


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("taggit", "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx"),
        ("articles", "0007_remove_article_page_reference"),
    ]

    operations = [
        # --- category: free-text field -> real Category model -----------
        migrations.RenameField(
            model_name="article",
            old_name="category",
            new_name="category_name",
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Section label shown above an article's title, e.g. 'Developer Journal'.", max_length=100, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=120, unique=True)),
            ],
            options={
                "verbose_name": "Category",
                "verbose_name_plural": "Categories",
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="article",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="articles",
                to="articles.category",
                help_text="Section label shown above the title, e.g. 'Developer Journal'.",
            ),
        ),
        migrations.RunPython(populate_category_fk, revert_category_fk),
        migrations.RemoveField(
            model_name="article",
            name="category_name",
        ),
        migrations.AlterField(
            model_name="article",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="articles",
                to="articles.category",
                help_text="Section label shown above the title, e.g. 'Developer Journal'.",
            ),
        ),
        # --- topics: comma-separated string -> django-taggit tags --------
        migrations.RenameField(
            model_name="article",
            old_name="topics",
            new_name="topics_legacy",
        ),
        migrations.AddField(
            model_name="article",
            name="topics",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="Optional topic tags shown in the side column, e.g. 'Mindset, Debugging, Logs, Growth'.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Topics",
            ),
        ),
        migrations.RunPython(populate_tags, revert_tags),
        migrations.RemoveField(
            model_name="article",
            name="topics_legacy",
        ),
    ]
