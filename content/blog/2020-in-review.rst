2020 in review
===============

:date: 2020-12-30
:category: Blog
:slug: 2020-in-review
:summary: Looking back on what I did in 2020


Learning a bit of Go
---------------------

I wrote `a simple utility <https://github.com/nickhuber/tc-vis>`_ in Go to view
Linux TC qdiscs and classes in a way I find easier to understand. I wanted
something easy to write and statically compiled so it would run on any system
with a minimal amount of fuss. I found Go very easy to pick up, I have looked at
a bit before when looking into how InfluxDB handles things. I really enjoyed the
built in tooling for doing things like formatting code and compiling and running
in a single command. I hope to focus a bit more strongly on some Go projects in
2021.

Working from home
------------------

With the global pandemic of COVID-19 forcing a change in work style, I started
working from home full time and found it easy to adapt to. This lead to me
thinking about finding a new job as other companies were becoming more open to
remote workers.

I am very fortunate to work in an industry where being fully remote is now a
fully realized possibility, at least one good thing has come from this virus.

Learning a bit of Nim
----------------------

I started on a GameBoy emulator written in `Nim <https://nim-lang.org/>`_, which
I cleverly named `Nimboy <https://github.com/nickhuber/nimboy>`_. Nim is a very
interesting language, which can write very performant code but is nearly as easy
to write as Python. I hope to regain focus and finish this project, because I
have been enjoying learning what goes into making an emulator work along with
all the interesting details about how the CPU and other components work together
to run an application.

I also wrote a simple decision making website in Nim, except compiling to
JavaScript instead of C. I have already `written a post </blog/nim-javascript/>`_ about
this.

Flag voting website
--------------------

I've already covered this in a `blog post </blog/flag-voting/>`_ but it was a fun
project to work on, and the website is still active for more votes. It was fun
to work on and see the results come in from the people interested in casting
votes.

I may spend more time on this in 2021 to see how different ways of counting
votes can change the outcomes, or doing some plotting of how certain flags are
considered over time.

Changing career
----------------

in November I left my job of 9 years at `Multapplied <https://multapplied.net>`_
and joined `Tucows <https://www.tucows.com>`_. The increase of nearly 2 orders
of magnitude in the number of employees has taken some getting used to, however
I am very much enjoying the new technology, methodologies and people I am now
working with.

Rethinking my stance on container applications
-----------------------------------------------

I used to be very opposed to systems like docker, as I would rather just run
applications directly than have all these extra layers of abstractions and
complexity. I upgraded my VPS to Fedora 33 and several of my Django applications
broke as their virtual environments had to be recreated due to a change of the
version of Python to 3.9. If these were run as
`Docker <https://www.docker.com/>`_ or
`Podman <http://docs.podman.io/en/latest/>`_ containers then this would not have
been a problem. I also setup my home router to export some metrics to
`InfluxDB <https://www.influxdata.com/>`_ and display then with
`Grafana <https://grafana.com/>`_. I ran these as Podman containers on my local
server and found it easy to manage the storage and network port mappings.

In 2021 I hope to have a more firm understanding of systems like Docker and see
what it is like to manage my own applications in that manner.

Handling a toddler
-------------------

My son became 2 years old this year and has been learning many words like "no".
He has gotten really good at playing without constant attention which is nice
for my wife and I to spend more time on our own activities while he plays in his
own world. It will be exciting to see how he grows in 2021 as his use of
language grows and he can better express his desires.

Top games of the year
----------------------

This isn't a list of the top games that came out in 2020, but the top games I
enjoyed playing in 2020.

Hades
^^^^^^

I love roguelikes, and this one is no exception. It has a nice form of
progression to keep things fresh and has an absolutely insane amount of
voiceover for all the communication between characters. I couldn't put this game
down until after I beat it, and still see myself wanting to come back for more.

Deep Rock Galatic
^^^^^^^^^^^^^^^^^^

One of the best co-op games of recent times, its very fun to go through the
randomly generated caves complete all the objectives. I've been playing since
early access and still keep coming back.

Divinity: Original Sin 2
^^^^^^^^^^^^^^^^^^^^^^^^^

I've already beaten this game many times, both in solo and co-op with a friend.
In 2020 I started a 4 player co-op playhrough with many mods which brought new
life to the game. I hope that Baldur's Gate 3 is just as good if not better than
this.

StarCraft 2
^^^^^^^^^^^^

StarCraft 2 celebrated its 10th anniversary with the addition of a new
achievement to every level in each of the campaigns. It was incredibly fun to go
back and play through all those levels after so long and earning some of the
achievements was a bit difficult.

Halo: The Master Chief Collection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I've been enjoying playing through the Halo games again as they became released
on the PC. With Halo 4 released this year it is finally complete, since there
are no plans to bring Halo 5 this way. Despite Halo 4 being the worst of the
bunch to end on, I did greatly enjoy playing through all of these games and will
be spending some more time trying to unlock more of the many achievements
available.

Cyberpunk 2077
^^^^^^^^^^^^^^^

Not the most stable, performant or bug-free game released this year, even on the
PC but I kept coming back until I reached the end. I plan to revisit this game
once the developers have had some more time to iron out some of the bugs and
hopefully improve the performance.

Monster Hunter: World
^^^^^^^^^^^^^^^^^^^^^^

The Iceborne expansion came out early in 2020 and sucked me right back into this
game. I generally like the changes that the expansion brought in, and the
increased diversity in the monsters and environments helps prevent the game from
getting too repetitive too quickly. I wrote a
`Monster Hunter: World Iceborne review </reviews/monster-hunter-world-iceborne/>`_
with some more details.

DOOM Eternal
^^^^^^^^^^^^^

I actually preferred DOOM 2016 more than this, I did write a
`DOOM Eternal review </reviews/doom-eternal/>`_ on this going into more detail
about it already. but I still did enjoy it but don't see myself coming back to
play it again.
