import pickle
import re
from contextlib import contextmanager, nullcontext
from pathlib import Path

import docutils.nodes
import pygments.lexers  # type: ignore
from fucko import clocked, is_relative_uri, logging, net, rsthacks, write_if_changed
from fucko.rstutil import document_metadata, document_resources, path_publisher

logger = logging.getLogger(__name__)


def prefork(args):
    with clocked("rsthacks"):
        rsthacks.compile_patterns()
    del globals()["prefork"]
    return ()


def pickle_rst(args):
    with clocked("publish", rst=args.rst):
        pub = path_publisher(args.rst)
        pub.publish()

    # Warn if resource don't point to real files?
    # Actually copying to the output path happens for every non-rst file in the ninja file
    rstpath = Path(args.rst)
    for res in filter(is_relative_uri, document_resources(pub.document)):
        respath = rstpath.parent / res
        if not respath.exists():
            logger.warning(
                "%s referenced %s but %s does not exist", args.rst, res, respath
            )

    meta = {"title": pub.writer.parts["title"] or rstpath.stem, "rstpath": rstpath}
    meta.update(document_metadata(pub.document))

    body = pub.writer.parts["body"]

    with clocked("pickle"):
        with write_if_changed(args.meta) as f:
            pickle.dump(meta, f, protocol=pickle.HIGHEST_PROTOCOL)
        with write_if_changed(args.body) as f:
            pickle.dump(body, f, protocol=pickle.HIGHEST_PROTOCOL)
