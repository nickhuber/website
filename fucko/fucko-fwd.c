// vim: ts=2 sw=2 et

#define _GNU_SOURCE

#include <assert.h>
#include <errno.h>
#include <linux/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

typedef __int32_t u32;

char MAGIC[] = "fucko";

#define OK 1
#define NOT_OK 0
#define ptr__ok(p) (p ? OK : NOT_OK)

void exit_with_errno(char *msg, int err) {
  fprintf(stderr, "[fwd] err %s (%d %s)\n", msg, err, strerror(err));
  _exit(EXIT_FAILURE);
}

void exit_with(char *msg) {
  fprintf(stderr, "[fwd] %s\n", msg);
  _exit(EXIT_FAILURE);
}

/*** xdr -- functions generally return 1 for success, 0 for otherwise ***/

typedef struct xdrpack {
  char *buf;
  size_t len;
  size_t cap;
} xdrpack_t;

int xdr_alloc(xdrpack_t *xdr);
void xdr_free(xdrpack_t *xdr);

int xdr_enc_u32(xdrpack_t *xdr, u32 v);
int xdr_enc_str(xdrpack_t *xdr, char *src);
int xdr_enc_sized(xdrpack_t *xdr, void *src, unsigned int sz);
int xdr_enc_fixed(xdrpack_t *xdr, void *src, unsigned int sz);

int xdr_dec_u32(xdrpack_t *xdr, u32 *v);
int xdr_dec_fixed(xdrpack_t *xdr, void *dst, unsigned int sz);

/*** fucko forward ***/

int encode_xdr_message(xdrpack_t *xdr, int argc, char *argv[]) {
  int ok;
  char *cwd;

  if (!(ok = xdr_enc_str(xdr, MAGIC)))
    return ok;

  cwd = get_current_dir_name();
  if (!cwd)
    return NOT_OK;

  ok = xdr_enc_str(xdr, cwd);
  free(cwd);
  if (!ok)
    return ok;

  if (!(ok = xdr_enc_u32(xdr, argc)))
    return ok;

  for (int i = 0; i < argc; i++)
    if (!(ok = xdr_enc_str(xdr, argv[i])))
      return ok;

  return OK;
}

/* stolen from https://blog.cloudflare.com/know-your-scm_rights/ */
int send_stdinouterr(int sock, char *dat, size_t datlen) {
  const int fds[3] = { fileno(stdin), fileno(stdout), fileno(stderr) };
  struct iovec iov = {.iov_base = dat, .iov_len = datlen};

  union {
    char buf[CMSG_SPACE(sizeof(fds))];
    struct cmsghdr align;
  } u;

  struct msghdr msg = {.msg_iov = &iov,
                       .msg_iovlen = 1,
                       .msg_control = u.buf,
                       .msg_controllen = sizeof(u.buf)};

  struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
  *cmsg = (struct cmsghdr){.cmsg_level = SOL_SOCKET,
                           .cmsg_type = SCM_RIGHTS,
                           .cmsg_len = CMSG_LEN(sizeof(fds))};

  memcpy(CMSG_DATA(cmsg), &fds, sizeof(fds));

  return sendmsg(sock, &msg, 0);
}

int recv_reply(int sock, u32 *reply) {
  char buf[1024];
  int len = recv(sock, buf, 1024, 0);
  if (len <= 0)
    return NOT_OK;

  xdrpack_t pack = {.buf = buf, .cap = len};
  return xdr_dec_u32(&pack, reply);
}

int main(int argc, char *argv[]) {
  struct sockaddr_un addr = {.sun_family = AF_UNIX};
  xdrpack_t xdr = {0};
  u32 reply;
  int sock;
  char *sock_path =
      getenv("FUCKO_SOCK"); /* This won't support abstract socket paths. */

  if (!sock_path)
    exit_with("specify a sock path in FUCKO_SOCK");

  if (!xdr_alloc(&xdr))
    exit_with_errno("xdr_alloc", errno);

  if (!encode_xdr_message(&xdr, argc, argv))
    exit_with_errno("encode_xdr_message", errno);

  sock = socket(AF_UNIX, SOCK_STREAM, 0);
  if (!sock)
    exit_with_errno("socket", errno);

  strncpy(addr.sun_path, sock_path, sizeof(addr.sun_path) - 1);

  if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0)
    exit_with_errno("connect", errno);

  if (!send_stdinouterr(sock, xdr.buf, xdr.len))
    exit_with_errno("send_stdinouterr", errno);

  if (!recv_reply(sock, &reply)) {
    if (!errno)
      exit_with("no reply received");
    else
      exit_with_errno("recv_reply", errno);
  }

  xdr_free(&xdr);

  return reply;
}

/*** xdr implementation ***/

/* 256 = 1 << 8 */
#define XDR_GROWBY 8
#define XDR_QUADLEN(l) (((l) + 3) >> 2)

int xdr_alloc(xdrpack_t *xdr) {
  xdr->buf = malloc(1 << XDR_GROWBY);
  return ptr__ok(xdr->buf);
}

void xdr_free(xdrpack_t *xdr) { free(xdr->buf); }

int xdr__fits(xdrpack_t *xdr, size_t moar) {
  if (moar <= xdr->cap - xdr->len)
    return OK;

  /* round up to nearest multiple of 1 << XDR_GROWBY */
  xdr->cap = ((xdr->len + moar - 1) / (1 << XDR_GROWBY) + 1) << XDR_GROWBY;
  assert(xdr->len + moar <= xdr->cap);
  xdr->buf = realloc(xdr->buf, xdr->cap);
  return ptr__ok(xdr->buf);
}

int xdr_enc_u32(xdrpack_t *xdr, u32 v) {
  __be32 be = htobe32(v);
  return xdr_enc_fixed(xdr, &be, sizeof(v));
}

int xdr_enc_str(xdrpack_t *xdr, char *src) {
  return xdr_enc_sized(xdr, src, strlen(src));
}

int xdr_enc_sized(xdrpack_t *xdr, void *src, unsigned int sz) {
  __be32 be_sz = htobe32(sz);
  return xdr_enc_fixed(xdr, &be_sz, sizeof(__be32)) &&
         xdr_enc_fixed(xdr, src, sz);
}

int xdr_enc_fixed(xdrpack_t *xdr, void *src, unsigned int sz) {
  /* copied from linux/net/sunrpc/xdr.c:xdr_encode_opaque_fixed
   * idk how xdr's padding works */
  unsigned int quadlen = XDR_QUADLEN(sz);
  unsigned int padding = (quadlen << 2) - sz;
  int ok;
  if (!(ok = xdr__fits(xdr, sz + padding)))
    return ok;

  memcpy(xdr->buf + xdr->len, src, sz);
  if (padding)
    memset(xdr->buf + xdr->len + sz, 0, padding);

  xdr->len += sz + padding;
  return OK;
}

int xdr_dec_u32(xdrpack_t *xdr, u32 *v) {
  int ok;
  __be32 be;

  if (!(ok = xdr_dec_fixed(xdr, &be, sizeof(be))))
    return ok;

  *v = be32toh(be);
  return OK;
}

int xdr_dec_fixed(xdrpack_t *xdr, void *dst, unsigned int sz) {
  unsigned int quadlen = XDR_QUADLEN(sz);
  unsigned int padding = (quadlen << 2) - sz;

  if (xdr->cap < xdr->len + sz)
    return NOT_OK;

  memcpy(dst, xdr->buf + xdr->len, sz);
  xdr->len += sz + padding;
  return OK;
}
