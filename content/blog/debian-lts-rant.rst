Debian "LTS" rant
==================

:date: 2019-06-04
:category: Blog
:slug: debian-lts-rant
:tags: linux, debian
:summary: Just some late complaining about a recent Debian change

Debian has extended support for some of their recent releases for people that
are slow to upgrade. As of the time of this writing, Debian Jessie is considered
LTS [#LTS]_. The concept of LTS on Debian is relatively new, with Jessie only
being the third release to be considered as one, after Wheezy and Squeeze.

Supported must have a special meaning to Debian, because in March 2019, the
people in charge of the FTP repository for Debian `decided to remove
<https://lists.debian.org/debian-devel-announce/2019/03/msg00006.html>`_
`jessie-updates` and `jessie-backports` from the mirrors, causing existing
Jessie installs to get errors when trying to update to fix any pending security
issues that have been patched. The reasoning for this was that
`jessie-updates` and `jessie-backports` were no longer getting updates and
were already copied in the archive.debian.org repository, and only the security
repository . `jessie-updates` is a bit of a strange case, it seems to have to
do with the point releases (8.10, 8.11) of Debian, and once those are released
anything from `jessie-updates` gets merged into the standard `jessie`
repository.

`jessie-backports` is a bit more complicated, since although the repository is
archived on archive.debian.org, it expired a while ago and won't work unless you
globally disable the validity checks for "valid-until" for all repositories.

Hopefully by the time Debian Stretch goes "LTS" I will no longer have any old
systems running on it so I don't have to do a bunch of maintenance on an
operating system that is advertised as still being supported. I would rather be
supported or not, instead of being in this gray area that Debian insists on.

.. [#LTS] Long-term support
