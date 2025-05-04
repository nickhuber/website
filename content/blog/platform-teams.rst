The problem with platform teams
================================

:date: 2025-05-03
:category: Blog
:slug: the-problem-with-platform-teams 
:summary: Dividing responsibilities the wrong way, and making everything worse

For a while I have been wanting to write about my concerns about what having a
dedicated "DevOps" team can cause but could never fully determine why I thought
that way. Recently I have expanded my viewing of the problem to include the
concept of a "platform" team and I think it helped me put things into a better
focus.

What is a platform team?
-------------------------

A platform team is a group of people who do not work on the features that solve
the problem of your business, but instead are directed with managing things
like the infrastructure, global and/or generalized planning, shared libraries
or services that are used within a software stack.

I want to break this into 2 main categories:

1. An infrastructure-focused team
2. Everything else

This is because I have observed some more specific issues into how
infrastructure is managed than the rest of the platform team problem.

Platforms teams aren't inheritely evil and are created out of a sense of
purpose. Maybe years of short sighted decisions have let technical debt get to
a breaking point or these ideas could be brought in from a new hire intendeding
to add some lacking technical expertise to a growing company.

Infrastructure
^^^^^^^^^^^^^^^

The most common name for a team like this is "DevOps", but DevOps is more of a
culture or paradigm than a team. If you create a team called DevOps you almost
certainly aren't realizing the potential of DevOps; you are just have what
would tradionally be called the operations team.

This style of platform team will be less knowledge about your business
domain-specific problems and focus on solving generic infrastructure related
problem — cloud cost optimizations, kubernetes upgrades, CI pipelines, etc.
Things may even get to the point where everything is working well for the
current business size but the infrastructure team needs something to do, so
they will find something: replacing services or tools with competitors because
things might be better or planning large and disruptive changes to handle
unrealized and unexpected levels of load.

This team will almost inevitably end up conflicting with feature work by
introducing or modifying core actions (deployments, migrations, scripts, data
access, etc) in such a way that they require special attention from themselves,
since they don't grasp the domain concept the code is being run for.

Everything else
^^^^^^^^^^^^^^^^

I have seen these kinds of teams fall under various names:

* Platform
* Architecture
* Integration

I consider these teams "gatekeepers". The gatekeepers have a disconnected view
on reality from that of a developer building a feature, or a product manager
planning a feature: they are on a never-ending quest to adjust the tools and
set the standards to be used by the people designing and implementing features.
A gatekeeper will have grandeous plans for "the future" and will try to block
or delay work from being done that doesn't align with their vision.

The gatekeeper is so focused on doing things "right" the first time and will
introduce and enforce all sorts of process to achieve this goal. They will
inject themselves into new, often manual, processes that they don't have time
for which solve problems that don't exist. Even after the gatekeeper leaves the
company, the processes will likely persist with no one questioning why any of
this is done.

The worst part about the gatekeeper is everything they say and do can sound
correct, and will often be backed by so-called "industry best practices". The
problem is that they introduce their solutions without considering things like
how the team works, the size of the team or what the actual trade off from
things like risk tolerance vs velocity need to be. These things are all very
important, especially in a startup environment where getting something done the
"wrong" way fast is more important than doing it the "right" way slowly.

Conclusion
^^^^^^^^^^^

This ended up being a bit of a rant about how people can be placed into roles
where they may (hopefully inadvertently) end up causing more harm than good to
the organization that implemented this role. I hope that maybe at least 1
person will think twice about why a process is in place or if making a platform
team is actually needed to solve real business problems.
