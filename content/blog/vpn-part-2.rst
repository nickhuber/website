A less worst VPN
=================

:date: 2023-03-20
:category: Blog
:slug: less-worst-vpn
:tags: linux, internet
:summary: Making the worst VPN a bit less worse

This is a follow-up post to my `previous post`_ about Postgresql as a transport
layer for a VPN application. I suggest reading that post first, but you don't
have to listen to me; I'm just a website.

Kind of cheating
-----------------

I was curious if the `pg_notify` or the `INSERT` was more of a bottleneck so I
adapted the tunnel to call `pg_notify` directly instead of ever doing an
`INSERT` or `SELECT`. I included a base64 encoding of the packet as the
notification payload and this resulted in a roughly 100x improvement to the
throughput of the tunnel. I didn't focus a lot of time here because it really
defeats what I think of as the core principle of the tunnel (requiring data to
be logged) but it did show a possible increase to the ceiling in possible
performance with using postgres as a data transport layer

Moving the `pg_notify`
-----------------------

Previously, I used a trigger in the Postgresql database to send the `pg_notify`.
This was nice because it kept everything contained in the database and I figured
it would be quick. After hearing some feedback that triggers can be quite a slow
path in performance, I tried sending the `pg_notify` with the row ID after
writing it to the database from the tunnel process. The performance seemed
unchanged however.

Go improvements
----------------

I made the database actions after reading a packet off of the tun device into a
goroutine, and saw a significant performance boost. The same goroutine changes
before the changes to `pg_notify` inside the tunnel application don't show any
noticeable difference so at some point the application must have become limited
by the speed of syncing packets to the database rather than the signalling and
reading of them from the other side.

With both the changes to calling `pg_notify` inside the application and calling
the function to do the Postgres operations as a goroutine I now see a roughly
10x performance gain compared to letting the database call it with a trigger.

.. code::

    Accepted connection from 10.0.0.2, port 38994
    [  5] local 10.0.0.1 port 5201 connected to 10.0.0.2 port 39002
    [ ID] Interval           Transfer     Bitrate
    [  5]   0.00-1.00   sec  6.55 MBytes  54.9 Mbits/sec                  
    [  5]   1.00-2.00   sec  6.20 MBytes  52.0 Mbits/sec                  
    [  5]   2.00-3.00   sec  4.49 MBytes  37.7 Mbits/sec                  
    [  5]   3.00-4.00   sec  3.29 MBytes  27.6 Mbits/sec                  
    [  5]   4.00-5.00   sec  6.18 MBytes  51.9 Mbits/sec                  
    [  5]   5.00-6.00   sec  6.58 MBytes  55.2 Mbits/sec                  
    [  5]   6.00-7.00   sec  4.59 MBytes  38.5 Mbits/sec                  
    [  5]   7.00-8.00   sec  5.73 MBytes  48.0 Mbits/sec                  
    [  5]   8.00-9.00   sec  6.23 MBytes  52.3 Mbits/sec                  
    [  5]   9.00-10.00  sec  6.03 MBytes  50.6 Mbits/sec                  
    [  5]  10.00-10.08  sec   444 KBytes  46.1 Mbits/sec                  
    - - - - - - - - - - - - - - - - - - - - - - - - -
    [ ID] Interval           Transfer     Bitrate
    [  5]   0.00-10.08  sec  56.3 MBytes  46.9 Mbits/sec                  receiver

This has some of the benefits of the cheating method of calling `pg_notify` from
the tunnel program without the cheating aspect of including the packet as the
payload and still relies on the data existing in the database, since it has to
be fetched by the peer using a `SELECT`.

Follow-up performance thoughts
-------------------------------

I still want to add batch read/write support, but the tun device isn't even the
bottleneck, as proven by the speeds I was able to achieve just using `pg_notify`
to transport the data, but using the goroutine to write entries to the database
concurrently shows that if I can parallelize more work to the database I could
potentially get more performance boosts. I should try and insert multiple rows
in the same call and do the same with reading the packets as a next step.

Conclusion
-----------

The tunnel is now performing a bit better than I thought it would, much better
than it was before and with a potential ceiling dramatically higher than I
thought it could be.

.. _previous post: /blog/the-worst-vpn
