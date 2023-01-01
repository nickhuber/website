2022 in review
===============

:date: 2023-01-01
:category: Blog
:slug: 2022-in-review
:summary: Looking back on what I did in 2022

I don't really feel like I have anything remarkable to note on this year. I have
changed my mind a bit about what I said about microservices in
`2021 in review </blog/2021-in-review/>`_.

I think Event-driven microservices overcomplicate 99% of projects that use them.
I don't believe its worth going that route unless you have evidence that going
with something simpler will not scale at your expected usage levels. I believe
it analogous to an early-optimization problem and you should worry about having
something that solves the problem correctly before worrying about managing a
scale you may never achieve.

First ever gym membership
--------------------------

I spent the latter quarter of 2022 getting into bouldering at my local climbing
gym with a few of my friends. It has been fun, challenging, and great to actual
be getting some exercise. I have been pretty good about keeping up a twice a
week cadence of having climbing sessions with only a few missed sessions due to
an injured back and being sick.

.. image:: /images/2022-in-review/climb.jpg
    :alt: Climbing a V2

New job
--------

I left my job as a Principle Software Engineer at Tucows for a Senior Software
Engineer position at a company named Procurify. Despite the lower title I took a
pay raise, and now work 4 day work weeks, Monday → Thursday. Having consistent 3
day weekends does wonders for a work/life balance and more companies should
embrace this. The team structure seems a lot nicer as well, with smaller more
focused teams which I am enjoying more.

New computer
-------------

My previous computer was an AMD 3600 with a Nvidia 1070 GPU which was pretty OK
but was starting to struggle a bit on some newer games. It would also
intermittently blue screen with random error codes. I could never quite figure
out what was going on to cause these sporadic failures. Sometimes it would
happen multiple times a day, sometimes not for weeks and sometimes right after
power on. I wanted to mix things up a bit so I decided to just do a whole new
build to solve the problem.

The new computer I decided on was this:

* Intel i5 13600kf
* Scythe Fuma 2 CPU cooler
* Gigabyte B660M DS3H
* AMD Radeon RX 6800 XT
* Corsair HX750 PSU
* Thermaltake Core V21 case

I also reused my 16 GB of DDR4 RAM and disks from my previous computer since I
was pretty certain they weren't causing my issues.

I quite like this new build. The case lets you lay the motherboard horizontal
which is nice for how big and heavy GPUs tend to be now. I used a bunch of 140mm
Noctua fans to help manage airflow and the case is a lot quieter than my
previous, especially when under little load where it is now barely audible.

New phone
----------

I "upgraded" my Pixel 3 to a Pixel 7. It feels generally better but I have a few
grievances:

* No font-facing speakers makes watching videos on the phone significantly worse
  than my previous phone.
* The notch in the display for the front facing camera is weird.
* The camera bump is really large, and actually feels kind of sharp with its
  hard corner. I still don't understand why they don't just make the rest of the
  phone that width so it can sit nicely on a surface without balancing on the
  glass in front of the camera lens. We would even have room for such luxuries
  as a 3.5mm headphone jack.

My old phone was holding less than a day's worth of battery and the USB-C port
stopped working or I would have kept it around quite a bit longer I think. I
hope by the time this Pixel 7 dies phones circle back to having modular
batteries and being more user serviceable.

Gaming with my son
-------------------

My son has taken an interest in both video and board games, 2 of my favourite
hobbies. He turned 4 years old this year so he isn't winning any Fortnite
tournaments or whatever kids do these days but he does like running around in
Mario Maker and/or Mario Odyssey on the Nintendo Switch as well as running
around as C-3PO playing Lego Star Wars: The Skywalker Saga in co-op.

For board games its been a lot of Hungry Hungry Hippos and Don't Break the Ice.
After playing a lot of Hungry Hungry Hippos we went to a local arcade where they
had a human-sized variant of the game which he was very impressed by.

I try to limit his screen time but feel my reasoning is very hypocritical based
on how much time I spend playing games.

Working with AWS
-----------------

I've managed to avoid AWS and other similar offering up until now. I recently
had a look at using EventBridge to push events to services using an API
Destination and found the whole ordeal to be very upsetting. Every time I
thought I had figured it out it turned out I needed to configure yet another
piece of this AWS infrastructure to do solve a self-imposed problem. Its no
wonder Amazon can make so much money with the complex web they let you build and
charge you unexpected amounts for when all is said and done.

Of all the "new" things I have done in the software development space,
generalized infrastructure or whatever you might want to call things like AWS,
GCP or whatever Oracle does has been my least favourite. I like just running
specific services to manage specific data to solve my own specific problems
rather than configuring Amazon to sort of fit my case.

3D printer
-----------

I got my first 3D printer on the 30th of December, and stayed up until the 31st
running into every possible problem assembling it. After I woke up on the 31st I
was able to get it working.

The first print started good and then quickly turned into a spindly mess but
after I adjusted a Z offset I was able to get some nice prints out of it. Things
still do like to pull off from the bed while printing a bit, so I have some more
fine-tuning to do before it is just fire and forget.

.. image:: /images/2022-in-review/3d-printer.jpg
    :alt: Printing some spaghetti

Memorable games of the year
----------------------------

Across the Obelisk
^^^^^^^^^^^^^^^^^^^

It sounds like yet-another-roguelike-deck-builder but something about it clicked
with me more than Slay the Spire or Monster Train. I first played it in co-op
but kept playing by myself until I unlocked nearly everything

Shadows Over Loathing
^^^^^^^^^^^^^^^^^^^^^^

From the makers of Kingdom of Loathing and West of Loathing, this is another
funny RPG with black and white stickman style art. If the comedy is your style
its a great game.

Per Aspera
^^^^^^^^^^^

I played through this colonizing mars game in a sandbox co-op mode with a friend
before playing through the single player campaign. I wish some of the concepts
from the campaign were available in co-op but the game is fun either way.

Elden Ring
^^^^^^^^^^^

I don't care much for the open world part of the game since it mostly just feels
like filler in between the interesting dungeons, but the combat, dungeons and
bosses are great. I played with the
`seamless co-op <https://www.nexusmods.com/eldenring/mods/510>`_ mod with a few
friends after beating the game and it added a great new experience.

It does suffer from the same things that other open world games do where a lot
of the content feels copy and pasted. There are many of these micro dungeons
that almost feel like they were built in a template engine (Mario Maker but for
Dark Souls) and you end up fighting the same boss multiple times just with
different HP and damage numbers.

Ready or Not
^^^^^^^^^^^^^

Like a modern version of SWAT 4, this game is a blast to play with a group of
friends. The game isn't finished yet as of the time of writing and for some
reason they just disabled all of the mirrors in the game. They have one very
questionable decision with a more expensive version of the game that gets
updates earlier but overall I'm looking forward to seeing how the game shapes up
as it finishes its journey through early access

God of War
^^^^^^^^^^^

I just started playing this over the Christmas break and its every bit as good
as people say it is. I hope that the sequel comes to PC as well since I do not
have a Playstation.
