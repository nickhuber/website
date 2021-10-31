""" reStructuredText extensions
"""

from docutils import nodes, writers
from docutils.parsers.rst import Directive, directives, roles
from docutils.parsers.rst.directives.body import CodeBlock
from docutils.parsers.rst.directives.images import Image
from docutils.transforms import Transform
from docutils.writers.html5_polyglot import HTMLTranslator, Writer

roles.DEFAULT_INTERPRETED_ROLE = "code"  # ¯\_(ツ)_/¯ intead of title/citation


def rst_role(fn):
    roles.register_local_role(fn.__name__.replace("_", "-"), fn)


@rst_role
def newthought(name, rawtext, text, lineno, inliner, options={}, content=[]):
    return [nodes.inline(text=text, classes=["newthought"])], []


@rst_role
def hl_purple(name, rawtext, text, lineno, inliner, options={}, content=[]):
    return [nodes.inline(text=text, classes=["hl-purple"])], []


@rst_role
def hl_yellow(name, rawtext, text, lineno, inliner, options={}, content=[]):
    return [nodes.inline(text=text, classes=["hl-yellow"])], []


@rst_role
def abbr(name, rawtext, text, lineno, inliner, options={}, content=[]):
    import re

    abbr_re = re.compile(r"\((.*)\)$", re.S)

    matched = abbr_re.search(text)
    if matched:
        text = text[: matched.start()].strip()
        options = options.copy()
        options["title"] = matched.group(1)

    return [nodes.abbreviation(rawtext, text, **options)], []


class aside(nodes.General, nodes.Element):
    pass


class picture(nodes.General, nodes.Element):
    pass


class source(nodes.General, nodes.Element):
    pass


class Decorate(Transform):
    """ It seems like there should be an easier way ... """

    default_priority = 999

    def apply(self, **kwargs):
        pending = self.startnode
        parent = pending.parent
        i = parent.index(pending)
        aside_ = parent[i - 1]
        target = parent[i + 1]
        # yoink
        parent.remove(pending)
        parent.remove(target)
        aside_.append(target)


class Aside(Directive):
    """
    Encloses contents in an <aside> element. If it has no contents, encloses
    the following element instead, a bit like the .. class:: directive.
    """

    has_content = True

    def run(self):
        if self.content:
            node = aside(**self.options)
            self.state.nested_parse(self.content, self.content_offset, node)
            return [node]
        else:
            aside_ = aside(**self.options)
            node = nodes.pending(Decorate)
            self.state_machine.document.note_pending(node)
            return [aside_, node]


class EmptyCode(CodeBlock):
    has_content = False

    def assert_has_content(self):
        pass


class Picture(Image):
    has_content = True

    def run(self):
        (image_node,) = Image.run(self)
        if isinstance(image_node, nodes.system_message):
            return [image_node]

        picture_node = picture("")
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, picture_node)
        picture_node += image_node
        return [picture_node]


class Source(Directive):
    option_spec = {"media": directives.unchanged, "srcset": directives.uri}

    def run(self):
        return [source(**self.options)]


directives.register_directive("aside", Aside)
directives.register_directive("empty-code", EmptyCode)
directives.register_directive("picture", Picture)
directives.register_directive("source", Source)


def meme_writer_class(name):
    cls = writers.get_writer_class(name)
    return build_MemeHTMLWriter(cls)


def build_MemeHTMLWriter(cls):
    _translator_class = build_MemeHTMLTranslator(cls().translator_class)

    class MemeHTMLWriter(cls):
        def __init__(self):
            super().__init__()
            self.translator_class = _translator_class

    return MemeHTMLWriter


_empty = set()

def build_MemeHTMLTranslator(cls):
    class MemeHTMLTranslator(cls):
        def visit_literal_block(self, node):
            # pygments generates inline nodes with classes like "s", visit_inline will
            # see this and promote it to a <s> which is a strikeout/strikethrough and
            # that's not what we want.
            # Anything that pygments spits out should be left alone.
            super().visit_literal_block(node)
            assert self.supported_inline_tags is not _empty
            self.supported_inline_tags = _empty

        def depart_literal_block(self, node):
            assert self.supported_inline_tags is _empty
            del self.supported_inline_tags
            super().depart_literal_block(node)

        def visit_abbreviation(self, node):
            self.body.append(
                self.starttag(node, "abbr", "", **node.non_default_attributes())
            )

        def depart_abbreviation(self, node):
            self.body.append("</abbr>")

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
            if "alt" not in node:
                cap = node.first_child_matching_class(nodes.caption)
                if cap:
                    img = node[cap - 1].first_child_matching_class(nodes.image)
                if cap and img is not None:
                    img_attrs = node[cap - 1][img].attributes
                    if "alt" not in img_attrs:
                        img_attrs["alt"] = node[cap].astext()
            self.body.append(self.starttag(node, "figure", **atts))

        def depart_figure(self, node):
            self.body.append("</figure>\n")

        def visit_picture(self, node):
            self.body.append(self.starttag(node, "picture"))

        def depart_picture(self, node):
            self.body.append("</picture>\n")

        def visit_source(self, node):
            attrs = {a: node.get(a) for a in Source.option_spec.keys()}
            self.body.append(self.starttag(node, "source", **attrs))

        def depart_source(self, node):
            pass

        def visit_caption(self, node):
            """Like base but <figcaption>."""
            self.body.append(self.starttag(node, "figcaption", ""))

        def depart_caption(self, node):
            self.body.append("</figcaption>\n")

        def visit_aside(self, node):
            self.body.append(self.starttag(node, "aside", ""))

        def depart_aside(self, node):
            self.body.append("</aside>\n")

    return MemeHTMLTranslator


Html5Writer = meme_writer_class("html5")


class FieldBodyTranslator(Html5Writer().translator_class):  # type: ignore
    """mostly stolen from pelican/readers.py

    Honestly, this seems very high-effort.  It seems almost more appropriate to
    use a directive.
    """

    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.compact_p = None

    @classmethod
    def astext(cls, document, value):
        self = cls(document)
        value.walkabout(self)
        return "".join(self.body)

    def visit_field_body(self, node):
        pass

    def depart_field_body(self, node):
        pass
