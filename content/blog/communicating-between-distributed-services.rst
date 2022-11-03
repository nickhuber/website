Communicating Between Distributed Services
===========================================

:date: 2022-10-31
:category: Blog
:slug: communicating-between-distributed-services
:summary: Reflecting on some various ways I have communicated between services of various sizes

Over the years I have witness and been involved with various ways of
communicating between services. It has varied from specific communication
between several larger services in a `service-oriented architecture`_ pattern or
something more akin to an event driven `microservice architecture`_. I thought
it might be fun to reflect on them and give some of my opinions.

PostgreSQL NOTIFY events
-------------------------

.. class:: comment

  Why use many service when few service do trick

It has been several years since I looked at this way of doing things. I tried to
refresh myself by reading the docs but take this section with a grain of salt.

Perhaps not truly event-driven, PostgreSQL can act as somewhat of an event
source for an event-driven architecture. The problem I saw being solved was
pushing out configuration updates to various clients, tracked in a table that
maybe looked something like this

.. code-block:: sql

    CREATE TYPE configuration_update_status AS ENUM ('pending', 'in_progress', 'complete', 'failed');
    CREATE TABLE configuration_update (
        id serial PRIMARY KEY,
        content jsonb,
        status configuration_update_status,
        destination inet
    );

Whenever a configuration update is created, it is inserted into this table with
a status of `pending` along with a
`pg_notify('configuration_update_created', <configuration_update_id>);` and a
client program would use `LISTEN configuration_update_created;`. The client
program would then do something like this after receiving an event from
`LISTEN` to find the configuration update, and all the details about it needed
to push it out to the desired client.

.. code-block:: sql

    SELECT id, content, status, destination
    FROM configuration_update
    WHERE id = %s AND status = 'pending'

Since PostgreSQL's `NOTIFY` only signals in realtime, if your client is not running
when the `NOTIFY` is sent then no event will be read. So the startup case needs
to be handled by doing something like
`SELECT * FROM configuration_update WHERE status = 'pending';` to get a list of
all pending configuration updates and process them

Benefits
^^^^^^^^^
* If you are already using PostgreSQL, you don't need to run any extra
  infrastructure
* The syntax is pretty simple
* Application sending the notification doesn't care about who consumes it

Drawbacks
^^^^^^^^^^
* Handling the startup case to process any missed messages
* `pg_notify(channel, message)` events are sent to every session that has
  `LISTEN channel`, making scaling of consumers more complicated.

Apache Kafka
-------------

.. class:: comment

  If everyone else is using it, it must be a good idea

Its hard to talk about event driven microservices and not consider something
like Kafka. Kafka and its ecosystem gives you a lot of power and tooling to
design and develop this sort of architecture. My experience with Kafka as to use
it as the foundation for building an application to manage some workflows around
onboarding customers onto a platform.

When starting with Kafka things seemed easy. Some application produces an event
encoded as JSON to some named topic like `order-created` and have some other
application consumes from that same topic and processes the created order.

Schema Handling
^^^^^^^^^^^^^^^^

The first complexity came from trying to ensure that the data being received
matched the expected schema. I added some JSON Schema validation on the consumer
but this was a bit annoying because multiple consumers would have to define the
same schema if consuming from the same topic. Confluent has a solution for this
that they call the `Schema Registry`_. This ends up being a fairly simple
solution where each Kafka message is prepended with 5 bytes, a 1 byte magic
number and a 4 byte ID of the schema and then the consuming application can
lookup and cache the schema by ID. Schemas are Apache AVRO and can be configured
with various levels of forwards/backwards evolution rules.

This works well, the Schema Registry API is easy to use and you can define a
minimal set of the schema that the consumer actually cares about to keep your
application focused on its task. Since you can decide on schema evolution
compatibility rules you get to decide if you want to allow breaking changes or
not. Not allowing breaking changes means that you may need to introduce a new
Kafka topic when that becomes required which is a pain if there are many
services consuming from the topic being deprecated, however breaking the schema
has the same sort of problem where all of the consumers of the topic need to be
updated to support the breaking change before it can be used.

Some tools like ksqlDB_ support the schema registry, but they do so by auto
generating schemas with every field defaulted to null to make schema evolutions
simple. In my mind this loses a lot of the benefits of using a schema since you
can't actually be sure what is required or not on a message coming from a schema
like this.

