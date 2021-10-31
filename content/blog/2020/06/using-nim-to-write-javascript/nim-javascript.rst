Using Nim to write JavaScript
==============================

:date: 2020-06-28
:modified: 2020-07-03
:category: Blog
:slug: nim-javascript
:tags: nim, javascript
:summary: My brief experience with using Nim for JavaScript

I've been `playing around with Nim <https://github.com/nickhuber/nimboy>`_ [#]_
recently and have been finding it to be quite the enjoyable language. I knew it
was possible to have the language compile to JavaScript but wanted to see how
that worked, since I find JavaScript to not be that enjoyable to work with.

.. [#]

    I plan on writing about this once I actually get around to finishing it

Recently a `friend of mine <https://tremblay.dev>`_ made
`wheelman <https://wheelman.tremblay.dev/>`_ in Elm, itself being a recreation
of `wheeldecide <https://wheeldecide.com/>`_ and I decided to do pretty much the
same thing except in Nim. The end result is available as
`Nimdecision <https://wheel.nickhuber.ca/>`_.

.. class:: comment

    Nimdecision is a really lame play on "Nim" and "indecision"

There are already framework for making web pages with Nim, like `karas
<https://github.com/pragmagic/karax>`_ and `Jester
<https://github.com/dom96/jester>`_ but I wanted to see what the base language
was capable of, so decided against using anything outside of the core library.

Compiling is simple, just use `nim js file.nim` instead of `nim c file.nim`,
and then the resulting javascript file is free for including in whichever html
page you want.

Getting started
----------------

I decided I would write some basic HTML, using my current favourite CSS
framework, `bulma <https://bulma.io/>`_ for some basic styling. I put some IDs
on some elements, which I would use as both input and output selectors. Things
started out simple with using `document.getElementById()` to get the elements
and updating with the standard JavaScript DOM API. I decided to use an SVG to
actually render the wheel, and that is where I saw my first major problem. The
SVG wouldn't render even though it appeared in the DOM just fine. If I edited
the DOM in Firefox then the SVG would show up just fine though, even though I
didn't actually change anything.

It turns out I just missed something somewhat important with how you have to
declare an SVG element. They need a namespace defined, in particular I wanted
to define the `http://www.w3.org/2000/svg` namespace. Normally you use the
`createElementNS` function to create an element with a specific namespace,
but that isn't exposed in Nim so I had to write the wrapper for it myself.
Luckily this is incredibly simple and ended up just being

.. code-block:: nim

    import dom

    proc createElementNS*(d: Document, namespace: cstring, identifier: cstring): Element {.importcpp.}
    proc setAttributeNS*(n: Node, namespace: cstring, name, value: cstring) {.importcpp.}

With the NS functions defined I was able to make the SVG and actually have it render properly!

Animating the wheel
--------------------

I just used some basic CSS animations for the rotating of the wheel, which is
all just flavour since the application has already decided what the outcome is
before any animation starts. One new thing I used here but haven't used before
was `CSS custom properties
<https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties>`_
which is a really cool way of dynamically adjusting style sheets from
JavaScript (or Nim, in my case). For example

.. code-block:: nim

    var svg = document.getElementById("svg")
    svg.style.setProperty("--rotationEnd", fmt("{rotation}deg"))

will update the `--rotationEnd` variable defined in the style sheet initially as

.. code-block:: css

    #svg {
        --rotationEnd: 0deg;
    }

    @keyframes spin-stop {
        from { transform:rotate(0deg); }
        to { transform:rotate(var(--rotationEnd)); }
    }

to be whatever angle the variable `rotation` is.

Conclusion
-----------

In summary, this was a simple project that let me discovery how simple it is to
use Nim as a replacement for JavaScript in any future projects I may have that
require it. I believe that I could recommend it going forward to others that
dislike JavaScript and don't really see TypeScript as solving the problems that
JavaScript has.

The source code for this is available on as
`a GitHub repository <https://github.com/nickhuber/nimdecision>`_.
