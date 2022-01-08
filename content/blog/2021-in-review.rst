2021 in review
===============

:date: 2022-01-07
:category: Blog
:slug: 2021-in-review
:summary: Looking back on what I did in 2021

Event-driven microservices with Kafka
--------------------------------------

Near the end of 2020 I started working at Tucows, and at Tucows our software
stack is largely backed by Kafka. The closest thing to event-driven development
I have worked with before was `NOTIFY` in Postgresql so this was quite the
learning experience. I have had a bit of experience working with microservices
before, having been trying to adapt a monolithic Django application at my
previous company into a more focused microservices before quitting, so it has
been nice to continue thinking on things in these terms with even more focus.

Many things initially seem harder when working with event-driven microservices:

#. Things happen asynchronously, so the things patterns like request/response
   become very difficult to emulate.
#. Things can happen out of order (at least between different topics).
#. The system as a whole is more difficult to visualize.

On the other hand a bunch of things initially seem a lot easier:

#. Each service handles a small, specific function. This becomes easy to build,
   test, document and even replace as requirements change.
#. Horizontal scaling is simple, as you can run more instances of any particular
   service with ease as Kafka distributes the workload.
#. Data integrity and discovery can be made easier with a
   `schema registry <https://docs.confluent.io/platform/current/schema-registry/index.html>`_,
   enforcing stronger data guarantees than you would typically get with a mesh
   of RESTful interfaces.
#. Interfacing services from various developers is just publishing and
   subscribing to the right topics.

Overall it has been a learning curve with mistakes made along the way, but the
pros do seem to outweigh the cons. I look forward to continuing to learn the
best ways to manage microservices in this way.

Docker all the things
----------------------

I moved most of my self-hosted websites to a free ARM VPS from Oracle, and
switched to running everything under Docker. It was pretty easy to migrate
everything over to the new VPS, and the new style of running applications.
Having a simple and reproducible environment for my various projects has also
helped for the few minor changes I have made since.

I also have used Docker to run some things on my NAS as I discussed in `an
earlier blog post </blog/traefik-docker-systemd/>`_. Its safe to say I am a fan
of running things in containers now, despite what
`an even earlier post </blog/bitwarden-rs-without-docker/>`_ had said.

A Somewhat viral YouTube video
-------------------------------

.. image:: /images/2021-in-review/youtube.png
    :alt: A very abnormal spike in views in December 2021

For whatever reason, the algorithm decided to pick up on
`a video I made <https://www.youtube.com/watch?v=UzlFU5Q8bTY>`_ in March 2020,
and it has over 210k views at the time of writing. It had a peak of nearly 40k
new views on a single day and still maintains more unique new views a day than
all of my other videos put together.

Nothing is clear why this video was picked up by the algorithm, with YouTube
only telling me that most of the traffic is sourced from "Browse features".

The video seems well received, with a 96.9% positive like ratio, current sitting
at 6614 likes and 215 dislikes.

I hate the video, it was one of the lowest effort videos I have made and its
annoying to watch with how I edited it. It was really fun watching it slowly
grow up to a huge peak that quickly tapered off while I was off work on holiday
though.

Memorable games of the year
----------------------------

In no particular order, here are some of the favourite games I started playing
in 2021.

Celeste
^^^^^^^^

I don't know why I put this off for so long, it was a great platformer with
solid controls and nice pixel-art graphics. I might try and 100% it later.

Neon Abyss
^^^^^^^^^^^

I think I picked this up through a Humble Bundle or something, but it caught my
attention pretty well and I very quickly put quite a few hours into it.

Zero Hour
^^^^^^^^^^

Sort of like a modern day SWAT 4, its great to play with friends. I have only
ever played the mode vs bots though so I have no idea how good the PvP is.

Code Vein
^^^^^^^^^^

Kind of like an anime Dark Souls, but not really as hard and with a more
obnoxious story. Combat didn't vary as much as Dark Souls, but it was still fun.

SNKRX
^^^^^^

Snake, with power-ups and enemies. Its strangely addictive and fun to play in
bursts.

Humankind
^^^^^^^^^^

Like Civilization. Some parts it does better than Civilization 6 and others it
does worse. Still a great game.

Record of Lodoss War-Deedlit in Wonder Labyrinth
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A very long name, for a very short game. This is a Metroidvania-style game and I
think I beat it in around 4 hours. Those 4 hours were solid fun though.
