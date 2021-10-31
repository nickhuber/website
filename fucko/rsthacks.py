import re

from docutils.parsers.rst.states import state_classes


def compile_patterns():
    for cls in state_classes:
        for name, pattern in cls.patterns.items():
            cls.patterns[name] = re.compile(pattern)
