from pathlib import Path

import docutils.nodes
from fucko import is_relative_uri, logging, slugify
from fucko.cfg import get_config
from fucko.rstutil import (
    document_metafields,
    document_resources,
    parse_datetime,
    path_publisher,
    traverse,
)
from markupsafe import Markup

logger = logging.getLogger(__name__)


def organize(args):
    cfg = get_config()

    if not cfg.paths.dated:
        logger.error("no date format in [paths].dated; can't do anything")
        raise SystemExit(1)

    datefmt = cfg.paths.dated

    if args.dry_run:
        logger.info("dry run ... not actually do anything; just pretending")

    into = Path(args.into) if args.into else None

    for rst in args.rst:
        pub = path_publisher(rst)
        doc = pub.reader.read(pub.source, pub.parser, pub.settings)

        title = next(traverse(doc, docutils.nodes.title), None)
        if title is None:
            logger.error("no title found; skipping", rst=rst)
            continue

        slug = slugify(Markup(title.astext()).striptags().lower())

        for name, value in document_metafields(doc):
            if name == "date":
                value = parse_datetime(value)
                break
        else:
            logger.error("date field missing from %s", rst)
            continue

        path = Path(rst)
        newdir = (into or path.parent) / value.strftime(datefmt).format(slug=slug)
        newpath = newdir / path.name

        if path == newpath:
            logger.debug("skipping since source matches destination: %s", path)
            continue

        if not args.dry_run:
            newdir.mkdir(parents=True, exist_ok=True)
            with newpath.open(mode="x") as f:
                path.rename(newpath)

        logger.info("%s -> %s", path, newpath)

        for res in filter(is_relative_uri, document_resources(doc)):
            respath = path.parent / res
            if respath.exists():
                newres = newdir / res
                if not args.dry_run:
                    respath.rename(newres)
                logger.info("%s -> %s", respath, newres)
            else:
                logger.warning("%s referenced %s but %s does not exist", rst, res, respath)
