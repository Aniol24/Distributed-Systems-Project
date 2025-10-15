#include <cstring>
#include <iostream>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>


class WRClient {
public:

    WRClient(int port);
    ~WRClient();

    bool connect_server();
    void close_server();
    bool lock();

    bool run(int iterations, bool read_only);

private:
    int port;
    int sock = -1;

    
    bool unlock();
    bool read(uint32_t &out);
    bool update(uint32_t newValue);
};