from django.db import migrations

# Full article bodies for the detail page, keyed by the article's title so
# this migration can find the rows seeded in 0002_seed_articles without
# guessing at IDs. Each body is plain HTML (<p>, <h2>, <blockquote>, <ul>)
# and contains exactly one '[[HERO_IMAGE:...]]' token marking where the
# article's own (already-existing) image should be rendered.

DEBUGGING_CONTENT = """
<p class="has-dropcap"><span class="article-dropcap">I</span>t started like any
other night. The code compiled without complaint. The test suite blinked
green, calm as ever. And then, somewhere between &ldquo;it works on my
machine&rdquo; and the review queue, everything came apart at the seams.</p>

<p>I stared at the error message the way you stare at a locked door you're
certain you have the key for. It offered no explanation. It never does.</p>

<p>Hours passed. Print statements multiplied like rabbits. I was tired,
mildly offended, and quietly convinced that debugging was some kind of
professional hazing ritual nobody warns you about at orientation.</p>

<p>But somewhere in that fog of console output, something shifted.</p>

[[HERO_IMAGE:The author at work, somewhere between the bug and the breakthrough.]]

<h2 class="article-section-title">1. The Breaking Point</h2>

<p>There was a moment I nearly gave up &mdash; not on the bug, but on myself.
I remember thinking that maybe I wasn't cut out for this, that everyone else
simply &ldquo;got it&rdquo; while I sat chasing ghosts through someone else's
function names.</p>

<p>Walking away didn't feel right, so instead I took a breath, closed the
editor, stepped outside, and came back with a different question entirely:
<em>what is this code actually trying to tell me?</em></p>

<h2 class="article-section-title">2. A New Perspective</h2>

<p>I stopped trying to defeat the bug and started trying to understand it. I
read the code out loud. I traced the flow line by line. I wrote down what I
expected to happen, then what actually happened, and let the gap between the
two do the talking.</p>

<p>Patterns began to emerge &mdash; not just in the bug itself, but in the way
I had been thinking about it all along. It was never really about being
perfect. It was about being curious enough to ask better questions.</p>

<blockquote class="article-pullquote">&ldquo;Debugging isn't about finding
mistakes. It's about <strong>understanding</strong> the story your code is
trying to tell you.&rdquo;</blockquote>

<h2 class="article-section-title">3. The Power of Logs</h2>

<p>Logs became my closest collaborator that week. Not just error logs, but
meaningful ones &mdash; logs that told a story, that answered questions
before I'd even finished asking them.</p>

<p>A well-placed <code>console.log()</code> turned out to be less a debugging
crutch and more a flashlight in a very dark forest. The more I logged with
intention, the clearer the path became, one small clue at a time.</p>

<h2 class="article-section-title">4. What I Do Differently Now</h2>

<p>Over time, that one long night became a routine that now saves me hours
whenever things go sideways:</p>

<ul>
<li>Reproduce the issue consistently before touching anything.</li>
<li>Read the code like a stranger would, assuming nothing.</li>
<li>Log with intention, not just in a panic.</li>
<li>Isolate the problem before reaching for a fix.</li>
<li>Fix the root cause, not just the symptom on the surface.</li>
</ul>

<p>None of it is magic. It's discipline &mdash; and discipline, it turns out,
is what quietly turns panic into progress.</p>

<h2 class="article-section-title">5. Lessons Learned</h2>

<p>Debugging taught me more about the craft than writing new features ever
has. A short list of what stuck:</p>

<ul>
<li>Patience is a genuine superpower.</li>
<li>Most bugs are really assumptions wearing a disguise.</li>
<li>Every bug has a backstory worth listening to.</li>
<li>Growth tends to live just on the other side of frustration.</li>
</ul>

<p>These days, when a bug appears, I don't groan. I smile, because I already
know &mdash; it's just another lesson, patiently waiting to be learned.</p>
""".strip()

