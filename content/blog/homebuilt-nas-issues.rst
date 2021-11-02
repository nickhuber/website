I built a NAS for my home and ran into many issues
===================================================

:date: 2021-10-19
:category: Blog
:slug: homebuilt-nas-issues
:tags: hardware
:summary:
    I wanted to reuse some old parts I had from when I last upgraded my computer
    to put together a NAS, but ended up replacing everything anyway.

I like to build my own computers, and I have been wanting a NAS for solving some
local file storage needs so I decided to combine these two things into a little
project. I had some leftover parts from when I upgraded from an i5 3570k to a
Ryzen 3600 and intended to reuse the motherboard, RAM and CPU.

As you can probably tell from the title of this post, that didn't quite happen
as smoothly as I intended.

Getting started
----------------

I was talking with my brother about this and he mentioned how he had a case and
power supply he wasn't using any more and offered them up, since I had been
thinking about this for a while but the only things I was missing was the case,
power supply and some hard drives I decided to finally commit to it. I ordered a
SSD and a storage HDD and once they arrived I got started.

Things started nicely with the computer booting into the BIOS and detecting all
of the hardware but as soon as I tried to boot the OS installer it would reboot
shortly into loading the Linux kernel. I tried a few different Linux
distributions and even tried booting a FreeBSD installer and they all behaved
the same. I ran a memcheck and saw no memory issues and could sit in the bios
for hours without issue so on a whim I decided to try the latest BIOS available
for this motherboard, in the odd case it would resolve my issue. In hindsight
this was a bad idea since the motherboard, RAM and CPU had sat unchanged for a
year or two and the BIOS should have had nothing to do with it at this point.

Obviously this didn't do anything to make the situation better, although it did
make it much worse as the computer would no longer show any display output and
just go into a boot loop.

Starting again
---------------

Feeling a bit defeated I shelved the project for a week until picking it back up
deciding to get some new hardware. I decided to get an AMD Athlon 3000G CPU and
an ASRock B450M Pro4-F and a stick of DDR4 RAM to go with it. After taking
another week for these parts to arrive I put them together only for the computer
to fail to even POST! It would just turn itself off after a few seconds. Without
any RAM installed the fans would stay spinning without powering off but
otherwise I would see no activity.

I have a few other computers so I tried the RAM from each of them and saw no
difference. Feeling extra defeated and nearly running out of options I decide to
put together a disaster of a setup with a power supply from my wife's computer
that I didn't feel like removing from its case.

.. figure:: /images/computer-disaster.jpg
    :alt: a very messy computer setup

    This is what peak "I don't care anymore" troubleshooting looks like. Numerous
    cables are stretched to their limit.

And then the computer would happily power on properly! It turns out the power
supply my brother donated to me was a bit defective and was probably the caused
of the initial issues I saw with the original parts. After fully scavenging the
power supply (and ordering a new one to replace her stolen one) the computer
finally functions and I can start configuring the software side of things!

Closing thoughts
-----------------

I was curious if the old motherboard worked with a proper power supply, but
putting that together showed no difference. I think my BIOS upgrade broke it.
That motherboard is an ASRock Z77 Extreme4, which has a swappable BIOS chip so I
could buy a replacement BIOS or get a BIOS reprogrammer to try and flash it
myself and get another working computer out this maybe. Probably a plan for
another day though.

In the end I tried to save myself some money by reusing a motherboard, CPU and
memory and ended up replacing all of them. I tried to save some more money by
using an old power supply and case from my brother and the power supply ended up
needing to be replaced so all I succeeded doing is getting an old case that I
don't even like that much and will probably end up replacing in the near future.

I'm glad its all working now, and now I can go to fighting with software instead
of hardware.
