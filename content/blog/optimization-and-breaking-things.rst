That time I broke phone calls by optimizing
============================================

:date: 2025-05-15
:category: Blog
:slug: optimizing-and-breaking-things
:summary: Once I made some code go so fast that it broke phone calls

I used to be a developer on a VPN product, although nothing like "NordVPN" or
"Surfshark" which kind of pollute that term these days. This software was
written in Python and originally serviced 3Mbps DSL connections. It's primary
goal was "link aggregation" which was the ability to consume (most) of the
bandwidth amongst any number of internet connections into a single psuedo
connection for increased speed and reliability.

As the customer base expanded the bandwidth needs grew, running a high
performance application in Python was becoming a limiting factor. Because of
this there were initially a lot of room for trivial improvements, sometimes by
adding some type hints to help `Cython`_ compile to a more direct C alias,
sometimes by calling functions written in C directly. This was some of the most
enjoyable work I did at that company and I loved seeing how much throughput I
could push through a specific hardware platform without breaking any
compatibility between client and server versions. The most memorable of these
optimization scenarios will be discussed in this post.

I was working on what I called the "critical path" the code that every packet
would always traverse when being processed by our application. In particular I
was improving the speed at which some metrics were collected and how it would
decide to transmit packets received on a physical interface out the VPN tunnel
interface. This was important sice our VPN would send and receive packets
across any number of internet connections the software would need do its best
to ensure things were received in order on the other side to help avoid various
applications and protocols from thinking the connection has packet loss or is
congested from receiving things out of order.

Something along this path would try to configure a timer based on the time it
took between packet receives which would actually cause the queued packets to
be transmitted in order. The problem was that the time between packets was
becoming so short in duration that sometimes it would be close enough to 0 that
the timer function (``ev_timer_set`` from `libev`_) would end up receiving a value
of 0 for the repeat interval, which it treats as being asked to stop repeating
the timer, instead of the intended behaviour to repeat as soon as possible.

This went mostly unnoticed for a while until some customer started reporting
that they would receive 1 way audio on VOIP calls after a few minutes on some 
calls. After some testing I was able to observe that the calls would actually
resume working in both directions after some specific (I forget the duration)
amount of time, and after viewing some packet captures it seemed that it was
when our sequence numbers on the packets would roll over and sort of trick our
own software into thinking an "early" packet had been received and to flush the
queue of out of order packets. It would then continue to function until it ran
into the same bug again and disabled repeating this timer.

I'm pretty sure the initial solution was to use something along the lines of
``max(0.001, x)`` to set the repeat value, which pretty much ensured that this
would be acted on in the next iteration of the event loop.

.. _Cython: https://cython.org/
.. _libev: https://software.schmorp.de/pkg/libev.html
