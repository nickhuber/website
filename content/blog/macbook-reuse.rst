MacBook Reuse
====================

:date: 2025-01-14
:category: Blog
:slug: macbook-reuse
:summary: Making an old MacBook usable again since Apple doesn't want to

History
--------

Back in post-secondary; I was a bit of an Apple fan so I got myself a 15" 2010
MacBook Pro, specced with a 2.6Ghz i7 CPU, 8GB of RAM, a 120 GB SSD, a 512MB
Nvidia GT 330M GPU and a "high resolution" 1680x1050 matte display. I used this
computer as my primary computing device for a long time; even swapping out the
optical disk drive to fit another hard drive for increased storage capacity.
Eventually I grew tired of using a laptop and of Apple and switched back to
using a custom built desktop.

The laptop sat in a drawer for many years until I decided I could try and
repurpose it as a portable computer to use around the house. A few kind of
annoying problems exist though, mostly caused by trying to solve the first
problem:

* Apple no longer does operating system updates for this computer
* The computer tries to only use the discrete Nvidia GPU when not running Mac OS
    * | In Linux, this tends to mean that both Intel and Nvidia GPUs are enabled
      | and the computer thinks it has 2 displays and runs quite hot 
    * | I previously had the motherboard replaced because this computer can run
      | too hot and destroy itself (Apple engineering at its finest)
* The Apple keyboard layout has the "super" and "alt" keys positions inverted

Installing Linux
-----------------

Initially I tried installing Fedora Workstation but the display would render
strange looking streaks across the screen after getting past GRUB so something
didn't seem to be working. I decided to try something else, so I went for a
Cinnamon desktop environment running under MATE; which worked but I was quickly
frusted having to work with an Ubuntu derivative so I went back to Fedora, but
this time with the XFCE spin and everything seemed to be working.

As previously mentioned though, the computer thought it had 2 displays, one for
each of the integrated and discrete GPUs in the computer which was making
things very obnoxious to use, and the computer was already starting to run
quite hot. Luckily some people smarter than me seem to have already run into
`this problem
<https://tsak.dev/posts/macbookpro62-disable-nvidia-graphics-card-linux/>`_ and
by following their instructions; by adding 

.. code-block:: shell

    outb 0x728 1 # Switch select
    outb 0x710 2 # Switch display
    outb 0x740 2 # Switch DDC
    outb 0x750 0 # Power down discrete graphics

after :code:`set gfxmode=${GRUB_GFXMODE}` in :code:`/etc/grub.d/00_header` and
regenerating my grub config with :code:`grub-mkconfig -o /boot/grub/grub.cfg` I
was able to see the Nvidia card being seemingly disabled

Finishing things up
--------------------

Now the only thing that seemed to be getting in my way was consistently
pressing "command" when I meant to press "alt", and vice-versa. After trying
(and not having a lot of success) to remap the keys using Xmodmap, I
`discovered <https://wiki.archlinux.org/title/Apple_Keyboard>`_ an option in
the :code:`hid_apple` module, :code:`swap_opt_cmd` which does exactly what I
wanted. After testing the setting I configured it in
:code:`/etc/modprobe.d/hid_apple.conf` and regenerated my initramfs with
:code:`dracut --regenerate-all --force`. Everything seemed to be working as I
was expecting.

After a while the computer still felt like it was running a bit hot; which was
always a problem I had with it and had a fair bit of regret that I paid extra
for the crazy hot i7 instead of sticking with the i5. using :code:`cpupower` I
have tried to limit the frequency to help contain the thermals but it still
runs a bit uncomfortably warm. Hopefully I find it good enough for the small
amount of use I expect it to get.

Maybe this description of my kind of pointless journey of reusing a 14 year old
laptop will help someone out. The battery in this laptop is reporting being
fully charged at 62.7Wh, 82% of the original 75.6Wh. I never used this thing on
battery very often; so it looks like the battery might still hold some
reasonable level of charge. At the very least the effort of writing it out, on
said laptop, gave me some excuse to try it out a bit.
