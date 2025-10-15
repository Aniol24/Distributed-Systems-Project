#pragma once
#include <cstdint>
#include <queue>
#include "../Message/Message.h"

class Master {
public:
    Master();
    ~Master();

    bool Server_start(uint16_t port);
    void stop();

private:
    bool process_request(int client_fd);
    void handle_message(int client_fd, Msg t, uint32_t v);

    int listen_fd = -1;
    bool running = true;

    uint32_t shared_value = 0;

    bool lock_held = false;
    int lock_holder_fd = -1;
    std::queue<int> lock_queue;  // cua d’espera per a lock
};


