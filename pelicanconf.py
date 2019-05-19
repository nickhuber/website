#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Nick Huber'
SITENAME = "Nick Huber"
SITEURL = ''

PATH = 'content'

TIMEZONE = 'America/Vancouver'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

STATIC_PATHS = [
    'images',
    'extra',
]

EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/favicon.ico': {'path': 'favicon.ico'},
}

# Blogroll
LINKS = ()

# Social widget
SOCIAL = (
    ('github', 'https://github.com/nickhuber/'),
    ('bitbucket', 'https://bitbucket.com/nhuber/'),
    ('youtube', 'https://www.youtube.com/channel/UCYFRJqnrSddXDQCKOZbPd7g'),
)

DEFAULT_PAGINATION = 10
PAGINATION_PATTERNS = (
    (1, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html'),
)
THEME = './theme'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True