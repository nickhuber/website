My experience with project management
======================================

:date: 2020-02-02
:modified: 2020-02-04
:category: Blog
:tags: project management, history
:slug: project-management-history
:summary:
    A somewhat brief overview of how I have seen project management done and
    how it has evolved.


The beginning
--------------

.. class:: aside
.. [#]

    We worked closely with a Dutch ISP with similar goals, Kliksafe, to provide
    either white or blacklist access to certain websites. The city I live in
    has a fairly significant Dutch populace.

Around 8 years ago a friend helped me get a job doing technical support for a
filtered ISP [#]_ that also did managed services, and I would eventually pivot
into my true calling as a software developer. After half a year or so of doing
technical support I joined in on development of a project that had the goal of
merging multiple internet connections into a single virtual connection that we
called bonding, and I now better know as link aggregation. This project would
form my current employer in another year or so. I was fairly fresh out of post
secondary school and had never been involved with something I hadn't started.
At that point in time I worked on whatever features or bugs were assigned to me
and helped provide support to the few clients we had.

.. class:: aside
.. [#]

   I'm sure many projects start off as waterfall as the project is small enough
   to keep the whole thing in hand and features are simple like "Add a DHCP
   server configuration"

I had heard of and studied some different software development patterns, but
never worked on something big enough to really be classified as any of them.
Looking back at this part of the company, the closest way to categorize it would
be as waterfall [#]_, except the features were kept small so we were able to do
multiple releases a year. Adding support for things like NAT, quality of
service, encryption and more.

Growth and the pains that come with it
---------------------------------------

For many years this worked fine. The project was spearheaded by my only other
co-worker and things grew slowly. We added a few new developers and some sales
people and things started to pick up steam. At this point in time we started to
change our focus into what the industry would start to coin "SD-WAN". We all of
a sudden had a big feature on our hands. A long time was spent planning this
feature and during development problems were found and things had to be
changed. *Things had to be changed multiple times*.

.. class:: aside
.. [#]

    In 2020, we are still modifying parts of the original implementation.

We eventually did release our SD-WAN implementation, and it has gotten more use
than any other feature outside of the core component, link aggregation. What it
ended up being released as differed quite a bit from the original plan and much
time would have be spent fixing up some assumptions that were made in the
original plan [#]_. No other feature single-handedly added as much technical
debt into our product. From this point on, nearly every feature had a
significantly increased complexity with much less certainty in how it should be
implemented when brought forward by the people in charge of the business. I
consider this to be first turning point of how we managed our project.

.. class:: aside

    I don't remember if this was before or after the initial pivot into full
    SD-WAN features, but even it was before we weren't properly following it at
    that point in time.

We went to a seminar about using scrum for project management where we played
with all the stereotypical things like sticky notes in swim lanes and assigning
story points to things based on the fibonacci numbers. We adopted the parts of
it we could and officially adopted Scrum.

Scrum, and how it didn't quite work for us
-------------------------------------------

At the beginning scrum seemed great. We could just plan a bit ahead of where we
were and hopefully spend less time planning months of features all in one go.
The business didn't quite let us adhere to it perfectly though. At this point
in time, the software development team was also the technical support team.
This made the number of hours the development team could spend every scrum
period (we did 2 weeks) very variable, which conflicts with some of the core
concepts of scrum of getting very predictable work loads.

.. class:: aside

    This was quite a while ago now, maybe around 2015 or 2016 so I'm not sure
    how accurate this information will be.

Scrum is slightly ill-defined in what to do if you complete all the work in a
sprint or when something urgent like a bug in a currently released project
comes in. We would consistently have to add new stories to our sprints, and
sometimes due to our inconsistent development hours, we would run out of
stories before the sprint period was complete.

Our backlog grew and we were spending more time trying to manage scrum than we
wanted to, and didn't seem to be getting the right stuff out of. Something had
to change. We had enough features planned for many years at our current rate of
development with more still being added.

In come the yes-men
--------------------

.. class:: aside
.. [#]

    I think the original intention would be that if we finished everything in a
    scrum sprint earlier, that we would use that time to work on more
    experimental or less defined features. It seems now to encourage only doing
    this type of work if you happened to underestimate the current week's
    stories.

We ended up getting a consultant that teaches other companies how to do project
management to help us figure out what we were doing wrong. They went over scrum
and more generically agile and when we brought up our complaints with scrum
they agreed, and suggested that scrum isn't the right fit and something that
allowed for our level of interruptions and changing priorities more. This is
where we switched to something that was like scrum but less strict. We would
have our planned work still, and that was never supposed to change. We added a
new board to our JIRA called "Innovation" [#]_, but it was innovation in name only.
The innovation board was where every interruption went and ensured that the
normal planned work board stayed still.

For a while this seemed like it was working. But after a few months we realized
it was just scrum with a different coat of paint and our issues spread across 2
projects making it harder for everyone involved to exactly tell what was going
on.

.. class:: aside

    I never realized how easily it is to fall into this "yes-man" trap.

Looking back at the consultants, I don't think they gave us any useful
information, they just agreed with everything we said and we had to spend a lot
of time undoing everything they proposed we add to our processes and tooling.

One good thing to come from this is we just gave up on our old project with
years worth of planned work and made a new one, although it did start to grow
until we got more strict about things, which brings us to…

Weighted Kanban
----------------

We realized that the so-called "Innovation" board was working pretty well for
the work that ended up there. It was managed mostly like Kanban but we kept the
story points since many issues had greatly differing complexities associated
with them. The story points would mean a lot less than they do in scrum, but
they let us stay looser with our planning on things that were incredibly
coupled while still breaking apart things that we could. We also have an
understanding that if we try and rate a story with too high of a complexity
that perhaps we should instead spend some more time figuring out why we don't
know how to break it apart.

We have been using this for a few years now and it has really helped.

With this approach we try to keep as many tasks as possible at around a relatively low
complexity. I think in a perfect world a story should be completed in under a
day, with a full peer review. We do allow for tasks to take longer but if a
task gets over a week of time logged against I know that something went wrong
in planning. Maybe we needed to spend more time researching or maybe something
from the nearly decade-old codebase crept up and complicated matters.

.. class:: aside
.. [#]

    https://nvd.nist.gov/vuln/detail/CVE-2019-14899

With a smaller set of planned work we are able to still follow Kanban enough
that we can be reactive to changes in the landscape, whether its a problem
discovered in our software, a problem discovered in our domain [#]_, or an exciting
new feature.

.. class:: aside
.. [#]

    Time estimates are the single-hardest part of my job to get right. Breaking
    down complicated features into smaller sub-features is sometimes the best
    you can do. At least then you are probably slightly less wrong on a bunch
    of smaller things.

With the current system we now don't plan too far ahead and always try to have
enough research done for upcoming features that we can roughly estimate [#]_
what is involved in many features. We still get it wrong but I think that you
always will. With our new approach we can tell that we got it wrong much
earlier to let the business figure out how to handle it earlier into development.

.. class:: aside
.. [#]

    We have an ordered list of features that we work our way through.

Our general process goes something like this:

#. The business proposes a feature, like "send traffic directly out an internet
   connection, instead of through link aggregation"
#. We look at it, and plan some stories to figure out what we don't know about
   the feature. Sometimes we are already quite familiar with the requested
   functionality and skip this step.
#. We give a rough time estimate back to the business, and ask how this feature
   request ranks to any other. The business tends to weight the priorities of
   features based on how long they might take to complete. [#]_
#. We further break out and plan features as they get to the top of the list of
   requested features


.. class:: aside
.. [#]

    Did you know the "R" in R&D stands for research?

From the project manager to the development team everyone seems happy with this
current process. We spend less time planning out features that eventually get
cancelled and more time researching [#]_ ways to improve our product or better
implement features.
