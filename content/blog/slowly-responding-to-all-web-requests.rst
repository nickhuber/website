Trying to troll website crawlers
=================================

:date: 2021-10-28
:category: Blog
:slug: slowly-responding-to-all-web-requests
:tags: internet
:summary:
    I responded to every HTTP request with a never-ending stream of data to see
    how long the bots would stick around for.

Preamble
---------
I was looking at my nginx logs and saw many bogus requests for things like
`/phpmyadmin` and `/wp-login.php`. I was curious how long these bots would keep
a connection open if I just started responding to them with data so that is what
I did.

The results
------------
I'll start by summarizing some of the results, since that is maybe the most
interesting thing out of this otherwise uninteresting project.

+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| Total number of requests | Path                                                                                                              |
+==========================+===================================================================================================================+
| 1960                     | /                                                                                                                 |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 300                      | /boaform/admin/formLogin                                                                                          |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 224                      | /.env                                                                                                             |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 175                      | /config/getuser?index=0                                                                                           |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 153                      | /vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php                                                               |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 103                      | /wp-login.php                                                                                                     |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 90                       | /robots.txt                                                                                                       |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 78                       | /_ignition/execute-solution                                                                                       |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 73                       | /wp-content/plugins/wp-file-manager/readme.txt                                                                    |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 73                       | /solr/admin/info/system?wt=json                                                                                   |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 73                       | /index.php?s=/Index/\think\app/invokefunction&function=call_user_func_array&vars[0]=md5&vars[1][]=HelloThinkPHP21 |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 73                       | /console/                                                                                                         |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 73                       | /api/jsonws/invoke                                                                                                |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 73                       | /Autodiscover/Autodiscover.xml                                                                                    |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 73                       | /?a=fetch&content=<php>die(@md5(HelloThinkCMF))</php>                                                             |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 73                       | /?XDEBUG_SESSION_START=phpstorm                                                                                   |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 44                       | /favicon.ico                                                                                                      |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+
| 27                       | /HNAP1/                                                                                                           |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+

I think `/` was the most common occurrence because I handled any request that
didn't specify a server, so if things were just trolling through IP addresses
this is where they would end up. It is probably best to ignore that when trying
to find any meaning in this data, assuming there is any.

It is kind of fun to see the sorts of exploits that these bots are probably
looking for.

Another cool chart is how long I was able to keep connections open. Some of
these records might have been able to be higher if I wrote a program that didn't
crash as often and didn't leave it stopped for days or months on end.

+-------------+------------------------------+
| Time (ms)   | Path                         +
+=============+==============================+
| 1692140443  | /                            |
+-------------+------------------------------+
| 178329225   | /                            |
+-------------+------------------------------+
| 95747072    | /                            |
+-------------+------------------------------+
| 93974501    | /                            |
+-------------+------------------------------+
| 75506249    | /                            |
+-------------+------------------------------+
| 72288944    | /mysql.php                   |
+-------------+------------------------------+
| 71374032    | /wp-includes/wlwmanifest.xml |
+-------------+------------------------------+
| 51706852    | /                            |
+-------------+------------------------------+
| 45828589    | /                            |
+-------------+------------------------------+
| 38326312    | /                            |
+-------------+------------------------------+
| 32069630    | /invoker/readonly            |
+-------------+------------------------------+
| 31677935    | /                            |
+-------------+------------------------------+
| 28798161    | /                            |
+-------------+------------------------------+
| 25827719    | /                            |
+-------------+------------------------------+
| 24480354    | /                            |
+-------------+------------------------------+
| 16025985    | /                            |
+-------------+------------------------------+
| 16024819    | /                            |
+-------------+------------------------------+
| 15239431    | /                            |
+-------------+------------------------------+
| 14133912    | /                            |
+-------------+------------------------------+
| 13668459    | /                            |
+-------------+------------------------------+
| 12270901    | /                            |
+-------------+------------------------------+
| 12062093    | /                            |
+-------------+------------------------------+

That looks like an impressive 19 days I held someone's random connection open,
quickly dropping quite quickly down to under day. I wonder why that one
connection was able to stay open for so long.

What did I do to keep the connections open
-------------------------------------------

Using no evidence, I thought that clients would terminate the connection if
they didn't receive any data so I decided to not only hold connections open, but
send back 1 character from Rick Astley's "Never Gonna Give You Up" every 75 ms
on repeat forever. I truly never will give up on these connections.

I initially wrote this in Python, using some asyncio iterators(I think) but have
since rewritten it into Go using some goroutines since I am somewhat interested
in learning that language. Source code is available
`on my GitHub <https://github.com/nickhuber/reverse-slowloris>`_.

What did I learn from this?
----------------------------

Nothing much really. I guess I learned that if I don't close my database handles
in Go I leak a ton of memory eventually but that isn't very surprising. I also
learned that I should have set this supervised by systemd or something since I
had it crash a lot and lose a lot of potential metrics while the service wasn't
running in the random tmux session I had open.

The results were kind of fun I guess. And it was pretty cool seeing text stream
into a webpage in Firefox without any JavaScript.
