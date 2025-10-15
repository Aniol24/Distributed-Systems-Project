/*
    WRClient class implementation in c++ by Aniol Verges
*/

#include "Wrclient.h"
#include "Message.h"


WRClient::WRClient(int port): port(port) {}   


WRClient::~WRClient() { close_server(); }

bool WRClient::connect_server(){
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(port);
    serverAddress.sin_addr.s_addr = inet_addr("127.0.0.1");

    if (connect(sock, (struct sockaddr *)&serverAddress, sizeof(serverAddress)) < 0) {
        perror("connect");
        close(sock);
        exit(EXIT_FAILURE);
    }

    std::cout << "[client] Conectado a 127.0.0.1 :" << port << "\n";
    return true;
}

void WRClient::close_server() {
    if (sock >= 0) {
    ::close(sock);
    sock = -1;
    std::cout << "[client] Conexión cerrada\n";
    }
}

bool WRClient::lock() {
    if (!Message::send(sock, Msg::LOCK_REQ)) return false;
    Msg t; uint32_t v;
    if (!Message::recv(sock, t, v)) return false;
    if (t == Msg::LOCK_OK) return true;
    if (t == Msg::ERR) std::cerr << "[client] ERR al LOCK, code=" << v << "\n";
    return false;
}

bool WRClient::unlock() {
    return Message::send(sock, Msg::LOCK_REL);
}

bool WRClient::read(uint32_t &out) {
    if (!Message::send(sock, Msg::READ_REQ)) return false;
    Msg t; uint32_t v;
    if (!Message::recv(sock, t, v)) return false;
    if (t != Msg::READ_RESP) {
    if (t == Msg::ERR) std::cerr << "[client] ERR al READ, code=" << v << "\n";
    return false;
    }
    out = v;
    return true;
}

bool WRClient::update(uint32_t newValue) {
    if (!Message::send(sock, Msg::UPDATE_REQ, newValue)) return false;
    Msg t; uint32_t v;
    if (!Message::recv(sock, t, v)) return false;
    if (t == Msg::UPDATE_OK) return true;
    if (t == Msg::ERR) std::cerr << "[client] ERR al UPDATE, code=" << v << "\n";
    return false;
}

bool WRClient::run(int iterations, bool read_only) {
    for (int i = 0; i < iterations; ++i) {
        if (!read_only) {
            std::cout << "[client] (" << (i+1) << ") pidiendo LOCK...\n";
            if (!lock()) {
                std::cerr << "[client] no se pudo obtener LOCK\n";
                return false;
            }
        }

        uint32_t val = 0;
        if (!read(val)) {
            std::cerr << "[client] error leyendo valor\n";
            return false;
        }
        std::cout << "[client] (" << (i+1) << ") READ = " << val << "\n";

        if (!read_only) {
            uint32_t next = val + 1;
            if (!update(next)) {
            std::cerr << "[client] error actualizando a " << next << "\n";
            return false;
            }
            std::cout << "[client] (" << (i+1) << ") UPDATE -> " << next << "\n";
            unlock();
        }

        ::sleep(1); 
    }
    return true;
}

int main(){
    WRClient client(12345);
    client.connect_server();
    client.run(5, false);
    client.close_server();
    return 0;
}
