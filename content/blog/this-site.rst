This website
=============

:date: 2019-05-18
:modified: 2020-02-02
:category: Blog
:slug: this-site
:tags: meta
:summary: What is going on with this website?

I decided to use Pelican_ for this blog since I
didn't feel like messing around with HTML too much and it seemed like a nice
way of letting me just write things in restructured text.

.. class:: strike

I wrote a simple theme using bootstrap so I could have some control over how
things are displayed.

I used a theme from `my friend`_ which works really well, has support for
putting markup in the margins and even respects light/dark mode of the
operating system.

Replacing the default landing page
-----------------------------------

I wanted the default page for this site to be a static page, and not a listing
of articles like Pelican wants to serve. It ends up being pretty easy to
achieve this behaviour, but is not intuitive at all. On a file in the
``content/pages`` set something up like the following. I used
``content/pages/index.rst`` for this website.

.. code-block:: rst

    My new root page
    =================

    :untitled:
    :override_url:
    :save_as: index.html

    This is my homepage, it is not just a listing of articles.

Just replacing the ``save_as`` metadata with index.html and overriding the
``url`` to be nothing is enough to achieve the desired behaviour

.. _Pelican: https://github.com/getpelican/pelican/
.. _`my friend`: https://git.sr.ht/~sqwishy/froghat.ca