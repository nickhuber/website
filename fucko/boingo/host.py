import os
import socket
import sys
import xdrlib
from contextlib import contextmanager
from select import EPOLLERR, EPOLLHUP, EPOLLIN, EPOLLONESHOT, epoll

from fucko import clocked, close_fds, duration, fd_copy_restore, logging, net
from fucko.cfg import get_config

logger = logging.getLogger(__name__)


__inouterr = sys.stdin.fileno(), sys.stdout.fileno(), sys.stderr.fileno()
assert 3 == len(set(__inouterr)), (
    f"I don't know if this can ever happen but stdin (%s), stdout (%s), & stderr (%s) must be distinct file descriptors for fucko host to work"
    % __inouterr
)


def host(args):
    with fork_and_host_at(str(args.path)):
        try:
            os.wait()
        except KeyboardInterrupt:
            pass


@contextmanager
def fork_and_host_at(forward: str):
    """Fork and do jobs that come in to the unix socket at `forward`.

    This is a context manager that yields for the parent process.  When you
    exit the context, this will try to close the child and not give it a large
    timeout since it shouldn't be doing anything anyway presumably?"""
    net.maybe_unlink_sock(forward)
    with net.open_unix_listener(forward) as job_sock:
        sock, my_dude = net.fork_with_socketpair()

        if my_dude:  # parent
            try:
                del job_sock
                logger.debug(
                    "forked a little duder (%s) listening at: %s", my_dude, forward
                )
                yield  # yield control back because context manager
            finally:
                try:
                    os.unlink(forward)
                except Exception as e:
                    logger.exception("unlink %s:", forward, e)

                try:
                    ok = net.say_goodbye(sock, timeout=duration(ms=100))
                except (BrokenPipeError, ConnectionRefusedError):
                    pass
                except Exception as e:
                    logger.exception("goodbye to (%s): %s", my_dude, e)
                else:
                    if not ok:
                        try:
                            logger.debug("killing child (%s)", my_dude)
                            os.kill(my_dude, 2)
                        except Exception as e:
                            logger.exception("kill child (%s): %s", my_dude, e)

        else:  # child
            try:
                run_job_socket(sock, job_sock)
            except Exception:
                logger.exception("exception in run_job_socket")
            finally:
                os.sync()
                os._exit(os.EX_OK)


def run_job_socket(to_parent, job_sock):
    running = True
    jobs = {}
    cfg = get_config()
    # When None, we never fork and do one job at a time.  When forkwhen is a
    # set(), we don't fork the first time we do each action.  This is just a
    # general and vague way to get stuff cached in the main process so it can
    # be used when forking later.
    forkwhen = set() if cfg.build.fork else None

    with epoll() as poll:
        eventsflag = EPOLLIN | EPOLLHUP | EPOLLERR
        poll.register(to_parent, eventsflag)
        poll.register(job_sock, eventsflag)

        while running:
            events = poll.poll()
            for (fd, event) in events:
                if fd == to_parent.fileno():
                    logger.debug("poll on parent socket; quitting", event=event)
                    running = False

                elif (child := jobs.get(fd)) is not None:
                    child_sock, child_pid = child
                    del child_sock
                    _remove_child_sock(jobs, fd, child_pid)

                elif event == EPOLLIN:
                    peer, _ = job_sock.accept()
                    logger.debug("got a buddy: %s", peer)

                    try:
                        parent_pid = os.getpid()

                        with peer:
                            forked = serve_peer(peer, forkwhen)

                        assert parent_pid == os.getpid(), "child is on the loose"

                    except Exception:  # does not catch SystemExit KeyboardInterrupt
                        logger.exception("failed to serve peer")

                    else:
                        if forked is not None:
                            logger.debug("forked in serve_peer: %s", forked)
                            # We forked, we're the parent.  Don't leak shit.
                            child_sock, child_pid = forked
                            # Keep an eye on the socket for when it goes so we can reap
                            # that process.
                            jobs[child_sock.fileno()] = (child_sock, child_pid)
                            poll.register(child_sock, EPOLLONESHOT | eventsflag)
                            del child_sock

                    del peer

                else:
                    logger.error("??? job sock event: %s", event)
                    running = False


def _remove_child_sock(jobs, fd, child_pid):
    del jobs[fd]
    logger.debug("waitpid(%s)", child_pid, ret=os.waitpid(child_pid, 0))


