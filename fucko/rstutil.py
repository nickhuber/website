from datetime import time
from io import StringIO

import dateutil.parser
import docutils
import docutils.core
import docutils.io
import docutils.writers

from fucko import default_time_and_timezone, rstext

DOCUTILS_SETTINGS = {"smart_quotes": True, "footnote_references": "superscript"}

metadata_parsers: dict = {
    "date": (dateutil.parser.parse, default_time_and_timezone),
    "modified": (dateutil.parser.parse, default_time_and_timezone),
    "tags": lambda v: [s.strip() for s in v.split(",")],
}

metadata_converter: dict = {"summary": rstext.FieldBodyTranslator.astext}


class _func_chains(tuple):
    def __call__(self, v):
        for fn in self:
            v = fn(v)
        return v


for d in (metadata_parsers, metadata_converter):
    for key, value in d.items():
        if not callable(value):
            d[key] = _func_chains(value)


def path_publisher(path):
    """ return a docutils rst publisher that will read from the given path """
    extra_params = {
        "initial_header_level": "2",
        "syntax_highlight": "short",
        "input_encoding": "utf-8",
        "language_code": "en",
        "halt_level": 2,
        "traceback": True,
        "warning_stream": StringIO(),
        "stylesheet_path": None,
        "stylesheet": None,
    }
    extra_params.update(DOCUTILS_SETTINGS)

    pub = docutils.core.Publisher(
        writer=rstext.Html5Writer(), destination_class=docutils.io.StringOutput
    )
    pub.set_components("standalone", "restructuredtext", "html")
    pub.process_programmatic_settings(None, extra_params, None)
    pub.set_source(source_path=path)
    return pub


def traverse(inside, finding):
    for child in inside:
        if isinstance(child, finding):
            yield child
    for child in inside.children:
        yield from traverse(child, finding)


def document_metafields(doc):
    """ generator for docutils.nodes.field node name, value pairs """
    for f in traverse(doc, docutils.nodes.field):
        name, value = (c.astext() for c in f.children)
        yield name.lower(), value


def document_metadata(document):
    output = {}
    for docinfo in document.traverse(docutils.nodes.docinfo):
        for item in docinfo.children:
            key, value = _parse_docinfo_item(item)
            if key in metadata_parsers:
                value = metadata_parsers[key](value.astext())
            elif key in metadata_converter:
                value = metadata_converter[key](document, value)
            else:
                value = value.astext()
            output[key] = value
    return output


def _parse_docinfo_item(item):
    if len(item.children) == 1:
        (body,) = item.children
        return item.tagname.lower(), body
    else:
        (name, body) = item.children
        return name.astext().lower(), body


def parse_datetime(string):
    return dateutil.parser.parse(string)


def document_resources(document):
    for img in traverse(document, docutils.nodes.image):
        yield img.attributes["uri"]
    for source in traverse(document, rstext.source):
        yield source.attributes["srcset"]
