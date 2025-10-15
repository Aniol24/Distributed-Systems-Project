#include <iostream>
#include <string>
#include <csignal>
#include "Master/Master.h"
#include "Client/Wrclient.h"

void ignore_sigpipe() { signal(SIGPIPE, SIG_IGN); }

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage:\n"
                  << "  " << argv[0] << " server <port>\n"
                  << "  " << argv[0] << " client <ip> <port> <r|rw>\n";
        return 1;
    }

    std::string mode = argv[1];

    // -----------------------------------------------------------
    // MODE SERVIDOR MASTER
    // -----------------------------------------------------------
    if (mode == "server") {
        if (argc < 3) {
            std::cerr << "Usage: " << argv[0] << " server <port>\n";
            return 1;
        }
        uint16_t port = static_cast<uint16_t>(std::stoi(argv[2]));

        Master server;
        std::cout << "[main] Starting Master on port " << port << "...\n";
        if (!server.Server_start(port)) {
            std::cerr << "[main] Server failed to start.\n";
            return 1;
        }
        return 0;
    }

    // -----------------------------------------------------------
    // MODO SERVIDOR CLIENT
    // -----------------------------------------------------------
    else if (mode == "client") {
        if (argc < 4) {
            std::cerr << "Usage: " << argv[0]
                      << " client <port> <r|rw>\n";
            return 1;
        }
        uint16_t port = static_cast<uint16_t>(std::stoi(argv[2]));
        std::string rwmode = argv[3];
        bool read_only = (rwmode == "r");

        ignore_sigpipe();

        WRClient client(port);
        if (!client.connect_server()) {
            std::cerr << "[main] Could not connect to port " << port << "\n";
            return 1;
        }

        std::cout << "[main] Connected to server. Running 10 iterations (" 
                  << (read_only ? "read-only" : "read-write") << ")...\n";

        bool ok = client.run(50, read_only);
        client.close_server();

        std::cout << "[main] Client finished: " << (ok ? "OK" : "FAIL") << "\n";
        return ok ? 0 : 2;
    }

    // -----------------------------------------------------------
    // ERROR: MODE DESCONEGUT
    // -----------------------------------------------------------
    else {
        std::cerr << "Unknown mode: " << mode << "\n";
        return 1;
    }
}