ARCHITECTURE_CONTENT = """
<p class="has-dropcap"><span class="article-dropcap">G</span>ood architecture
rarely announces itself. It doesn't demand attention on day one &mdash; it
simply refuses to fall apart on day one thousand, long after the original
authors have moved on to other projects entirely.</p>

<p>Most teams don't set out to build something fragile. Fragility creeps in
quietly, one shortcut at a time, until a single schema change requires
touching fourteen files nobody remembers writing.</p>

[[HERO_IMAGE:Blueprints for a system built to outlast its first version.]]

<h2 class="article-section-title">Start With Boundaries, Not Frameworks</h2>

<p>Before choosing a framework, choose your boundaries. Decide what a module
is allowed to know about its neighbours, and just as importantly, what it
isn't. Boundaries drawn early are cheap. Boundaries drawn after the fact are
a renovation project.</p>

<p>A scalable system isn't one that never changes &mdash; it's one where
change stays contained to the part that needed it.</p>

<h2 class="article-section-title">Design for the Team You Have</h2>

<p>Clever architecture that only its author understands isn't scalable, no
matter how elegant it looks in a diagram. The most durable systems tend to
favour boring, well-labelled structure over cleverness &mdash; because six
months from now, &ldquo;boring&rdquo; is what lets a new hire ship a fix by
lunchtime.</p>

<p>A few habits worth keeping close:</p>

<ul>
<li>Name things for what they do, not how they're implemented.</li>
<li>Keep the data model honest about what the business actually needs.</li>
<li>Write the integration test before the elegant abstraction.</li>
<li>Leave a trail &mdash; comments, docs, decisions &mdash; for whoever
inherits this next.</li>
</ul>

<p>Scale, in the end, isn't a server count. It's how gracefully a system
accepts the next unexpected requirement.</p>
""".strip()

TOOLBOX_CONTENT = """
<p class="has-dropcap"><span class="article-dropcap">E</span>very developer
eventually assembles a small, personal toolkit &mdash; a handful of programs
and habits that quietly save hours nobody ever notices were saved.</p>

<p>These are rarely the flashiest tools in the room. They're the reliable
ones: the terminal shortcut, the linter that catches the typo before code
review, the tiny script that used to be a fifteen-minute chore.</p>

[[HERO_IMAGE:The humble toolbox behind every calm deployment.]]

<h2 class="article-section-title">The Tools Worth the Setup Time</h2>

<p>A good formatter that runs on save. A linter configured once and
forgotten. A snippet manager that remembers the boilerplate so your memory
doesn't have to. None of these are exciting purchases &mdash; all of them pay
for themselves within a week.</p>

<ul>
<li>An editor you've actually configured, not just installed.</li>
<li>A terminal multiplexer for the projects that need three panes at once.</li>
<li>A diff tool that makes a two-hundred-line change legible.</li>
<li>A task runner that remembers the command so you don't have to.</li>
</ul>

<h2 class="article-section-title">The Real Time Savings Are Boring</h2>

<p>The biggest hours saved rarely come from a single dazzling tool &mdash;
they come from removing friction, one small annoyance at a time, until the
workday finally feels like it belongs to you again.</p>

<p>Choose tools the way you'd choose colleagues: for reliability, not
charisma.</p>
""".strip()

CSS_CONTENT = """
<p class="has-dropcap"><span class="article-dropcap">C</span>SS has a
reputation problem. Ask around and you'll hear it called finicky,
unpredictable, occasionally cursed. And yet, in the right hands, it remains
one of the most quietly powerful tools in the entire stack.</p>

<p>The difference between a page that merely functions and one that feels
considered often comes down to a handful of small, deliberate decisions.</p>

[[HERO_IMAGE:A little stylistic magic, conjured from nothing but a stylesheet.]]

<h2 class="article-section-title">Spacing Is the Trick Nobody Talks About</h2>

<p>Consistent spacing does more visual work than almost any other single
decision. A tidy rhythm of margins and padding reads as intentional even when
nothing else on the page is particularly clever.</p>

<h2 class="article-section-title">A Few Reliable Favourites</h2>

<ul>
<li>Let <code>clamp()</code> handle responsive type instead of a dozen media
queries.</li>
<li>Reach for <code>gap</code> before reaching for more margin.</li>
<li>Use real contrast, not just a slightly darker grey.</li>
<li>Trust <code>flex</code> and <code>grid</code> before reaching for
anything more exotic.</li>
</ul>

<p>With the right flex, you can move mountains. With <code>position:
absolute</code> used carelessly, you can also knock a few of them over
&mdash; so use it deliberately, not defensively.</p>
""".strip()

