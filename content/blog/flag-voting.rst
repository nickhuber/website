Flag voting
==================

:date: 2020-10-12
:category: Blog
:slug: flag-voting
:tags: django, flags
:summary: Some retrospective on a flag voting system I made and it's results

`I made a website <https://flags.nickhuber.ca>`_ recently to add to the
`plethora <https://www.ranker.com/list/best-country-flags/ranker-travel>`_ `of
<https://www.theringer.com/2016/8/16/16046150/which-country-has-the-best-flag-d0b1d4bf1aa1>`_
`existing <https://justcredible.com/most-beautiful-flags-in-the-world/>`_ sites
analysing the subject of what the best flag is.

I took a different approach where I just provide an open voting platform and
let whoever cares to cast a vote be the deciders. To make things more
interesting, I use the microsoft TrueSkill rating system to treat this as a
skill based competition instead of just the traditional vote counting system. I
have no idea if this is better or worse, but it seems more fun.

What it is built on
--------------------

Django is my go-to framework for any sort of website, so I made this a basic
Django application. I wanted to avoid using any JavaScript in favour of keeping
this all managed server side, for no real reason except to maybe strike out at
the current state of web development.

I store each vote so the whole voting system can be replayed if there was ever
a bug found in how votes were calculated, if I wanted to add new voting methods
or if I wanted to analyze the data over time.

Problems started early
-----------------------

I started with a set of country flags, opting to use SVGs since they scale
perfectly regardless of how high DPI your display is. I shortly noticed some
weird problems on certain flags, and it wasn't until I saw this disaster that I
started to realize what was going on

.. image:: /images/flag-voting/bad-flags.png
    :alt: North Korea vs Brazil flags, with Brazil rendered very incorrectly

Since I was just inserting the content of the SVGs directly in the DOM, the ID
values of various elements (usually stars, which are a very common theme in
flags) would conflict and the flag on the right would end up with weird
rendering issues.

Solving the rendering problem
------------------------------

I still wanted to keep things as SVGs, so my first thought was to find any ID
values in the SVGs and prepend them them with a unique identifier from my
database, but I must have done something wrong because this approach ended up
not helping and corrupted a few of the SVGs. For the sake of not getting stuck
on this little problem I decided to just serve each flag as a SVG from a URL,
and change from having the SVGs declared in the HTML directly to be fetched
from the server. This had a few disadvantages, since it would cause 2 extra
requests to the server, and some extra database queries since all the flag data
is stored in the database. It was better than having broken rendering so I went
ahead with it thinking I would revisit if it ever became an actually problem in
rendering speed.

Showing results
----------------

With the rendering problem solved I wanted to show the top and bottom 5
results. This was pretty easy since the scores are all available in the
database... mostly. With TrueSkill you save a **mu** and a **sigma** value which
you can perform some basic math on to come up with the actual rating. I didn't
want to duplicate this calculated value in the database so I added a custom
manager to add the trueskill rating as a field that could be acted on.

.. code-block:: python

    class FlagManager(models.Manager):
        def get_queryset(self):
            qs = super().get_queryset()
            qs = qs.annotate(
                trueskill_rating=models.ExpressionWrapper(
                    F("trueskill_rating_mu") - (3 * F("trueskill_rating_sigma")),
                    output_field=models.FloatField(),
                )
            )
            return qs


    class Flag(models.Model):
        # [field definitions snipped for brevity]

        objects = FlagManager()

I could then show the results, without any database duplication!

Adding state flags
-------------------

I am going to call these state flags, even though I live in Canada which does
not have states, but has provinces. State is a nice short word that people
generally understand is a bit easier to describe than something generic like
"administrative district" since many countries have different terms for this
sort of thing.

Country flags were added and working but were getting a little boring. Many
people like to joke about how bad the United States's state flags are so I
added a new type of voting for these so-called state flags. I started with
Canada, USA and Netherlands but grew to add many more as the process became
more streamlined.

I quickly noticed that any new flag that was added would be considered a low
ranked flag, which didn't make a lot of sense to me since it never got the
chance to prove itself and took away from the fun of seeing the truly lowest
ranked flags on the list. I needed to add a new way to only consider flags
which were involved in a minimum amount of votes.

I decided to add a new object manager for this, which would only include flags
which have had been involved in at least some lower bound of votes.

