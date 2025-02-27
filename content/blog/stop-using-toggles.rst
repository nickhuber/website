Stop using toggles
===================

:date: 2025-02-26
:category: Blog
:slug: stop-using-toggles
:summary: Or, how to ruin a perfectly good checkbox
:extra_css: styles/stop-using-toggles.css


.. note::

  The inputs on this page are interactive

Styles of inputs
-----------------

It seems that since the iPhone came out everyone has been trying to mimic some
of its UI designs everywhere. The one I see the most is the "toggle switch" as a
replacement for a checkbox.


.. rubric:: The basic checkbox

.. raw:: html

    <label>
      <input type="checkbox">
      <span>Enable Foobar</span>
    </label>

Unstyled and simple. The fact that it is empty conveys its unchecked status. It
doesn't look like it lives in an iPhone though.


.. rubric:: A basic monochromatic toggle input

.. raw:: html

    <label class="toggle">
      <input class="toggle-checkbox" type="checkbox">
      <div class="toggle-switch"></div>
      <span class="toggle-label">Enable Foobar</span>
    </label>

I suppose this looks more "modern", but when interacting with it, you can become
confused as to which state means the option has been chosen or not. Some toggle
UIs, like using squares instead of circles, seem worse for this than others.


.. rubric:: A toggle that goes green when enabled

.. raw:: html

    <label class="toggle-colour">
      <input class="toggle-checkbox-colour-enabled" type="checkbox">
      <div class="toggle-switch"></div>
      <span class="toggle-label">Enable Foobar</span>
    </label>

Adding some colour to the enabled state seems like a common solution, now when
the toggle is enabled it is clear, But on first look you may not know if the
toggle is set to on if there is no other toggle set to on to indicate colour is
an option.

.. rubric:: A toggle which changes colour depending on enabled state

.. raw:: html

    <label class="toggle-colour">
      <input class="toggle-checkbox-colour-enabled" type="checkbox">
      <div class="toggle-switch toggle-switch-colour-disabled"></div>
      <span class="toggle-label">Enable Foobar</span>
    </label>

With some red colouring adding to the disabled state it can become more clear as
the state of the toggle, except now it kind of looks like an error state; or at
least something that you don't want; it sure would be nice if there was a
simpler way of just showing that this option was checked or not. This particular
obvious colour scheme also has the issue of impacting the roughly 10% of men who
are red/green colour blind.

So maybe using colour isn't a great way to make toggle inputs have clear states,
it also can conflict with your theming in whatever kind of application you are
designing so what other options are there?

.. rubric:: Other options

Using text or icons could help further describe the intended state of the toggle
input; but also adds further noise and complexity to an otherwise simple boolean
choice.


Conclusion
-----------

Let's compare the pros and cons between toggles and checkboxes:

**checkbox pros**

- standard
- simple
- widely used

**checkbox cons**

**toggle pros**

- Apple uses it on the iPhone

**toggle cons**

- tend to be much larger UI elements, wasting screen real estate
- requires extra code
- every application/website behaves differently
- easy to have poor user experience of guessing if a toggle is enabled
