import sys
from argparse import SUPPRESS, Action, FileType

from fucko import default_forward_path


def config_alias(key):
    return dict(
        type=lambda value: f"{key}={value}",
        dest="config",
        action="append",
        help=f"alias for -c {key}=...",
        default=SUPPRESS,
    )


class commands:
    def build(parser):
        """ build the internets -- this is probably what you want """
        parser.add_argument(
            "--show",
            action="store_true",
            help="dump the ninja file to stdout instead of running it",
        )
        parser.add_argument("--fwd", **config_alias("build.fwd"))
        parser.add_argument("--fork", **config_alias("build.fork"))
        parser.add_argument("ninja_args", nargs="*")

    def serve(parser):
        """ start a simple http server, watch paths for changes, rebuild on change """
        parser.add_argument("--host", default="0.0.0.0", help=" ")
        parser.add_argument("--port", default=8011, help=" ")
        parser.add_argument(
            "--open",
            action="store_true",
            help="this JUST runs `xdg-open http://<host>:<port>` ... srsly how lazy are you my dude",
        )

    def host(parser):
        """open a unix socket for command forwarding

        you probably don't want to use this unless you're debugging something"""
        parser.add_argument(
            "--path", default=default_forward_path(), help="socket path"
        )
        parser.add_argument("--fork", **config_alias("build.fork"))

    def organize(parser):
        """for each reStructured Text document listed on the command line,
        move the file to yyyy-mm-dd-title/foo.rst based on date & title"""
        parser.add_argument("--format", **config_alias("paths.dated"))
        parser.add_argument(
            "-n",
            "--dry-run",
            action="store_true",
            help="don't do anything, just describe what would happen -- highly recommended",
        )
        parser.add_argument(
            "--into",
            help="destination directory to organize under, by default files are organized under the directory they're found",
        )
        parser.add_argument("rst", nargs="*")

    def pickle_rst(parser):
        """ used by build to cache rst documents """
        parser.add_argument("rst")
        parser.add_argument("meta")
        parser.add_argument("body")

    def render(parser):
        """ used by build to render mako templates """
        parser.add_argument("--depfile", type=FileType("w"), nargs="?")
        parser.add_argument("-o", "--output", type=FileType("w"), default=sys.stdout)
        parser.add_argument("terms", type=assigners)
        parser.add_argument("template")
        parser.add_argument("pickles", nargs="*", type=FileType("rb"))

    def feedme(parser):
        """ used by build to generate an atom/rss feed """
        parser.add_argument("--pretty", action="store_true")
        parser.add_argument("--atom", type=FileType("wb"))
        parser.add_argument("--rss", type=FileType("wb"))
        parser.add_argument("pickles", nargs="*", type=FileType("rb"))

    _lookup = {
        k.replace("_", "-"): v for k, v in locals().items() if not k.startswith("_")
    }


command_map = commands._lookup


def assigners(terms):
    """
    this is honestly some stupid fucking shit i don't know why i've done this
    to myself

    TODO this is actually fucking stupid, the un-pickled data should just be
    sent as an argument to the template or function and handled there in
    regular boring Python ...

    >>> assigners("foo")({}, iter(range(1)))
    {'foo': 0}
    >>> assigners("foo, bar")({}, iter(range(4)))
    {'foo': 0, 'bar': 1}
    >>> assigners("foo, bar[:]")({}, iter(range(4)))
    {'foo': 0, 'bar': [1, 2, 3]}
    >>> assigners("foo, bar[:]")({}, iter(range(1)))
    {'foo': 0, 'bar': []}
    """
    import ast

    expr = ast.parse(terms, mode="eval")
    return _expr_assigner.from_item(expr.body)


class _expr_assigner(object):
    def __init__(self, item, variant):
        self.item = item
        self.variant = variant

    def __call__(self, ctx, values):
        self.variant(self, ctx, values)
        return ctx

    def _variant_name(self, ctx, values):
        ctx[self.item.id] = next(values)

    def _variant_subscript(self, ctx, values):
        slice = self.item.slice
        attr = self.item.value.id
        if slice.upper is not None:
            values = (next(values) for _ in range(slice.upper))
        ctx.setdefault(attr, []).extend(values)

    def _variant_tuple(self, ctx, values):
        for assigner in self.item:
            assigner(ctx, values)

    @classmethod
    def from_item(assigner, item):
        import ast

        if isinstance(item, ast.Tuple):
            return assigner(
                [assigner.from_item(item) for item in item.elts],
                assigner._variant_tuple,
            )
        elif isinstance(item, ast.Name):
            return assigner(item, assigner._variant_name)
        elif isinstance(item, ast.Subscript):
            sl = item.slice
            if sl.lower is not None or sl.step is not None:
                raise ValueError("only [:] or [:N] slices are supported")

            if isinstance(item.value, ast.Name):
                # can only slice on names ...
                return assigner(item, assigner._variant_subscript)
            else:
                raise NotImplementedError(ast.dump(item.value))
        else:
            raise NotImplementedError(ast.dump(item))
