from pelican import signals
import pelext.rst  # imported for side-effects


def register(*_, **__):
    signals.generator_init.connect(add_jinja_filters)


def add_jinja_filters(pelican):
    pelican.env.filters.update({"is_midnight": is_midnight})


def is_midnight(value):
    """jinja filter for if a date or datetime is at midnight """
    from datetime import time

    if hasattr(value, "time"):
        value = value.time()
    return value == time(0)
