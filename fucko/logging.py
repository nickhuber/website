import sys

from fucko import ansi

BUTT = DEBG = DEBUG = 0
TIME = 1
INFO = 2
WARN = WARNING = 3
CRIT = CRITICAL = ERROR = 4  # ehh ... who cares..

# includes aliases
ALL_LEVEL_NAMES = set(k.lower() for k in globals().keys() if k.isupper())
# indexed by level value
LEVEL_NAMES = ["BUTT", "TIME", "INFO", "WARN", "CRIT"]
LEVELS = [DEBUG, TIME, INFO, WARNING, CRITICAL]

CHOICES = type(
    "choices containing aliases",
    (list,),
    {"__contains__": lambda _, v: v in ALL_LEVEL_NAMES},
)(n.lower() for n in LEVEL_NAMES)

COLORS = [
    ansi.teal,
    ansi.yellow,
    ansi.blue,
    ansi.magenta,
    ansi.red,
]


class Logger(object):
    def __init__(self, *, name, parent):
        if name is None:
            self.name = "~root~"
        else:
            self.name = name
        self.parent = parent
        self.file = sys.stderr
        self.fmt = "%(level)s [%(name)s]\t%(msg)s"
        self.lvl_filter = None

        while parent is not None:
            assert self != parent, "recursive logger relationship"
            parent = parent.parent

        # seems like a great way to never get garbage-collected but loggers are
        # pretty perennial anyway
        # sys.addaudithook(self._audit)

    # def _audit(self, event, *args):
    #     pass

    def setLevel(self, lvl):
        self.lvl_filter = lvl

    def _includeLvl(self, lvl):
        """drop messages if a lvl_filter is above lvl for us or any of our parents"""
        if self.lvl_filter is not None and lvl < self.lvl_filter:
            return False
        elif self.parent is not None:
            return self.parent._includeLvl(lvl)
        else:
            return True

    def is_filtered(self, lvl):
        return not self._includeLvl(lvl)

    def log(self, lvl, *args, exc_info=None, **extra):
        if not self._includeLvl(lvl):
            return

        try:
            lvltxt = LEVEL_NAMES[lvl]
        except IndexError:
            lvltxt = str(lvl)

        if args:
            try:
                msg = str(args[0]) % args[1:]
            except (TypeError, IndexError, KeyError, ValueError) as e:
                msg = f"failed interpolation {args}: {repr(e)}"
        else:
            msg = ""

        # TODO check if self.file isatty?
        try:
            color = COLORS[lvl]
        except IndexError:
            pass
        else:
            lvltxt = color(lvltxt)

        if extra:
            msg += "".join(f"\t» {k} {v}" for k, v in extra.items())

        try:
            msg = self.fmt % {"level": lvltxt, "msg": msg, "name": self.name}
        except (TypeError, IndexError, KeyError, ValueError) as e:
            msg = f"invalid format {repr(e)} {self.fmt} lvl:{lvltxt} msg:{msg}"

        print(msg, file=self.file)

        if exc_info:
            import traceback

            traceback.print_exception(*exc_info, file=self.file)

    def debug(self, *args, **kwargs):
        return self.log(DEBUG, *args, **kwargs)

    def time(self, *args, **kwargs):
        return self.log(TIME, *args, **kwargs)

    def info(self, *args, **kwargs):
        return self.log(INFO, *args, **kwargs)

    def warning(self, *args, **kwargs):
        return self.log(WARNING, *args, **kwargs)

    def error(self, *args, **kwargs):
        return self.log(ERROR, *args, **kwargs)

    def critical(self, *args, **kwargs):
        return self.log(CRITICAL, *args, **kwargs)

    def exception(self, *args, **kwargs):
        return self.log(CRITICAL, *args, exc_info=sys.exc_info(), **kwargs)


INSTANCES = {}  # type: ignore


def getLogger(name=None):
    logger = INSTANCES.get(name)
    if logger is None:
        logger = INSTANCES[name] = _makeLogger(name)
    return logger


def _makeLogger(name):
    if name is None:
        parent = None
    else:
        leading, _, _ = name.rpartition(".")
        if leading:
            parent = getLogger(name=leading)
        else:
            parent = getLogger()  # root/parentless logger
    return Logger(name=name, parent=parent)


ROOT = getLogger()


def basicConfig(level=DEBUG):
    ROOT.lvl_filter = level


if __name__ == "__main__":  # lmao nice unit testing buddy
    from itertools import cycle
    from textwrap import dedent

    ROOT.info("test kwargs", dank="memes", blazeit=420)

    lines = (
        dedent(
            """
        Have you ever wondered why clouds behave in such familiar ways when
        each specimen is so unique?  Or why the energy exchange market is so
        unpredictable?  In the coming age we must develop and apply nonlinear
        mathematical models to real world phenomena. We shall seek, and find,
        the hidden fractal keys which can unravel the chaos around us.

        -- Academician Prokhor Zakharov, University Commencement
        """
        )
        .strip()
        .splitlines()
    )
    for line, lvl in zip(lines, cycle(LEVELS)):
        ROOT.log(lvl, line)
