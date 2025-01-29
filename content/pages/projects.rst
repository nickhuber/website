Projects
=========

:date: 2021-12-06
:slug: projects
:summary: projects

These are some projects of my own I have worked on. The sources for most can be
found on my `Github <https://github.com/nickhuber>`_

PACT
-----

It stands for **\ P**\ latform **\ A**\ gnostic **\ C**\ ombat **\ T**\ racker,
although I've only ever used it with Pathfinder and D&D 5th edition. It should
work fine for any tabletop gaming system that has the concept of initiative,
and hit points.

It's goal is to give something simple to help a DM manage encounters while
still being out of the way enough to not bring too much technology to the table
during game nights.

I use Django for the database management and serving an API powered by Django
REST Framework. The frontend is a pretty simple Vuejs with Axios to handle the
requests.

I am very happy with how it works right now, and am looking forward to adding
more features to it. It is my first project that I have actually managed to get
users for, even if it is just my friends.

It is somewhat reliably online at https://pact.nickhuber.ca/.

Youtube stats
--------------

https://youtube.nickhuber.ca is a site I made to track some of the trends
between my own and some of my friends Youtube channels. Its a very simple Django
application that pulls data from the Youtube API on a timer, and draws charts
server-side using Pygal.


btrfs RAID explainer
---------------------

https://btrfs.nickhuber.ca is a simple VueJS application to show how much usable
space you would get with various disk configurations when running RAID profiles
on a btrfs filesystem. It was both an excuse to look at VueJS some more and a
way to figure out how RAID actually worked with btrfs.

Hitomezashi patterns
---------------------

After watching `A Numberphile video <https://youtu.be/JbfhzlMk2eY>`_ I thought
it would be fun to see some of these patterns made quickly using some of the
styles shown in the Video. I made https://hito.nickhuber.ca to do just that.


Joke websites
--------------

For some laughs with friends I have made some dumb websites.

- https://flags.nickhuber.ca
- https://wheel.nickhuber.ca
- https://startups.nickhuber.ca
- https://passwords.nickhuber.ca
