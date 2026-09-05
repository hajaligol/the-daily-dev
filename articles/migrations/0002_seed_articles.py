from django.db import migrations
from django.utils.text import slugify


ARTICLES = [
    {
        "order": 1,
        "category": "Developer Journal",
        "title": "The Day I Learned to Love Debugging",
        "excerpt": (
            "What started as hours of frustration turned into a lesson "
            "in patience, persistence, and logs that never lie."
        ),
        "image": "articles/debugging-engraving.svg",
        "image_alt": (
            "Vintage engraved illustration of a magnifying glass "
            "inspecting a bug on a laptop screen beside a steaming mug"
        ),
        "page_reference": 7,
    },
    {
        "order": 2,
        "category": "Code Architecture",
        "title": "Building Scalable Apps the Right Way",
        "excerpt": (
            "Good architecture doesn\u2019t happen by accident. Here\u2019s "
            "a practical approach that scales with you."
        ),
        "image": "articles/architecture-engraving.svg",
        "image_alt": (
            "Vintage engraved illustration of stacked building "
            "blocks assembled into a pyramid, flanked by tiny figures"
        ),
        "page_reference": 11,
    },
    {
        "order": 3,
        "category": "Tools We Love",
        "title": "10 Developer Tools That Save Hours",
        "excerpt": (
            "A handpicked list of tools that make coding, testing, and "
            "deploying a whole lot smoother."
        ),
        "image": "articles/toolbox-engraving.svg",
        "image_alt": (
            "Vintage engraved illustration of a wooden toolbox "
            "labelled Dev Tools with a wrench and screwdriver crossed on top"
        ),
        "page_reference": 15,
    },
    {
        "order": 4,
        "category": "Frontend Magic",
        "title": "CSS Tricks That Make You Look Good",
        "excerpt": (
            "Simple but powerful CSS techniques that can instantly "
            "level up your UI game."
        ),
        "image": "articles/wizard-hat.webp",
        "image_alt": (
            "Vintage engraved illustration of a wizard\u2019s hat, "
            "conjuring a little stylistic magic"
        ),
        "page_reference": 19,
    },
    {
        "order": 5,
        "category": "Career Code",
        "title": "How to Grow as a Developer (Every Month)",
        "excerpt": (
            "Small, consistent steps that lead to massive growth in "
            "your development career over time."
        ),
        "image": "articles/growth-engraving.svg",
        "image_alt": (
            "Vintage engraved illustration of a seedling sprouting "
            "from a stack of books labelled Build, Ship, and Repeat"
        ),
        "page_reference": 23,
    },
    {
        "order": 6,
        "category": "Beyond Code",
        "title": "Finding Balance in a Hustle Culture",
        "excerpt": (
            "Productivity is important. But so is your peace of mind. "
            "Let\u2019s talk about balance."
        ),
        "image": "articles/balance-engraving.svg",
        "image_alt": (
            "Vintage engraved illustration of a balance scale "
            "weighing a laptop against a small potted plant"
        ),
        "page_reference": 27,
    },
]


def seed_articles(apps, schema_editor):
    Article = apps.get_model("articles", "Article")
    for data in ARTICLES:
        data = {**data, "slug": slugify(data["title"])}
        Article.objects.get_or_create(title=data["title"], defaults=data)


def remove_articles(apps, schema_editor):
    Article = apps.get_model("articles", "Article")
    Article.objects.filter(
        title__in=[data["title"] for data in ARTICLES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_articles, remove_articles),
    ]
