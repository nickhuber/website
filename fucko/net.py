import array
import io
import os
import pickle
import select
import socket
import stat
import sys

MAGIC = b"fucko"
BACKLOG = 2 * (os.cpu_count() or 8)  # ??? is this important ???
MAX_MSG = 8 * 1024  # i imagine this is going to be a problem at some point


def maybe_unlink_sock(path: str):
    if path and path[0] in (0, "\x00"):
        return  # Abstract socket path
    try:
        if stat.S_ISSOCK(os.stat(path).st_mode):
            os.remove(path)
    except FileNotFoundError:
        pass
    except OSError:
        pass


def open_unix_listener(path: str):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.bind(path)
        sock.listen(BACKLOG)
    except:
        sock.close()
        raise
    else:
        return sock


def open_unix_connection(path: str):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(path)
    except:
        sock.close()
        raise
    else:
        return sock


def open_unix_socketpair():
    # I thought we could use SOCK_DGRAM here because preserves message
    # boundaries and doesn't reorder on AF_UNIX but I can't seem to epoll on
    # this properly, maybe because it's "connectionless"?  But it's a
    # socketpair ... how is it "connectionless"? They're a fucking pair ...
    return socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)


def fork_with_socketpair():
    # the order is arbitrary as long as we're consistent ...
    to_child, to_parent = open_unix_socketpair()
    # once the unused socket/other end drops out of scope, it should be closed
    child_pid = os.fork()
    if child_pid:  # parent branch
        return to_child, child_pid
    else:  # child branch
        return to_parent, child_pid


def send_fds(sock, msg, fds):
    """stolen from https://docs.python.org/3/library/socket.html#socket.socket.sendmsg"""
    if not isinstance(fds, array.array):
        fds = array.array("i", fds)
    return sock.sendmsg([msg], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, fds)])


def recv_fds(sock, msglen, maxfds):
    """stolen from https://docs.python.org/3/library/socket.html#socket.socket.recvmsg"""
    fds = array.array("i")  # Array of ints
    msg, ancdata, flags, addr = sock.recvmsg(
        msglen, socket.CMSG_LEN(maxfds * fds.itemsize)
    )
    for cmsg_level, cmsg_type, cmsg_data in ancdata:
        if cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS:
            # Append data, ignoring any truncated integers at the end.
            fds.frombytes(cmsg_data[: len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
    return msg, list(fds)


def say_goodbye(sock, *, timeout=None):
    if timeout is not None:
        timeout = timeout.total_seconds()

    sock.send(b"see ya")

    with select.epoll() as poll:
        poll.register(sock.fileno())
        return bool(poll.poll(0.1, maxevents=1))
