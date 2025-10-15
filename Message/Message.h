#pragma once
#include <cstdint>
#include <cstddef>

enum class Msg : uint8_t {

  READ_REQ     = 0x10,  // Demanem llegir
  READ_RESP    = 0x11,  // Servidor respon amb el valor actual

  UPDATE_REQ   = 0x12,  // Quan tenim acces a l'objecte, demanem update (el valor nou va a var)
  UPDATE_OK    = 0x13,  // update ok

  LOCK_REQ     = 0x20,  // Demanem lock de la variable
  LOCK_OK      = 0x21,  // El server ens ho dona
  LOCK_DENY    = 0x22,  // El server no ens ho dona
  LOCK_REL     = 0x23,  // Alliberem el lock

  ERR          = 0x7F   // (srv→cli) var = codi d'error
};

enum class Err : uint32_t {
  E_PROTO       = 1,   // Missatge desconegut
  E_NOT_HOLDER  = 2,   // Operació reservada al holder del lock
  E_CLOSED      = 3,   // Tancament del servidor/cliente
};

class Message {
public:
  static constexpr std::size_t kSize = 1 + 4; // type (1) + var (4)

  Message() = default;
  Message(Msg t, uint32_t v = 0) : type_(t), var_(v) {}
  explicit Message(const uint8_t raw[kSize]);

  void serialize(uint8_t out[kSize]) const;

  static bool send(int fd, Msg t, uint32_t v = 0);
  static bool recv(int fd, Msg &t, uint32_t &v);

  Msg       type() const { return type_; }
  uint32_t  var()  const { return var_;  }

private:
  Msg       type_{Msg::READ_REQ}; 
  uint32_t  var_{0};
};