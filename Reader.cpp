#include <iostream>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

using namespace std;

#define RED "\033[0;31m"

class Reader {
    private:
    string ip;
    string port;
    int socket_fd;

    bool connect_to_server() {
        struct sockaddr_in server_addr;
            socket_fd = socket(AF_INET, SOCK_STREAM, 0);
            if (socket_fd < 0) {
                cerr << RED << "Error creating socket\n" << endl;
                return false;
            }

            memset(&server_addr, 0, sizeof(server_addr));
            server_addr.sin_family = AF_INET;
            server_addr.sin_port = htons(stoi(port));
            if (inet_pton(AF_INET, ip.c_str(), &server_addr.sin_addr) <= 0) {
                cerr << RED << "Invalid IP address\n" << endl;
                close(socket_fd);
                return false;
            }

            if (connect(socket_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
                cerr << RED << "Connection failed\n" << endl;
                close(socket_fd);
                return false;
            }

            return true;
    }

    bool disconnect_from_server() {
        if (close(socket_fd) < 0) {
            cerr << RED << "Error closing socket\n" << endl;
            return false;
        }
        return true;
    }

    public:

        Reader(string ip, string port) : ip(ip), port(port) {}

        ~Reader() {}

        bool run() {
            if (!this->connect_to_server()) return false;
            cout << "Connected to " << ip << ":" << port << endl;

            
            if (!this->disconnect_from_server()) return false;
            cout << "Disconnected from server" << endl;
            return true;

        }

};

int main(int argc, char *argv[]) {
    if (argc != 3) {
        cerr << RED << "Ús: " << argv[0] << " <IP> <Port>\n" << endl;
        return 1;
    }

    Reader reader = Reader(argv[1], argv[2]);
    reader.run();
    return 0;
}