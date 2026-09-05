from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0002_seed_articles"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="content",
            field=models.TextField(
                blank=True,
                default="",
                help_text=(
                    "Full article body shown on the detail page. Written as "
                    "simple HTML (<p>, <h2 class=\"article-section-title\">, "
                    "<blockquote class=\"article-pullquote\">, <ul>) and "
                    "rendered as-is, the way a newsroom CMS body field "
                    "would be. Include the token "
                    "'[[HERO_IMAGE:caption text]]' once, at the point where "
                    "the article's own image should appear."
                ),
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="topics",
            field=models.CharField(
                blank=True,
                default="",
                max_length=255,
                help_text=(
                    "Optional comma-separated topic tags shown in the side "
                    "column, e.g. 'Mindset, Debugging, Logs, Growth'."
                ),
            ),
        ),
    ]
