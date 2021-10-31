import pickle

from feedgen.feed import FeedGenerator  # type: ignore
from fucko import is_relative_uri, logging
from fucko.cfg import get_config

logger = logging.getLogger(__name__)


def feedme(args):
    """ use https://validator.w3.org/feed/check.cgi to make sure it's right """
    cfg = get_config()

    site_url = cfg.site.url
    site_name = cfg.site.name

    if is_relative_uri(site_url):
        logger.warning("[site].url must be absolute, feed will NOT be valid")

    fg = FeedGenerator()
    fg.id(f"{site_url}/")
    fg.title(site_name)
    fg.link(href=f"{site_url}/")

    pickles = map(pickle.load, args.pickles)
    pairs = ((p, next(pickles)) for p in pickles)
    for post, body in pairs:
        self = f'{site_url}/{post["rstpath"].parent.stem}'
        author = post.get("author") or cfg.site.author

        fe = fg.add_entry()
        fe.id(self)
        fe.link(href=self)
        fe.title(post["title"])
        fe.published(post["date"])
        if "updated" in post:
            fe.updated(post["updated"])
        if author:
            fe.author(name=author)  # TODO support email?
        else:
            logger.warning(
                "%s is missing an author, feed will NOT be valid", post["rstpath"]
            )
        if "summary" in post:
            fe.summary(post["summary"], type="html")
        fe.content(body, type="html")

    if args.rss:
        fg.description(site_name)
        fg.link(href=f"{site_url}/{cfg.site.rss}", rel="self", replace=True)
        args.rss.write(fg.rss_str(pretty=args.pretty))

    # TODO why even support this? why both? what the fuck?
    if args.atom:
        fg.link(href=f"{site_url}/{cfg.site.atom}", rel="self", replace=True)
        args.atom.write(fg.atom_str(pretty=args.pretty))
