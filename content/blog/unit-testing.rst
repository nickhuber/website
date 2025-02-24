Unit Testing
=============

:date: 2025-02-23
:category: Blog
:slug: unit-testing
:summary: Some ideas on how to better manage data in testing scenarios

Over my many years in software development I have seen many different flavours
of unit testing for database driven applications. I intend to highlight some
bad practices that should be avoided and propose what I assert is a strong
foundation to build various unit tests on.

As with all things, there are no absolute rules here but I will point out
numerous shortcomings in common approaches when it comes to writing a good,
focused unit test.

This article is going to use the following (kind of terrible) database
definition of a hosted blog platform to showcase various examples:

.. code-block:: sql

    CREATE TABLE users (
      user_id integer PRIMARY KEY,
      name text
    );

    CREATE TABLE blogs (
      blog_id integer PRIMARY KEY,
      creator_id integer REFERENCES users (user_id)
    );

    CREATE TABLE articles (
      article_id integer PRIMARY KEY,
      blog_id integer REFERENCES blogs (blog_id),
      name text,
      content text,
      is_draft boolean
    );

    CREATE TABLE comments (
      comment_id integer PRIMARY KEY,
      article_id integer REFERENCES articles (article_id),
      poster_id integer REFERENCES users(user_id),
      content text
    );

No fixtures
------------

The simplest anti-pattern to fall in to is defining the full data requirements
inline in each test. This has the benefit of only defining exactly what you
need but makes it unclear what data the test is actually intending to assert
on.

This is an example with a pretend ORM showing how this may look

.. code-block:: python

    def test_can_add_comment_to_article():
        user = User(name="Test User").save()
        blog = Blog(creator=user, name="Test Blog").save()
        article = Article(
          blog_id=blog.id,
          name="Test Article",
          content="Test Content"
        ).save()
        comment = create_comment(
          article_id=article.id,
          user_id=user.id,
          content="This is a test comment"
        )
        assert article.comments.first().id == comment.id


This function has to create so much overhead that is unrelated to the comment.
The problem only gets worse as more test are added, or the object under test
requires more parent objects to be created. As more tests are created for more
deeply nested schemas the boilerplate code to setup each test will overwhelm and
mask any actual intended logic in the tests.

Database defaults
------------------

Looking at the above example you may think most of it could be solved by
creating a user, blog and article in some base default database definition.
This can work nicely in the short term but inevitably leads to complicated
tests as some tests need to lookup and adjust values on per-existing data.

.. code-block:: python

    def test_can_add_comment_to_article():
        comment = create_comment(
          article_id=1,
          user_id=1,
          content="This is a test comment"
        )
        assert article.comments.first().id == comment.id

    def test_cant_add_comment_to_draft_article():
        # Update the article to be a draft
        article = get_article(id=1)
        article.update(is_draft=True)
        comment = create_comment(
          article_id=article.id,
          user_id=1,
          content="This is a test comment"
        )
        assert article.comments.first().id == comment.id

The second test could also use a different article fixture which was already in
draft status but that pattern can drastically increase the size of your test
database template, as every new configuration of your objects needs to be
defined ahead of time to maybe be used by some tests. It also does not help
solve the problem of defining the data under test far apart from the test
itself.

Fixtures
---------

A common solution to both of the previous problems is to use something like
`pytest fixtures <https://docs.pytest.org/en/7.1.x/how-to/fixtures.html>`_.
These let you define some data definition and allow it to be reused between
whatever tests care about it. This has a few downsides which are not
immediately obvious:

- Each fixture can only be created once per test, so tests that want to do
  assertions on multiple objects without caring much about the content in the
  objects will either need a custom fixture that generates multiple objects or
  using other specific fixture implementations even though the test doesn't
  care about those specifics.
- The data under test is abstracted from the test. Even though the fixture name
  hopefully describes what it is creating it is still a level removed from the
  test itself.
- Easy to end up with many bespoke versions of each object fixture, and these
  fixtures can easily end up only being used once.

Mocked database
----------------

.. note::
    This section is more focused on the case of already having a managed way of
    accessing data, such as using Django's ORM.

You may think to yourself, "Self, the database is another system and a unit
test should testing only a single unit; so why not mock or abstract away the
concept of the database entirely?". To this I say that you are going to invest
a lot of time and complexity into managing a lot of mocked interfaces and
hoping you are still actually testing anything that hasn't been mocked, or you
are going to complicate your application by adding another layer of indirection
from the data. Generally the database is such a crucial dependency of the
application that trying to remove it from the tests is going to do more harm
than good.

Factories
----------

Now to finally mention what I believe is the best method at managing your test
data: factory functions. These are parameterized functions with some sensible
defaults to allow the developer to define strictly what is needed for the test
without needing to define the entire object.

Ideally a test should describe exactly what data it needs so it is clear to the
writer and reader of a test what it is attempting to assert.

.. code-block:: python

   def article_factory(blog=None, content="Test Content"):
       # Allow the user to supply a blog if necessary, otherwise just make one
       if blog is None:
           user = User().save()
           blog = Blog(creator=user).save()
       return Article(blog=blog, content=content).save()

    def test_can_add_comment_to_article():
        # Despite the article content being required, we don't care about it
        # for this test so it is left unset.
        article = article_factory()
        comment = create_comment(
          article_id=article.id,
          user_id=1,
          content="This is a test comment"
        )
        assert article.comments.first().id == comment.id

This ends up acting very similar to the fixtures example, except all custom
data definitions are explicitly described where they are needed. You can also
use this one factory definition to create as many versions of copies of a thing
the specific test may call for.
