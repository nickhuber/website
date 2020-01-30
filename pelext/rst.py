from docutils import nodes
from docutils.parsers.rst import roles, directives
from docutils.parsers.rst.directives.body import CodeBlock
from docutils.writers.html5_polyglot import Writer, HTMLTranslator

from pelican.readers import (
    PelicanHTMLWriter,
    PelicanHTMLTranslator,
    RstReader,
    METADATA_PROCESSORS,
)


roles.DEFAULT_INTERPRETED_ROLE = "code"  # ¯\_(ツ)_/¯ intead of title/citation


def rst_role(fn):
    roles.register_local_role(fn.__name__, fn)


@rst_role
def newthought(name, rawtext, text, lineno, inliner, options={}, content=[]):
    return [nodes.inline(text=text, classes=["newthought"])], []


class EmptyCode(CodeBlock):
    has_content = False

    def assert_has_content(self):
        pass


directives.register_directive("empty-code", EmptyCode)

PelicanHTMLTranslator.__bases__ = (HTMLTranslator,)


class MemeHTMLWriter(PelicanHTMLWriter):
    def __init__(self):
        super().__init__()
        self.translator_class = MemeHTMLTranslator


class MemeHTMLTranslator(PelicanHTMLTranslator):
    def visit_section(self, node):
        """Same as base but <section>."""
        self.section_level += 1
        self.body.append(self.starttag(node, "section"))

    def depart_section(self, node):
        self.section_level -= 1
        self.body.append("</section>")

    def visit_attribution(self, node):
        prefix, suffix = self.attribution_formats[self.settings.attribution]
        self.context.append(suffix)
        self.body.append(self.starttag(node, "footer", prefix, CLASS="attribution"))

    def depart_attribution(self, node):
        self.body.append(self.context.pop() + "</footer>\n")

    def visit_figure(self, node):
        """Same as base but <figure>."""
        atts = {"class": "figure"}
        if node.get("width"):
            atts["style"] = "width: %s" % node["width"]
        if node.get("align"):
            atts["class"] += " align-" + node["align"]
        self.body.append(self.starttag(node, "figure", **atts))

    def depart_figure(self, node):
        self.body.append("</figure>\n")

    def visit_caption(self, node):
        """Like base but <figcaption>."""
        self.body.append(self.starttag(node, "figcaption", ""))

    def depart_caption(self, node):
        self.body.append("</figcaption>\n")


RstReader.writer_class = MemeHTMLWriter