def serve_peer(peer: socket.socket, forkwhen):
    """Get a job from the peer and run it.

    This may fork to run the job in another process, this returns the child's
    (sock, pid) tuple in the parent in that case.  This function should not
    return in the child."""
    parent_pid = os.getpid()
    with read_job_from_sock(peer) as job:
        logger.debug("got job: %s %s", job.cwd, job.args)

        # Fun fact, main() may have side effects on this process before it
        # forks, like configuring the root logger ... we don't do anything
        # clever about this expect explicitly fix it up =\
        root_logger = logging.getLogger()
        orig_level = root_logger.lvl_filter

        try:
            try:
                with job.cwd_installed():
                    with job.fds_installed():
                        return run_job_args(job.args, forkwhen)
            finally:
                root_logger.setLevel(orig_level)
        except Exception:
            # This is bad if this happens since we've already uninstalled the
            # job's file descriptors.  All the job's output needs to happen
            # inside of main() before returning or raising.
            logger.exception("Unhandled exception in job main(); caught late!!!")
            exit_code = 1
        except KeyboardInterrupt:
            exit_code = 0
        except SystemExit as exit:
            exit_code = exit.code

    # We should only get here if we completed the job, either without forking
    # or as a child that forked. A parent that forked without completing the
    # job should not be here.

    # Close the job's file descriptors ...
    logger.debug("job exited with code %s", exit_code)

    reply_to_sock_with_result(peer, exit_code)

    if parent_pid != os.getpid():
        # We're the child.  We want to quit but don't want to unwind all of the
        # Python stack and accidentally start talking to the system as if we
        # were the parent.
        os.sync()
        os._exit(os.EX_OK)


def run_job_args(argv, forkwhen):
    from fucko.__main__ import (
        boingo_prefork,
        import_boingo,
        maybe_pdb_context,
        parse_args_configure_logging,
    )
    from fucko.cfg import load_config_from_cache

    args = parse_args_configure_logging(argv)

    with maybe_pdb_context(args):
        load_config_from_cache(args)

        boingo_mod, boingo_fn = import_boingo(args.action)
        extra = boingo_prefork(args.action, boingo_mod, args)

        if forkwhen is not None:
            if args.action in forkwhen:
                sock, child_pid = net.fork_with_socketpair()
                if child_pid:  # early exit for parent
                    return sock, child_pid
            else:
                logger.debug("not forking this time", action=args.action)
                forkwhen.add(args.action)

        with clocked("run", action=args.action):
            boingo_fn(args, *extra)

        raise SystemExit(0)


class Job(object):
    def __init__(self, stdinouterr, cwd, args):
        self.stdinouterr = stdinouterr
        self.cwd = cwd
        self.args = args

    def __enter__(self):
        return self

    def __exit__(self, *asdf):
        close_fds(self.stdinouterr)

    @contextmanager
    def cwd_installed(self):
        old = os.getcwd()  # consider using file descriptors and fchdir instead?
        os.chdir(self.cwd)
        try:
            yield
        finally:
            os.chdir(old)

    @contextmanager
    def fds_installed(self):
        """Clones the jobs' stdin, stdout, stderr file descriptors over ours.

        For instance, our descriptors 0, 1, & 2 will become the requesters'
        stdin, stdout, & stderr respectively.  The reason for this is that
        simply assigning over sys.stdout or whatever only works if nobody is
        holding on to the old sys.stdout.  Which they are.  And we want them to
        write to the requester's files instead.
        """
        inp, out, err = self.stdinouterr
        # os.sync()
        with fd_copy_restore(inp, sys.stdin.fileno()):
            with fd_copy_restore(out, sys.stdout.fileno()):
                with fd_copy_restore(err, sys.stderr.fileno()):
                    yield
                    # os.sync()


def read_job_from_sock(peer):
    msg, fds = net.recv_fds(peer, net.MAX_MSG, 3)  # 3 for stdin out err
    try:
        stdin, stdout, stderr, *rest = fds

        unp = xdrlib.Unpacker(msg)

        if (magic := unp.unpack_string()) != net.MAGIC:
            raise ValueError("invalid magic", magic)

        # fyi! unpack_string() doesn't give us a string of unicode, just bytes

        cwd = unp.unpack_string().decode()

        job_args = [unp.unpack_string().decode() for _ in range(unp.unpack_int())]
    except:
        close_fds(fds)
        raise

    return Job((stdin, stdout, stderr), cwd, job_args)


def reply_to_sock_with_result(peer, result):
    pkr = xdrlib.Packer()
    # pkr.pack_string(net.MAGIC)  # I don't care enough to decode a string in fucko-fwd.c?
    pkr.pack_int(result)
    msg = pkr.get_buffer()
    peer.send(msg)
