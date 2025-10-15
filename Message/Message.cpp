#include "Message.h"

#include <arpa/inet.h>  
#include <unistd.h>     
#include <cstring>
#include <cerrno>

static bool send_all(int fd, const uint8_t* buf, std::size_t n) {
  std::size_t sent = 0;
  while (sent < n) {
    ssize_t w = ::write(fd, buf + sent, n - sent);
    if (w < 0) {
      if (errno == EINTR) continue;
      return false;
    }
    if (w == 0) return false;
    sent += static_cast<std::size_t>(w);
  }
  return true;
}

static bool recv_exact(int fd, uint8_t* buf, std::size_t n) {
  std::size_t got = 0;
  while (got < n) {
    ssize_t r = ::read(fd, buf + got, n - got);
    if (r < 0) {
      if (errno == EINTR) continue;
      return false;
    }
    if (r == 0) return false;
    got += static_cast<std::size_t>(r);
  }
  return true;
}

// FUNCIONS PER ENVIAR I REBRE MISSATGES

Message::Message(const uint8_t raw[kSize]) {
  type_ = static_cast<Msg>(raw[0]);
  uint32_t netv;
  std::memcpy(&netv, raw + 1, sizeof(netv));
  var_ = ntohl(netv);
}

void Message::serialize(uint8_t out[kSize]) const {
  out[0] = static_cast<uint8_t>(type_);
  uint32_t netv = htonl(var_);
  std::memcpy(out + 1, &netv, sizeof(netv));
}

bool Message::send(int fd, Msg t, uint32_t v) {
  uint8_t buf[kSize];
  Message m(t, v);
  m.serialize(buf);
  return send_all(fd, buf, kSize);
}

bool Message::recv(int fd, Msg &t, uint32_t &v) {
  uint8_t buf[kSize];
  if (!recv_exact(fd, buf, kSize)) return false;
  Message m(buf);
  t = m.type();
  v = m.var();
  return true;
}
