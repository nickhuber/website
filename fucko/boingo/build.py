import io
import os
import shlex
import subprocess
import sys
from pathlib import Path

from fucko import PKG_DIR, clocked, default_forward_path, flatten, logging
from fucko.cfg import get_config

logger = logging.getLogger(__name__)


def build(args):
    ninja_args = args.ninja_args
    contents = ninja_document_for_args(args)

    if args.show:
        print(contents)
    elif get_config().build.fwd:
        from fucko.boingo.host import fork_and_host_at

        fwd_sock = str(default_forward_path())

        with fork_and_host_at(fwd_sock):
            env = os.environ | {"FUCKO_SOCK": fwd_sock}
            run_ninja_to_completion_and_raise(contents.encode(), ninja_args, env=env)
    else:
        run_ninja_to_completion_and_raise(contents.encode(), ninja_args)


def ninja_document_for_args(args):
    import ninja_syntax  # type: ignore

    cfg = get_config()

    if cfg.build.fwd:
        exe = ["$workdir/fucko-fwd"]
        runtime = exe[:]
    else:
        exe = [sys.executable, "-m fucko"]
        runtime = []  # TODO
    for c in args.config:
        exe += ("--config", c)
    exe += ("--log", args.log)  # TODO this should be a separate option

    cc = cfg.build.cc if cfg.build.fwd else None
    buf = io.StringIO()
    nja = ninja_syntax.Writer(buf)
    with clocked("ninja_document"):
        ninja_document(
            nja,
            cfg.paths,
            site_url=cfg.site.url,
            fork_cc=cc,
            exe=exe,
            runtime=runtime,
            rss=str(cfg.paths.out / cfg.site.rss) if cfg.site.rss else None,
            atom=str(cfg.paths.out / cfg.site.atom) if cfg.site.atom else None,
        )
    return buf.getvalue()


def ninja_document(nja, paths, *, site_url, exe, fork_cc, runtime, rss, atom):
    from ninja_syntax import escape as ninja_escape

    nja.variable("workdir", str(paths.work))
    nja.variable("outdir", str(paths.out))
    nja.variable("fucko", exe)
    nja.variable("sassc_opts", f"-I$workdir/{paths.static}/css/")

    nja.rule("cp", "cp $in $out")
    nja.rule("sassc", "sassc $sassc_opts $in $out")
    nja.rule(
        "render",
        "$fucko render --depfile $out.d $terms $in > $out",
        depfile="$out.d",
    )

    sass_vars = ninja_escape(shlex.quote(f'$site-url: "{site_url}"'))
    nja.rule("sass-vars", f"echo {sass_vars} > $out")
    # $out is in $feed_opts since they're passed as options ...
    nja.rule("feedme", "$fucko feedme $feed_opts $in")
    nja.rule("pickle-rst", "$fucko pickle-rst $in $out", restat=True)

    if fork_cc:
        nja.variable("cc", fork_cc)
        nja.rule("cc", "$cc -Werror -Wall -O3 $in -o $out")
        nja.build("$workdir/fucko-fwd", "cc", f"{PKG_DIR}/fucko-fwd.c")

    # files in static are ~mostly~ copied to $outdir
    for p in paths.static.glob("**/*"):
        if p.is_dir() or p.suffix == ".sass":
            continue
        nja.build(f"$outdir/{p}", "cp", str(p))

    # style sheet
    sass_vars = f"$workdir/{paths.static}/css/_vars.sass"
    nja.build(sass_vars, "sass-vars")
    nja.build(
        f"$outdir/{paths.static}/css/meme.css",
        "sassc",
        f"{paths.static}/css/meme.sass",
        implicit=[sass_vars, *(str(p) for p in paths.static.glob("css/_*.sass"))],
    )

    # posts
    posts = [] if paths.posts is None else list(paths.posts.glob("**/*.rst"))
    posts_meta = []
    posts_body = []
    for post in posts:
        rst_data = ninja_rst(
            nja, f"$workdir/post/{post.parent}", post, implicit=runtime
        )
        meta, body = rst_data
        posts_meta.append(meta)
        posts_body.append(body)
        # assume non-.rst sibling are resources like images and stuff.
        post_dir = post.parent.relative_to(paths.posts)
        ninja_cp_non_rst_siblings(nja, f"$outdir/{post_dir}", post)
        ninja_render_rst_post(
            nja, f"$outdir/{post_dir}/index.html", rst_data, implicit=runtime
        )

    # pages
    pages = [] if paths.pages is None else list(paths.pages.glob("*.rst"))
    for page in pages:
        rst_data = ninja_rst(nja, f"$workdir/page/{page.stem}", page, implicit=runtime)
        # ninja_cp_non_rst_siblings doesn't make much sense here since the
        # inputs aren't each in their own directory, we don't know what
        # static files each rst document actually needs. pickle-rst could
        # be clever and generate a deps file for us though ...
        if page.name == "index.rst":
            ninja_render_index(
                nja, "$outdir/index.html", rst_data, posts_meta, implicit=runtime
            )
        else:
            ninja_render_rst_post(
                nja, f"$outdir/{page.stem}/index.html", rst_data, implicit=runtime
            )

    # rss/atom feed
    if atom or rss:
        feed_out = [atom, rss]
        feed_opts = ""
        if atom:
            feed_opts += f"--atom {ninja_escape(atom)} "
        if rss:
            feed_opts += f"--rss {ninja_escape(rss)} "
        feed_src = [f for pair in zip(posts_meta, posts_body) for f in pair]
        nja.build(
            feed_out,
            "feedme",
            feed_src,
            implicit=runtime,
            variables={"feed_opts": feed_opts},
        )


def ninja_rst(nja, work_dir, rst_path, implicit=[], **kwargs):
    # not sufficient but better than nothing?
    implicit = [str(PKG_DIR / "boingo" / "pickle_rst.py")] + implicit
    rst_data = nja.build(
        [f"{work_dir}/meta", f"{work_dir}/body"],
        "pickle-rst",
        str(rst_path),
        variables={"terms": "meta,body"},
        implicit=implicit,
        **kwargs,
    )
    return rst_data


def ninja_cp_non_rst_siblings(nja, out: str, post: Path):
    for f in post.parent.glob("*"):
        if f.suffix != ".rst":
            nja.build(f"{out}/{f.relative_to(post.parent)}", "cp", str(f))


def ninja_render_rst_post(nja, out: str, rst_data: list, **kwargs):
    return nja.build(
        out,
        "render",
        inputs=[f"templates/post.html"] + rst_data,
        variables={"terms": "meta,body"},
        **kwargs,
    )


def ninja_render_index(nja, out: str, index_data: list, posts_meta: list, **kwargs):
    return nja.build(
        out,
        "render",
        inputs=[f"templates/index.html"] + index_data + posts_meta,
        variables={"terms": "meta,body,posts[:]"},
        **kwargs,
    )


def run_ninja_to_completion_and_raise(contents: bytes, ninja_args, **kwargs):
    with clocked("ninja"):
        ninja = subprocess.run(
            ["ninja", "-f", "/dev/stdin", *ninja_args],
            input=contents,
            stdout=sys.stdout,
            stderr=sys.stderr,
            **kwargs,
        )
    raise SystemExit(ninja.returncode)
