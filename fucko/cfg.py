from pathlib import Path

from dateutil.tz import gettz

from fucko import TOP_DIR, setitemr

_config_dict = None
_config_inst = None


def _read_config_file():
    import toml

    with (TOP_DIR / "www.toml").open() as f:
        return toml.load(f)


def load_config_from_file(args):
    global _config_dict
    _config_dict = _read_config_file()
    return load_config_from_cache(args)


def load_config_from_cache(args):
    if _config_dict is None:
        raise Exception("config not loaded")
    global _config_inst
    _config_inst = init_config_object(args, _config_dict)
    return _config_inst


def init_config_object(args, config_dict):
    import toml
    from fucko.cfg import Config

    for conf in args.config:
        key, _, value = conf.partition("=")
        try:
            value = toml.loads(f'_ = {value}')['_']
        except toml.TomlDecodeError:
            value = toml.loads(f'_ = {value!r}')['_']
        setitemr(config_dict, key.split("."), value)
    return Config(**config_dict)


def get_config():
    """ load a cached Config object """
    if _config_inst is None:
        raise Exception("config not loaded")
    return _config_inst


def _path_or_none(s):
    return None if s is None else Path(s)


# fmt: off

class _paths(object):
    def __init__(self, *, out, work, static, posts=None, pages=None, dated=None):
        self.out = _path_or_none(out)
        self.work = _path_or_none(work)
        self.static = _path_or_none(static)
        self.posts = _path_or_none(posts)
        self.pages = _path_or_none(pages)
        self.dated = dated


class _site(object):
    def __init__(self, *, url, name, author, logo, logo_alt, social, timezone, rss=None, atom=None, description=""):
        self.url = url
        self.name = name
        self.author = author
        self.logo = logo
        self.logo_alt = logo_alt
        self.social = social
        self.timezone = gettz(timezone)
        self.rss = rss
        self.atom = atom
        self.description = description

        if self.url:
            self.url = self.url.rstrip("/")


class _build(object):
    def __init__(self, *, cc="clang", fork=True, fwd=True):
        self.cc = cc
        self.fork = fork
        self.fwd = fwd


class Config(object):
    def __init__(self, *, paths, site, build={}):
        self.paths = _paths(**paths)
        self.site = _site(**site)
        self.build = _build(**build)

# fmt: on