.. code-block:: python

    class MinimumVoteManager(FlagManager):
        def get_queryset(self):
            qs = super().get_queryset()
            qs = (
                qs.annotate(
                    num_first_choices=Count(
                        "first_choice",
                        Case(
                            When(first_choice__choice__isnull=False, then=True),
                            When(first_choice__choice__isnull=True, then=False),
                        ),
                    ),
                    num_second_choices=Count(
                        "second_choice",
                        Case(
                            When(second_choice__choice__isnull=False, then=True),
                            When(second_choice__choice__isnull=True, then=False),
                        ),
                    ),
                )
                .annotate(num_choices=F("num_first_choices") + F("num_second_choices"))
                .filter(num_choices__gt=settings.MINIMUM_VOTES_FOR_STATS)
            )
            return qs

I had never used the `Case(When())` syntax in Django before but it really is
powerful and lets you express some complex scenarios without a lot of fuss.

One interesting thing is that I switched from using Sqlite to Postgres around
this time, and saw that this query would take about 500ms to complete on
Sqlite, but with the same data in the database the query would take less than
50ms on Postgres. Before I switched to Postgres I was thinking about removing
this query because it wasn't strictly required but was making pages take a
noticeably longer time to load than would usually be needed.

Finishing touches
------------------

I added a full list of results, showing both state and country flags in their
complete ranking. This page ended up serving 80MB of content and took something
like 4 seconds to load. I reconfigured my nginx configuration to compress HTML
requests and ran all of the SVGs through a python library named `scour
<https://github.com/scour-project/scour>`_ which brought the total request size
down to around 14MB.

This page was now making hundreds of individual requests to my web server,
since every flag had to be its own request to avoid the previously mentioned
rendering problem. Now that this was an actual problem I figured I should solve
it.

After a bit of searching online I decided to make each SVG use a data URI
instead of a new request. This avoids the rendering problem since every SVG is
in its own scope I guess. I was running into issues unless I also ran each SVG
through a base64 encoder which I don't think is strictly necessary but I didn't
really feel like trying to optimise this any more than it needed to.

So now the website is mostly complete. I might decide to add more state flags
or even grow the concept into city flags if I get bored one day.

The results
------------

With all the boring technical ramblings out of the way I am going to talk about
what my website has decided the best and worst flags are.

The most common voters were myself, and some of my friends and co-workers. I
tried to advertise the website briefly on reddit and twitter but that got very
little uptake.

I'm not going to bother showing images of the flags here, you can just look at
`the results yourself <https://flags.nickhuber.ca/full-stats/>`_ if you want to
see what they all look like.

Countries
^^^^^^^^^^

Canada was unsurprisingly the top rated country flag, with Barbados being a
close second. The barbados flag is very similar to the Canadian flag with with
a trident instead of a maple leaf, and blue/yellow/black instead of red and
white. Other flags that match this style are much lower rated, like Norfolk Island.

Macedonia is a seemingly strange 3rd place entry, it has a unique design but
the yellow and red just make me thing of something like the McDonald's logo.

Isle of Man is such a weird flag that I imagine it is mostly there as a series
of joke votes but maybe to be a truly great flag you must go a bit surreal.

Martinique closes out the top 5, from what I can tell this might not even be
their real flag but its a neat design so I decided not to question it any
further.

The bottom flags are almost all flags with the British ensign in the top left
corner. Haiti somehow closes out the list with its very small but incredibly
complex image stamped in the middle of the flag.

States
^^^^^^^

I think the state flags are much more interesting. I don't think I would
personally rank Alaska as the best flag in this category but it does deserve
its high rank. It is a simple design that is easily recognizable. Much more
than can be said about most of the USA state flags.

Japan has many nice looking flags, some end up looking more like corporate
logos than governmental regions but Hokkaido earns its 2nd place position with
another clean and simple design.

South Ostrobothnia in Finland is another strange top ranking flag. It has some
animal repeated 3 times. The animal does look pretty cute though so maybe that
is enough to justify it.

From Netherlands, Friesland claims the 4th place spot with an interesting
series of diagonal bars with what looks like red hearts dividing the blue bars.

Northern Territory from Australia is probably my favourite Australian flag. It
avoids the use the British ensign and has a nice looking flower on a bold
orange background. Still keeping the stars shown on the country flag to show
where it belongs. I think I would rank this flag as my first choice.

For the bottom of the state flags it used to be all the USA states with seals
and words until I added the Spanish flags, which seem universal hated by the
users of my website for their bad colours and complex designs.

Conclusion
-----------

I really enjoyed working on this project. I wish that I was able to get more
people interested in casting votes. I learned a bunch about SVGs and some new
ways of querying in Django. The whole thing is `open source on Github
<https://github.com/nickhuber/flag-voting>`_ if you are interested.