Topic Partitioning
^^^^^^^^^^^^^^^^^^^

Kafka topics have a setting called a partition, which is effectively how many
queues there are for that topic. A message published to a topic is hashed based
on its key and assigned to a partition so that all messages that share a key
will be in the same partition. When a consumer subscribes to a topic Kafka will
balance the partitions between all of the consumers, this is part of how a
distributed application using Kafka can scale to handle a change in workload.
It's pretty easy to raise the partition count on a topic with Kafka, but
decreasing is not supporting and would involve creating a new topic to handle
the events.

I have left out much of the finer details because this isn't really a tutorial
on Kafka partitions just enough to get enough of an understanding for now.

The problem I ran into was not knowing how many partitions should be set on a
topic. The more partitions you have the more consumers on any particular
consumer group you can have however the more partitions you have the more load
you put on the Kafka server. If you know your expected event throughput and how
long handling each message should take you can derive an expected partition
count but for a new or growing application that may not make any sense. One a
new application with unknown throughput I figured I would just set the
partitioning to 1 to keep it simple and change it after observing any delays in
the various topics.

The plan was complicated with the use of ksqlDB_, which requires defining the
partitions when you use it and will fail if you alter them under its hood. Maybe
I probably misunderstand something around partitions or maybe ksqlDB is still
too much of a work in progress to use yet but I don't know how you are expected
to manage it with this limitation.

Benefits
^^^^^^^^^
* Lots of tooling
* A common way of manage events between services
* Applications producing events don't care about who consume them
* Events are persisted so new consumers can be started up to read from the
  earliest events and stay consistent without being a special case

Drawbacks
^^^^^^^^^^
* Complex to run and manage
* Easy to run into scenarios that can be difficult to change

Webhooks / HTTP RPC
--------------------

.. class:: comment

  Let's add some network latency onto this function call, that will speed things
  up!

Instead of abstracting away the producer from the consumer, why not just call
them directly? Having your producer call a HTTP endpoint on another service
seems like a simple solution to distributing load and responsibilities between
services.

Despite sounding simple ths has some pretty serious drawbacks:

1. The sender must know which service(s) need to know about something happening,
   this adds coupling between services.
2. The task of sending a webhook can't be considered complete until the
   recipient has acknowledged it, making the task blocking or deferred into
   another thread or some other complicated solution.
3. How do you handle the sender terminating before the webhook has been
   successfully sent? A message broker simplifies this by relying that the
   broker will be available even if the consumer is not.

Assuming the service wanting to receive the event is already a web server, the
main benefit this gives is not requiring any extra dependencies on a another
system like a message broker or database.

Benefits
^^^^^^^^^
* Easy to get started

Drawbacks
^^^^^^^^^^
* Application sending a webhook has to choose which application receives it,
  adding coupling between services
* Nothing inherently handles If the sending application closing before the
  webhook is received, the event would need to be resent
* Sending webhooks can be a blocking event in some systems, or add complexity in
  an otherwise synchronous scenario.

Conclusions
------------

Like most things, there is not a definitive "do this" solution. If you need to
signal a configurable, external service about something happening a webhook
could be a good solution to that problem. If you want to do a lot of stream
processing on data then Kafka and its toolset offers a lot to help you out. If
you have a simple, small setup that already uses PostgreSQL maybe using
`NOTIFY`/`LISTEN` will handle you well, but if you want to keep a record of
every event emitted and who consumed it something like Kafka might be more of a
fit.

I think the thing I have learned the most is that you shouldn't go into problem
solving with a particular method just for the sake of it. You should understand
the benefits and drawbacks of different architectures and tools and pick
something that fits the scenario.

I have seen "bad" solutions work and "good" solutions struggle so it all does
come back to focusing on what is important to solving your problem. Why rewrite
a monolithic service with an event system when your core problem is somewhere
else? Why start a project with event-driven microservices when your throughput
is expected to be fewer than 100 events a day?

.. _ksqlDB: https://ksqldb.io/
.. _`Schema Registry`: https://docs.confluent.io/platform/current/schema-registry/index.html
.. _`service-oriented architecture`: https://en.wikipedia.org/wiki/Service-oriented_architecture
.. _`microservice architecture`: https://en.wikipedia.org/wiki/Microservices
