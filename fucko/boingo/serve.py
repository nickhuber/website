import os
import selectors
from contextlib import ExitStack
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from time import monotonic

from inotify_simple import INotify, flags as NotifyFlags  # type: ignore

from fucko import clocked, default_forward_path, duration, logging, net, xdg_open
from fucko.boingo.build import (
    ninja_document_for_args,
    run_ninja_to_completion_and_raise,
)
from fucko.boingo.host import fork_and_host_at
from fucko.cfg import get_config, load_config_from_file

logger = logging.getLogger(__name__)


def serve(args):
    """
    This uses the standard library to run a super simple http server.

    This forks & runs fucko.boingo.host.run_job_socket in a child, which
    listens on a socket until the end of forever.

    This then registers a bunch of paths to watch with inotify & listens on a
    socket for connections to handle with http.server.  Both of these can be
    selected on so that just runs in the main process ... although I think each
    HTTP request is handled by a new Python thread? TODO

    When a inotify yells at us about changes, we fork and run ninja in the
    child.  The fork is basically just so we can watch a socket die when it's
    complete instead of handling SIGCHLD like a well written program.
    """
    cfg = get_config()
    watch_paths = [
        cfg.paths.posts,
        cfg.paths.static,
        Path("templates"),
        cfg.paths.pages,
    ]
    debounce_sec = duration(ms=20).total_seconds()
    build_fork = None
    # start assuming we're a dirty boi
    rebuild_at = monotonic() - 420.69

    if not cfg.build.fwd:
        logger.warn("the [build].fwd setting is ignored by serve")

    with ExitStack() as stack, selectors.DefaultSelector() as selector:

        with clocked("start_host"):
            fwd_sock = str(default_forward_path())
            stack.enter_context(fork_and_host_at(fwd_sock))

        with clocked("start_rwatch"):
            rwatch = start_rwatch(watch_paths)

        with clocked("start_httpd"):
            httpd = stack.enter_context(
                start_httpd(args.host, args.port, cfg.paths.out)
            )
            url = "http://%s:%s" % httpd.server_address
            logger.info("serving", url=url)

            if args.open:
                xdg_open(url)

        rwatch_key = selector.register(rwatch, selectors.EVENT_READ)
        httpd_key = selector.register(httpd, selectors.EVENT_READ)

        while True:
            if build_fork is not None:
                timeout = None
            elif rebuild_at is None:
                timeout = None
            elif (timeout := rebuild_at - monotonic()) < 0:
                timeout = None
                rebuild_at = None
                logger.debug("Rebuilding now ...")
                assert build_fork is None
                build_fork = build_sock, _ = start_rebuild(args, fwd_sock)
                build_key = selector.register(build_sock, selectors.EVENT_READ)
                del build_sock

            try:
                events = selector.select(timeout=timeout)
            except KeyboardInterrupt:
                raise SystemExit(0)

            for event, mask in events:

                if event is rwatch_key:
                    if rwatch.read():
                        logger.debug("Rebuilding soon ...")
                        rebuild_at = monotonic() + debounce_sec

                elif event is httpd_key:
                    httpd._handle_request_noblock()

                elif event is build_key:
                    build_sock, build_pid = build_fork
                    selector.unregister(build_sock)
                    del build_sock
                    logger.debug("waitpid(%s)", build_pid, ret=os.waitpid(build_pid, 0))
                    build_key = build_fork = None

                else:
                    assert False, event


def start_rebuild(args, fwd_sock):
    sock, child_pid = net.fork_with_socketpair()
    if child_pid:
        return sock, child_pid

    try:
        # reload the configuration file in case it changed?
        load_config_from_file(args)
        contents = ninja_document_for_args(args)
        env = os.environ | {"FUCKO_SOCK": fwd_sock}
        run_ninja_to_completion_and_raise(contents.encode(), (), env=env)
    except Exception:
        logger.exception("failed serve rebuild")
    finally:
        os.sync()
        os._exit(os.EX_OK)


def start_rwatch(paths):
    rwatch = RWatch()

    for path in paths:
        rwatch.rwatch(path)

    return rwatch


class RWatch(object):
    wflags = (
        NotifyFlags.CREATE
        | NotifyFlags.DELETE
        | NotifyFlags.MODIFY
        | NotifyFlags.CLOSE_WRITE
        | NotifyFlags.MOVED_FROM
        | NotifyFlags.MOVED_TO
    )

    def __init__(self):
        self.inotify = INotify()
        self.wds = {}

    @property
    def fileno(self):
        return self.inotify.fileno

    def rwatch(self, path: Path):
        for sub in path.glob("**/"):
            wd = self.inotify.add_watch(sub, self.wflags)
            self.wds[wd] = sub

    def read(self):
        dirty = False
        for event in self.inotify.read():
            logger.debug(event=event, flags=NotifyFlags.from_mask(event.mask))
            self._sync(event)
            dirty = True
        return dirty

    def _sync(self, event):
        if event.mask & NotifyFlags.IGNORED:
            del self.wds[event.wd]
        elif event.mask & (NotifyFlags.ISDIR | NotifyFlags.CREATE):
            parent = self.wds[event.wd]
            self.rwatch(parent / event.name)


# stole'd from python's http.server
def _get_best_family(*address):
    import socket

    infos = socket.getaddrinfo(
        *address,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    family, type, proto, canonname, sockaddr = next(iter(infos))
    return family, sockaddr


def start_httpd(host, port, srv):
    class ServerClass(ThreadingHTTPServer):
        pass

    ServerClass.address_family, addr = _get_best_family(host, port)

    class HandlerClass(SimpleHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=srv, **kwargs)

        def send_response(self, code, *args, **kwargs):
            super().send_response(code, *args, **kwargs)
            if code == 301:
                # Stupid hack to prevent the client from waiting for a response
                # body forever in http/1.1.
                self.send_header("content-length", "0")

        def log_message(self, format, *args):
            logger.debug(format, *args)

    return ServerClass(addr, HandlerClass)
