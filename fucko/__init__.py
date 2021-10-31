import io
import mmap
import os
import os.path
import sys
import types
from contextlib import contextmanager
from datetime import time, timedelta, timezone
from pathlib import Path
from time import monotonic

PKG_DIR = Path(__file__).parent
TOP_DIR = PKG_DIR.parent
RUN_DIR = Path("/tmp")


def default_forward_path():
    return RUN_DIR / f"fucko-{os.getpid()}.sock"


def slugify(txt):
    """filesystem/url safe idk
    >>> slugify("  a  WOW  xD'?meme/:#$")
    'a-WOW-xD-meme'
    """
    skip = "'\""
    slug = ""
    for c in txt:
        if c in skip:
            continue
        o = ord(c)
        if ord("a") <= o <= ord("z"):
            slug += c
        elif ord("A") <= o <= ord("Z"):
            slug += c
        elif ord("0") <= o <= ord("9"):
            slug += c
        elif not slug.endswith("-"):
            slug += "-"
    return slug.strip("-")


def lfold_ip(init, fn, it):
    for v in it:
        fn(init, v)
    return init


def flatten(it):
    return lfold_ip([], list.extend, it)


def setitemr(obj, keys, v):
    *keys, key_last = keys
    for key in keys:
        obj = obj.setdefault(key, {})
    obj[key_last] = v


CLOCK_STACK = []  # type: ignore


@contextmanager
def clocked(*args, **kwargs):
    f = sys._getframe(2)  # 2 = 1 + contextlib's contextmanager

    logger = f.f_globals.get("logger")
    if logger is None:
        from fucko import logging  # TODO XXX FIXME move clocked somewhere else?

        logger = logging.getLogger(f.f_globals["__name__"])

    sp = len(CLOCK_STACK)
    start = monotonic()
    try:
        yield
    finally:
        alltime = duration(s=monotonic() - start)  # stop the clock
        cldtime = sum(CLOCK_STACK[sp:], start=duration())
        tottime = duration.fromdelta(alltime - cldtime)

        CLOCK_STACK[sp:] = (alltime,)

        logger.time(*args, all=alltime, slf=tottime, **kwargs)


def test_clocked_stack():
    logger = type("logger", (list,), {"time": lambda self, **kw: self.append(kw)})()

    assert "logger" not in globals()
    globals()["logger"] = logger

    try:
        with clocked():  # d
            with clocked():  # b
                slugify("wow super cpu intensive")
                with clocked():  # a
                    slugify("i'm doing so much work rn")
            with clocked():  # c
                slugify("i really gotta finish those tps reports")
    finally:
        del globals()["logger"]

    a, b, c, d = logger
    assert a["slf"] == a["all"]
    assert b["all"] == b["slf"] + a["all"]
    assert d["all"] == d["slf"] + c["all"] + b["all"]


def depickle_terms_into_context(ctx, terms, pickles):
    import pickle

    picklegen = map(pickle.load, pickles)
    try:
        terms(ctx, picklegen)
    except StopIteration:
        raise ValueError("ran out of pickles to assign to terms") from None
    for _ in picklegen:
        raise ValueError("not enough terms to consume pickles")


class NotAFileError(ValueError):
    pass


def fdfilepath(fd):
    link = os.path.join("/proc/self/fd", str(fd))
    target = os.readlink(link)
    if not os.path.isfile(target):
        raise NotAFileError(f"{target} is not a file")
    return target


@contextmanager
def fd_copy_restore(fd, dest):
    """
    TODO I think this can backfire because if there are any buffers around
    the file descriptor, they will start writing to the wrong thing?
    """
    # These should raise exceptions and always return > 0
    backup = os.dup(dest)  # +1
    try:
        os.dup2(fd, dest)  # close dest -1, dupe fd to dest +1
        try:
            yield
        finally:
            os.dup2(backup, dest)  # close dest -1, dupe backup to dest +1
    finally:
        os.close(backup)  # -1


def close_fds(fds):
    for fd in fds:
        try:
            os.close(fd)
        except OSError:
            pass


class duration(timedelta):
    def __new__(self, *, w=0, d=0, h=0, m=0, s=0, ms=0, us=0):
        return super().__new__(
            self,
            weeks=w,
            days=d,
            hours=h,
            minutes=m,
            seconds=s,
            milliseconds=ms,
            microseconds=us,
        )

    @classmethod
    def fromdelta(cls, td):
        return cls(d=td.days, s=td.seconds, us=td.microseconds)

    def __str__(self):
        tot = self.total_seconds()
        return f"{1000 * tot:.02f}ms"


def default_time_and_timezone(dt):
    """ timezone naive midnight becomes noon, adds a timezone if None """
    if dt.tzinfo is None:
        from fucko.cfg import get_config

        if dt.time() == time(0):  # is midnight
            dt = dt.replace(hour=12)

        return dt.replace(tzinfo=get_config().site.timezone)
    else:
        return dt


def is_relative_uri(uri):
    from urllib.parse import urlparse

    return not urlparse(uri).netloc


def humanize(dt):
    return dt.strftime("%a %b %-d '%y")


def striptags(t):
    from markupsafe import Markup

    return Markup(t).striptags()


def xmlescape(t):
    from markupsafe import escape

    return escape(t)


def contents_match(f, data, chunksz=64 * 1024):
    mm = mmap.mmap(f.fileno(), 0)
    slices = (slice(i, i + chunksz) for i in range(0, len(data), chunksz))
    return all(mm[sl] == data[sl] for sl in slices)


def _write_if_changed(f, data):
    stat_result = os.fstat(f.fileno())
    if stat_result.st_size == len(data) and contents_match(f, data):
        return False
    else:
        f.seek(0)
        f.write(data)
        f.truncate()
        f.flush()
        return True


@contextmanager
def write_if_changed(fname):  # TODO test this?
    fd = os.open(fname, os.O_CREAT | os.O_RDWR)
    with open(fd, "r+b") as f:
        buf = io.BytesIO()
        yield buf
        _write_if_changed(f, buf.getbuffer())


def xdg_open(url):
    import subprocess, sys

    subprocess.run(["xdg-open", url], stdout=sys.stdout, stderr=sys.stderr)
