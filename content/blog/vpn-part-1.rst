The worst VPN
==============

:date: 2023-03-04
:modified: 2020-03-20
:category: Blog
:slug: the-worst-vpn
:tags: linux, internet
:summary: What is the worst way to make a VPN?

VPNs are somewhat popular these days with seemingly every podcast, steamer and
YouTube creator being sponsored by one of them. Many of them claim to not log
what you do so I thought I would try to make a VPN that required logging
everything you did.

What is a VPN?
---------------

A **V**\ irtual **P**\ rivate **N**\ etwork has some uses to gain secure access
to remote services, or the more popular consumer approach to mask your network
activity from your ISP. I don't really care about any of these use cases for my
VPN, because its so bad it shouldn't have any users.

Why do I care?
---------------

Previously, I worked for a company that made a VPN for almost a decade so I'm
fairly familiar with how they work. I always thought it would be funny to
use a different technology to transport the packets from one peer to another and
for some reason finally decided to give it a shot.

The forced-logging VPN
-----------------------

This VPN, pgVPN, uses a Postgres database as the network transport layer. It
creates a tun device and whenever a packet is read on it, parses it and executes
an `INSERT` statement with the destructured IP details. A trigger in the
Postgres database then executes a procedure to send a `pg_notify` that a new
packet is available. The peer of the tunnel then can act on this notification
and `SELECT` any unreceived packets from the database and write them out of it's
tun device, completing the connection.

How well does it work
----------------------

The best thing I can say about it is that it technically works. Running both
peers and the Postgres database on some containers on my host, I managed to
benchmark a TCP connection at 3.93 Mbits/sec according to iperf3.

.. code::

        Accepted connection from 10.0.0.1, port 56296                                                                                                                  
    [  5] local 10.0.0.2 port 5201 connected to 10.0.0.1 port 56310                                                                                                
    [ ID] Interval           Transfer     Bitrate                                                                                                                  
    [  5]   0.00-1.00   sec   491 KBytes  4.02 Mbits/sec                                                                                                           
    [  5]   1.00-2.00   sec   546 KBytes  4.47 Mbits/sec                                                                                                           
    [  5]   2.00-3.00   sec   568 KBytes  4.66 Mbits/sec                                                                                                           
    [  5]   3.00-4.00   sec   578 KBytes  4.74 Mbits/sec                                                                                                           
    [  5]   4.00-5.00   sec   452 KBytes  3.71 Mbits/sec                                                                                                           
    [  5]   5.00-6.00   sec   280 KBytes  2.29 Mbits/sec                                                                                                           
    [  5]   6.00-7.00   sec   433 KBytes  3.54 Mbits/sec                                                                                                           
    [  5]   7.00-8.00   sec   509 KBytes  4.17 Mbits/sec                                                                                                           
    [  5]   8.00-9.00   sec   484 KBytes  3.96 Mbits/sec                                                                                                           
    [  5]   9.00-10.00  sec   494 KBytes  4.04 Mbits/sec                                                                                                           
    [  5]  10.00-11.00  sec   436 KBytes  3.57 Mbits/sec                                                                                                           
    [  5]  11.00-11.13  sec  65.0 KBytes  3.95 Mbits/sec                                                                                                           
    - - - - - - - - - - - - - - - - - - - - - - - - -                              
    [ ID] Interval           Transfer     Bitrate                                                                                                                  
    [  5]   0.00-11.13  sec  5.21 MBytes  3.93 Mbits/sec

I had no security configured with my connection to Postgres and no encryption of
the data so this is something of a best case scenario. Running TCP over TCP is
generally considered a bad idea, which is what this ends up being.

The benefit to this method is a full and complete log of all traffic managed by
the VPN. Also, both peers of the VPN should work even behind strict NAT since
they aren't connecting to each other directly. You could easily replay any
packets that were handled by this tunnel and/or sell the historical metrics to
interested third parties. The downsides include the incredibly slow speeds, and
the high storage requirements unless you clear out old packets from the
database.

Implementation details
-----------------------

At first I made a simple table, with a trigger and function to send a
`pg_notify` whenever a new packet has been inserted.

.. code::

    CREATE TABLE ipv4_packet (
        id serial PRIMARY KEY,
        ihl smallint,
        tos smallint,
        total_length smallint,
        identification int,
        flags smallint,
        fragment_offset smallint,
        ttl smallint,
        protocol smallint,
        header_checksum int,
        source_address inet,
        dest_address inet,
        options bytea,
        payload bytea,
        sender inet,
        received int DEFAULT 0
    );

    CREATE OR REPLACE FUNCTION notify_packet_ready()
    RETURNS TRIGGER AS $$
    DECLARE
        row RECORD;
    BEGIN
    row = NEW;
    PERFORM pg_notify('packet_ready', '' || row.id);
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE OR REPLACE TRIGGER "packet_notify"
    AFTER INSERT ON ipv4_packet
    FOR EACH ROW EXECUTE PROCEDURE notify_packet_ready();


The tunnel is a simple Go application that reads from a tun device, parses the
data into the header fields using `ipv4.ParseHeader` and then performs an
`INSERT` into the `ipv4_packet` table with the details. Another instance of the
tunnel program running elsewhere would be doing a `listen packet_ready` and then
query all non-received rows from the sender, parsing them back into bytes and
writing out the tun device.

After benchmarking this and seeing the poor performance I thought about
simplifying the schema and packet processing by changing the schema to just

.. code::

    CREATE TABLE raw_packet (
    id SERIAL PRIMARY KEY,
    payload BYTEA,
    sender INET,
    received INT DEFAULT 0
    );

However, this made no noticeable difference. I think the time to commit each row
in postgres is the limiting factor here, I can never observe more than a single
packet being available unreceived at a time.

A next step to improve performance would probably be to try and batch reads from
the tun device into a single update, but this would be at the cost of some
slight increase in latency but should increase performance a bit.

You can look at the code on my `GitHub`_, but I wrote it in Go and I don't know Go
very well so I might not recommend that.

Conclusion
-----------

I didn't expect good performance with this, and what I got was not unexpected. I
didn't really learn much other than a tiny bit about some Go. I probably should
have written it in Python since it would have taken a day less probably.

Some additional findings can be read about in `part 2`_ .

.. _Github: https://github.com/nickhuber/pgVPN
.. _part 2: /blog/less-worst-vpn
