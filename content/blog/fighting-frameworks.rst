Fighting Frameworks
====================

:date: 2024-10-17
:category: Blog
:slug: fighting-frameworks
:summary: Ranting about how people don't use their chosen tools

It seems like this must be a common line of thought from software developers in
the various industries I have worked in when working on some feature or fixing
some bug in an application written using a library (because who actually solves
interesting problems anymore, other people can do that work) and they think to
themselves "This library is not doing things the way I like; I'm going to
enforce a different pattern on it". Welcome to my video essay (in text format)
where I will express my opinions on why you are wrong if you think like that.

Most recently I have seen this with a moderately large Django project; where the
structure of the project has gone out of control and it barely resembles Django
anymore. Previously I have observed people trying to make a distributed
event-driven platform in Kafka work like synchronous HTTP calls. Prior to that I
was one of these people who was wrong as I overwrote large sections of Django
REST Framework to try and bend it to my will.

In each of these cases I have observed different types of self-induced pain
which could have been avoided by either:

#. Embracing the framework
#. Not using a framework

Picking the forbidden option "fight against the framework" will almost always
end in frustration.

The first example is a hilariously complex program that feels like someone
looked at `this
<https://github.com/EnterpriseQualityCoding/FizzBuzzEnterpriseEdition>` and
thought "This is exactly how every single feature should be written. I consider
myself fairly experienced in Django but I am constantly lost trying to find how
anything works, and minor features require touching many files with what ends up
looking like a bunch of functions proxying data through to each other before
they get to anything that actually does something.

The second example is kind of funny because there is some literature on doing
request/response patterns inside a system like Kafka but I think you are
generally wrong if you are using those and would be happier just making HTTP
calls between services.

The final example mostly exposed itself as an upgrade hell where our
customizations to Django REST Framework were incompatible with newer versions
of that library, and newer versions of Django were incompatible with our version
of Django REST Framework. From what I remember I quit working at that company
before the issue was resolved.

When you choose to use a framework you are making an important decision,  you
get to start working faster on solving your actual problem instead of building a
platform, however I think many people miss the fact that a framework is the
foundation of what you are building and if you are working outside of that
foundation because you don't agree with it then why do you even have the
framework. Worse is when you are working against the framework while still
operating inside of it; effectively sabotaging all the benefits a framework
offers.

Most of the problems I have observed are with people not using their chosen
framework the way it was intended, and then blaming the framework for the poor
performance or added complexity. Instead of trying to better learn to use the
tools they grow a hatred for them and do their best to encourage working against
them within the rest of the organization.

Outside of just the complexity of the code or upgrade paths you also lose out
another huge benefit of using a framework; the community and documentation. If
you are having performance issues in something written compliant with the
framework it would be easy to search for, or ask for examples about why things
are the way they are but if you have swapped out core components for bespoke
implementations or have overridden internal functions then the only person who
can help you is you.

Closing Thoughts
-----------------
I don't think everyone should always use a framework for everything, I probably
think close to the opposite; its crazy how much these frameworks have taken over
development. I just think that when you are writing software inside of a
framework you should use the tools given to you properly or else you are nailing
in a screw with a hacksaw.