GROWTH_CONTENT = """
<p class="has-dropcap"><span class="article-dropcap">G</span>rowth in this
field rarely arrives as a single dramatic leap. It tends to show up quietly,
one small deliberate habit at a time, compounding long after anyone's kept
score.</p>

<p>The developers who improve fastest aren't necessarily the most talented in
the room. They're usually the ones who've built a reliable rhythm of
learning into an otherwise busy week.</p>

[[HERO_IMAGE:A small seedling, sprouting from a stack of well-worn books.]]

<h2 class="article-section-title">Small, Repeatable Habits</h2>

<p>A monthly rhythm worth keeping:</p>

<ul>
<li>Read one piece of someone else's code you didn't write.</li>
<li>Ship something small enough to finish, on purpose.</li>
<li>Ask one question you'd normally be embarrassed to ask.</li>
<li>Revisit an old project and notice what you'd do differently now.</li>
</ul>

<h2 class="article-section-title">Progress Is Rarely Loud</h2>

<p>Most real growth is invisible in the moment &mdash; a slightly cleaner
instinct here, a slightly faster debugging session there. Look back after a
year, though, and the distance travelled tends to surprise you.</p>

<p>Build, ship, repeat &mdash; and let the seedling take its time.</p>
""".strip()

BALANCE_CONTENT = """
<p class="has-dropcap"><span class="article-dropcap">P</span>roductivity gets
a lot of attention in this industry. Peace of mind gets considerably less
&mdash; and yet the second tends to be what makes the first sustainable at
all.</p>

<p>Somewhere between the sprint boards and the always-on notifications, it's
easy to mistake constant motion for actual progress.</p>

[[HERO_IMAGE:A quiet moment, weighed against the noise of the week.]]

<h2 class="article-section-title">What the Scale Actually Measures</h2>

<p>A laptop on one side, a small potted plant on the other &mdash; not
because rest is precious in some abstract sense, but because a tired mind
writes tired code, and tired code eventually costs more time than the rest
would have.</p>

<h2 class="article-section-title">A Few Honest Boundaries</h2>

<ul>
<li>Close the laptop at a time you actually decided on, not just whenever
exhaustion wins.</li>
<li>Protect one hour a day that has nothing to do with output.</li>
<li>Let &ldquo;good enough&rdquo; be good enough more often than instinct
allows.</li>
</ul>

<p>Balance isn't the opposite of ambition. It's simply what lets ambition
last longer than a single hard quarter.</p>
""".strip()


ARTICLE_CONTENT = {
    "The Day I Learned to Love Debugging": {
        "content": DEBUGGING_CONTENT,
        "topics": "Mindset, Debugging, Logs, Growth",
    },
    "Building Scalable Apps the Right Way": {
        "content": ARCHITECTURE_CONTENT,
        "topics": "Architecture, Scalability, Systems Design",
    },
    "10 Developer Tools That Save Hours": {
        "content": TOOLBOX_CONTENT,
        "topics": "Tooling, Productivity, Workflow",
    },
    "CSS Tricks That Make You Look Good": {
        "content": CSS_CONTENT,
        "topics": "CSS, Frontend, Design",
    },
    "How to Grow as a Developer (Every Month)": {
        "content": GROWTH_CONTENT,
        "topics": "Career, Growth, Learning",
    },
    "Finding Balance in a Hustle Culture": {
        "content": BALANCE_CONTENT,
        "topics": "Wellbeing, Balance, Mindset",
    },
}


def seed_content(apps, schema_editor):
    Article = apps.get_model("articles", "Article")
    for title, data in ARTICLE_CONTENT.items():
        Article.objects.filter(title=title).update(
            content=data["content"], topics=data["topics"]
        )


def unseed_content(apps, schema_editor):
    Article = apps.get_model("articles", "Article")
    Article.objects.filter(title__in=ARTICLE_CONTENT.keys()).update(
        content="", topics=""
    )


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0003_article_content_topics"),
    ]

    operations = [
        migrations.RunPython(seed_content, unseed_content),
    ]
