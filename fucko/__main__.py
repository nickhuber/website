import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from contextlib import contextmanager

from fucko import NotAFileError, clocked, fdfilepath, logging
from fucko.boingo import command_map
from fucko.cfg import load_config_from_file

logger = logging.getLogger(__package__)


def main(argv=None):
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args_configure_logging(argv)

    with maybe_pdb_context(args):
        load_config_from_file(args)

        boingo_mod, boingo_fn = import_boingo(args.action)
        extra = boingo_prefork(args.action, boingo_mod, args)
        with clocked("run", action=args.action):
            boingo_fn(args, *extra)

        raise SystemExit(0)


def parse_args_configure_logging(argv):
    if argv:
        prog, *args = argv
    else:
        prog, args = None, None

    parser = ArgumentParser(prog=prog, formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--pdb", action="store_true")
    parser.add_argument(
        "--log",
        choices=logging.CHOICES,
        default="info",
        help="logging filter",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="append",
        default=[],
        help="override an option in www.toml ... ex. -c paths.out=/tmp/bananas",
    )
    subs = parser.add_subparsers(dest="action", required=True)

    for name, parser_setup in command_map.items():
        subp = subs.add_parser(
            name,
            help=parser_setup.__doc__,
            description=parser_setup.__doc__,
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        parser_setup(subp)
        subp.set_defaults(action=name.replace("-", "_"))

    args = parser.parse_args(args)

    logging.getLogger().setLevel(getattr(logging, args.log.upper()))
    logger.debug(args=args)
    return args


def import_boingo(name):
    with clocked("import", boingo=name):
        mod = __import__(f"{__package__}.boingo", fromlist=(name,))
    mod = getattr(mod, name)
    fn = getattr(mod, name)
    return mod, fn


def boingo_prefork(name, mod, args):
    if hasattr(mod, "prefork"):
        with clocked("prefork", boingo=name):
            return mod.prefork(args)
    else:
        return ()


@contextmanager
def maybe_pdb_context(args):
    if args.pdb:
        from pdb import post_mortem
    try:
        yield
    except Exception:
        if args.pdb and sys.stdout.isatty():
            logger.exception("entering pdb...")
            post_mortem()
        else:
            logger.exception("Failed doing a thing", action=args.action)

        # this is pretty aggressive ... TODO
        # if something like pickle-rst fails, it still creates the output
        # files, so ninja thinks it worked?  using a temporary output file
        # might fix that & the sponge/restat problem that requires cp-compare
        unlink_output_args(args)

        raise SystemExit(1) from None


def unlink_output_args(args):
    for var, val in vars(args).items():
        if hasattr(val, "mode") and "w" in val.mode:
            try:
                os.unlink(fdfilepath(val.fileno()))
            except NotAFileError:
                continue
            except (ValueError, OSError) as err:
                logger.error("could not clean up %s: %s", var, err)


if __name__ == "__main__":
    with clocked("main"):
        main()
