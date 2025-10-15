#include "Master.h"
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <cerrno>
#include <cstring>
#include <iostream>

Master::Master() {}
Master::~Master() { if (listen_fd >= 0) close(listen_fd); }

void Master::stop() { running = false; }

bool Master::Server_start(uint16_t port) {
    listen_fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) { perror("socket"); return false; }

    int yes = 1;
    ::setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    if (::bind(listen_fd, (sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind"); return false;
    }
    if (::listen(listen_fd, 10) < 0) {
        perror("listen"); return false;
    }

    std::cout << "[master] Listening on 127.0.0.1:" << port << "\n";

    fd_set master_set, read_set;
    FD_ZERO(&master_set);
    FD_SET(listen_fd, &master_set);
    int fdmax = listen_fd;

    while (running) {
        read_set = master_set;
        int ready = select(fdmax + 1, &read_set, nullptr, nullptr, nullptr);
        if (ready < 0) { if (errno == EINTR) continue; perror("select"); break; }

        for (int fd = 0; fd <= fdmax; ++fd) {
            if (!FD_ISSET(fd, &read_set)) continue;

            if (fd == listen_fd) {
                sockaddr_in caddr{}; socklen_t clen = sizeof(caddr);
                int new_fd = accept(listen_fd, (sockaddr*)&caddr, &clen);
                if (new_fd < 0) { perror("accept"); continue; }
                FD_SET(new_fd, &master_set);
                if (new_fd > fdmax) fdmax = new_fd;
                std::cout << "[master] Client connected fd=" << new_fd << "\n";
            } else {
                Msg t; uint32_t v;
                if (!Message::recv(fd, t, v)) {
                    std::cout << "[master] Client fd=" << fd << " disconnected\n";
                    if (lock_held && fd == lock_holder_fd) {
                        lock_held = false;
                        lock_holder_fd = -1;
                        if (!lock_queue.empty()) {
                            int next = lock_queue.front(); lock_queue.pop();
                            lock_held = true; lock_holder_fd = next;
                            Message::send(next, Msg::LOCK_OK);
                        }
                    }
                    close(fd);
                    FD_CLR(fd, &master_set);
                    continue;
                }
                handle_message(fd, t, v);
            }
        }
    }

    for (int fd = 0; fd <= fdmax; ++fd)
        if (FD_ISSET(fd, &master_set)) close(fd);

    return true;
}

void Master::handle_message(int fd, Msg t, uint32_t v) {
    switch (t) {
        case Msg::READ_REQ:
            Message::send(fd, Msg::READ_RESP, shared_value);
            std::cout << "[master] fd=" << fd << " READ -> " << shared_value << "\n";
            break;

        case Msg::UPDATE_REQ:
            if (lock_held && fd == lock_holder_fd) {
                shared_value = v;
                Message::send(fd, Msg::UPDATE_OK);
                std::cout << "[master] fd=" << fd << " UPDATE -> " << v << "\n";
            } else {
                Message::send(fd, Msg::ERR, (uint32_t)Err::E_NOT_HOLDER);
            }
            break;

        case Msg::LOCK_REQ:
            if (!lock_held) {
                lock_held = true;
                lock_holder_fd = fd;
                Message::send(fd, Msg::LOCK_OK);
                std::cout << "[master] fd=" << fd << " got LOCK\n";
            } else {
                std::cout << "[master] fd=" << fd << " queued for LOCK\n";
                lock_queue.push(fd);
            }
            break;

        case Msg::LOCK_REL:
            if (lock_held && fd == lock_holder_fd) {
                lock_held = false; lock_holder_fd = -1;
                if (!lock_queue.empty()) {
                    int next = lock_queue.front(); lock_queue.pop();
                    lock_held = true; lock_holder_fd = next;
                    Message::send(next, Msg::LOCK_OK);
                    std::cout << "[master] LOCK granted to fd=" << next << "\n";
                }
            }
            break;

        default:
            Message::send(fd, Msg::ERR, (uint32_t)Err::E_PROTO);
            break;
    }
}

