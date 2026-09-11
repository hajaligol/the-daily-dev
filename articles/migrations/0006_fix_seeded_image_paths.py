from django.db import migrations

# `0002_seed_articles` seeded five of the six launch articles with image
# paths pointing at SVG engravings (e.g. "articles/debugging-engraving.svg")
# that were never actually committed to the repository — they were
# superseded during development by the real illustrations that now live in
# `media/articles/`, but the seed migration itself was never corrected.
#
# The live database was fixed by hand through the admin at some point (its
# `articles_article.image` values already point at the real files), but a
# fresh database built from `migrate` alone would still get the broken SVG
# paths from 0002 and render broken article images everywhere. This
# migration corrects that at the migration-history level so
# "empty database -> migrate -> working application" holds for anyone
# checking out the project from scratch.
#
# Matching is done by (title, old broken path) rather than by title alone,
# so this is a no-op against any database where the image has already been
# repointed to something else (e.g. by an editor uploading a real photo
# through the admin) — it only repairs rows still carrying the original
# stale seed value.

IMAGE_FIXES = [
    (
        "The Day I Learned to Love Debugging",
        "articles/debugging-engraving.svg",
        "articles/ChatGPT_Image_Sep_6_2026_01_40_58_AM_SN99fDA.webp",
    ),
    (
        "Building Scalable Apps the Right Way",
        "articles/architecture-engraving.svg",
        "articles/ChatGPT_Image_Sep_6_2026_09_49_33_PM_IDL165V.webp",
    ),
    (
        "10 Developer Tools That Save Hours",
        "articles/toolbox-engraving.svg",
        "articles/ChatGPT_Image_Sep_6_2026_09_56_08_PM_AVv8y1r.webp",
    ),
    (
        "How to Grow as a Developer (Every Month)",
        "articles/growth-engraving.svg",
        "articles/ChatGPT_Image_Sep_6_2026_09_59_15_PM_3WhN2D5.webp",
    ),
    (
        "Finding Balance in a Hustle Culture",
        "articles/balance-engraving.svg",
        "articles/ChatGPT_Image_Sep_6_2026_10_03_15_PM_pIi52eO.webp",
    ),
    # "CSS Tricks That Make You Look Good" was already seeded correctly in
    # 0002 with "articles/wizard-hat.webp", which does exist — no fix needed.
]


def fix_image_paths(apps, schema_editor):
    Article = apps.get_model("articles", "Article")
    for title, broken_path, correct_path in IMAGE_FIXES:
        Article.objects.filter(title=title, image=broken_path).update(image=correct_path)


def revert_image_paths(apps, schema_editor):
    Article = apps.get_model("articles", "Article")
    for title, broken_path, correct_path in IMAGE_FIXES:
        Article.objects.filter(title=title, image=correct_path).update(image=broken_path)


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0005_rebalance_hero_placement"),
    ]

    operations = [
        migrations.RunPython(fix_image_paths, revert_image_paths),
    ]
