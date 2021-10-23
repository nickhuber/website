#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = "Nick Huber"
SITENAME = "Nick's blog"
SITEURL = ""

PATH = "content"

PLUGIN_PATHS = ["."]
PLUGINS = ["pelext"]

STATIC_PATHS =["images"]

DATE_FORMATS = {"en": "%A, %-d %B %Y"}

TIMEZONE = "America/Vancouver"

DEFAULT_LANG = "en"

DOCUTILS_SETTINGS = {"smart_quotes": True, "footnote_references": "superscript"}

STATIC_PATHS = ["images"]
ARTICLE_URL = "{category}/{slug}/"
ARTICLE_SAVE_AS = "{category}/{slug}/index.html"
CATEGORY_URL = "{slug}/"
CATEGORY_SAVE_AS ="{slug}/index.html"
PAGE_URL = "{slug}/"
PAGE_SAVE_AS ="{slug}/index.html"

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

LOGO = "theme/logo.jpg"

# Blogroll
LINKS = ()

# Social widget
SOCIAL = (
    ("github", "https://github.com/nickhuber/"),
    ("youtube", "https://www.youtube.com/channel/UCYFRJqnrSddXDQCKOZbPd7g"),
)

DEFAULT_PAGINATION = 10
PAGINATION_PATTERNS = (
    (1, '{url}', '{save_as}'),
    (2, '{base_name}/page/{number}/', '{base_name}/page/{number}/'),
)
THEME = "./theme"

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True