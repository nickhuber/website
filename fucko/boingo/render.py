from fucko import TOP_DIR, clocked, depickle_terms_into_context, fdfilepath, logging
from fucko.cfg import get_config
from mako.lookup import TemplateLookup  # type: ignore
from mako.template import Template  # type: ignore

logger = logging.getLogger(__name__)

template_cache = {}


def get_template(filename, depfile=None):
    if filename not in template_cache:
        l = TemplateLookup(directories=[TOP_DIR])
        # If this is cached without dep tracking and then later someone tries
        # to use it expecting tracking that could be unfortunate ...
        if depfile is not None:
            l = TrackDepsTemplateLookup(l)
        t = Template(filename=filename, strict_undefined=True, lookup=l)
        template_cache[filename] = t
        return t
    else:
        return template_cache[filename]


def prefork(args):
    with clocked("load template"):
        return (get_template(args.template, args.depfile),)


def render(args, t: Template):
    if args.depfile:
        deps: set = t.lookup.deps
        deps.clear()

    config = get_config()
    context = {
        "SITE": config.site,
        "PATHS": config.paths,
    }

    with clocked("depickle"):
        depickle_terms_into_context(context, args.terms, args.pickles)

    with clocked("render & write"):
        args.output.write(t.render_unicode(**context))

    if args.depfile:
        try:
            target = fdfilepath(args.output.fileno())
        except ValueError as e:
            raise ValueError(f"could not get depfile build rule target: {e}") from None
        write_makefile_deps(args.depfile, target, deps)


def write_makefile_deps(file, target, deps):
    print(f"{target}: {' '.join(deps)}", file=file)


class TrackDepsTemplateLookup(object):
    """ a mako.TemplateLookup that records every get_template """

    def __init__(self, inner):
        self.inner = inner
        self.deps = set()

    def adjust_uri(self, *args, **kwargs):
        return self.inner.adjust_uri(*args, **kwargs)

    def filename_to_uri(self, *args, **kwargs):
        return self.inner.filename_to_uri(*args, **kwargs)

    def get_template(self, uri):
        self.deps.add(uri)
        return self.inner.get_template(uri)
